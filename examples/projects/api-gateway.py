#!/usr/bin/env python3
"""API Gateway: асинхронный прокси-сервер с маршрутизацией, кэшированием и rate limiting.

Архитектура:
  Client → Gateway → Router → Cache (Redis) → Backend
                     ↓
              Rate Limiter
                     ↓
              Circuit Breaker
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import aiohttp
from aiohttp import web

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("gateway")


# ── Types ──────────────────────────────────────
@dataclass
class Route:
    """Маршрут до бэкенда."""
    prefix: str
    target: str
    methods: set[str] | None = None  # None = все методы
    timeout: float = 30.0
    rate_limit: int = 100  # запросов в минуту
    cache_ttl: int = 0     # 0 = не кэшировать


@dataclass
class BackendResponse:
    """Ответ от бэкенда."""
    status: int
    headers: dict[str, str]
    body: Any
    cached: bool = False
    backend_time: float = 0.0


# ── Rate Limiter ───────────────────────────────
class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int, per: float = 60.0) -> None:
        self._rate = rate
        self._per = per
        self._tokens = float(rate)
        self._last_refill = time.monotonic()
    
    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self._last_refill
        
        # Refill
        self._tokens += elapsed * (self._rate / self._per)
        self._tokens = min(self._tokens, self._rate)
        self._last_refill = now
        
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False


class RateLimiter:
    """Rate limiter с поддержкой per-route и per-IP."""
    
    def __init__(self) -> None:
        self._buckets: dict[str, TokenBucket] = {}
    
    def check(self, key: str, rate: int) -> bool:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(rate)
        return self._buckets[key].allow()


# ── Circuit Breaker ────────────────────────────
class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


@dataclass
class CircuitBreaker:
    """Circuit breaker для защиты бэкендов."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    
    _state: CircuitState = CircuitState.CLOSED
    _failures: int = 0
    _last_failure: float = 0.0
    
    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Выполнить с защитой circuit breaker."""
        if self._state is CircuitState.OPEN:
            if time.monotonic() - self._last_failure > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker open for {func.__name__}")
        
        try:
            result = asyncio.run(func(*args, **kwargs)) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN after %d failures", self._failures)
            raise
        
        if self._state is CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failures = 0
            logger.info("Circuit breaker CLOSED (recovered)")
        
        return result


class CircuitBreakerOpenError(Exception):
    pass


# ── Cache Layer ────────────────────────────────
class CacheLayer:
    """Кэш с TTL и инвалидацией по тегам."""
    
    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, Any]] = {}
        self._tags: dict[str, set[str]] = {}
    
    async def get(self, key: str) -> Any | None:
        if key in self._cache:
            expires, value = self._cache[key]
            if time.monotonic() < expires:
                return value
            del self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: float = 60.0, tags: list[str] | None = None) -> None:
        self._cache[key] = (time.monotonic() + ttl, value)
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(key)
    
    async def invalidate(self, tag: str) -> None:
        if keys := self._tags.pop(tag, None):
            for key in keys:
                self._cache.pop(key, None)
    
    async def clear(self) -> None:
        self._cache.clear()
        self._tags.clear()


# ── Gateway ────────────────────────────────────
@dataclass
class Gateway:
    """API Gateway."""
    routes: list[Route] = field(default_factory=list)
    rate_limiter: RateLimiter = field(default_factory=RateLimiter)
    cache: CacheLayer = field(default_factory=CacheLayer)
    circuit_breakers: dict[str, CircuitBreaker] = field(default_factory=dict)
    
    _client: aiohttp.ClientSession | None = None
    _stats: dict[str, int] = field(default_factory=lambda: {
        "requests": 0, "cached": 0, "errors": 0, "rate_limited": 0,
    })
    
    async def start(self) -> None:
        self._client = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100),
        )
        logger.info("Gateway started")
    
    async def stop(self) -> None:
        if self._client:
            await self._client.close()
        logger.info("Gateway stopped. Stats: %s", self._stats)
    
    def add_route(self, route: Route) -> None:
        self.routes.append(route)
        self.circuit_breakers[route.prefix] = CircuitBreaker()
    
    def _match_route(self, path: str, method: str) -> Route | None:
        for route in self.routes:
            if path.startswith(route.prefix):
                if route.methods is None or method in route.methods:
                    return route
        return None
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """Обработать входящий запрос."""
        self._stats["requests"] += 1
        path = request.path
        method = request.method
        client_ip = request.remote or "unknown"
        
        # 1. Route matching
        route = self._match_route(path, method)
        if not route:
            return web.json_response(
                {"error": "route_not_found", "path": path},
                status=404,
            )
        
        # 2. Rate limiting
        rate_key = f"{client_ip}:{route.prefix}"
        if not self.rate_limiter.check(rate_key, route.rate_limit):
            self._stats["rate_limited"] += 1
            return web.json_response(
                {"error": "rate_limit_exceeded", "retry_after": 60},
                status=429,
                headers={"Retry-After": "60"},
            )
        
        # 3. Cache check (for GET requests)
        if method == "GET" and route.cache_ttl > 0:
            cache_key = f"{method}:{path}"
            if cached := await self.cache.get(cache_key):
                self._stats["cached"] += 1
                return web.json_response(cached, headers={"X-Cache": "HIT"})
        
        # 4. Proxy to backend
        target_url = f"{route.target}{path}"
        
        try:
            cb = self.circuit_breakers.get(route.prefix)
            if cb:
                cb.call(lambda: None)  # Проверка circuit breaker
            
            start = time.monotonic()
            
            # Remove host header, forward the rest
            headers = {k: v for k, v in request.headers.items() 
                      if k.lower() not in ("host", "content-length")}
            
            body = await request.read()
            
            async with self._client.request(
                method, target_url,
                headers=headers,
                data=body or None,
                timeout=aiohttp.ClientTimeout(total=route.timeout),
            ) as resp:
                backend_time = time.monotonic() - start
                response_body = await resp.read()
                
                # Try to parse JSON for cache
                result: Any = response_body
                if resp.content_type == "application/json":
                    result = json.loads(response_body)
                
                backend_resp = BackendResponse(
                    status=resp.status,
                    headers=dict(resp.headers),
                    body=result,
                    cached=False,
                    backend_time=backend_time,
                )
                
                # Cache successful GET responses
                if method == "GET" and resp.status == 200 and route.cache_ttl > 0:
                    cache_key = f"{method}:{path}"
                    await self.cache.set(cache_key, result, route.cache_ttl)
                
                logger.info(
                    "%s %s → %s (%d) in %.2fms",
                    method, path, target_url, resp.status, backend_time * 1000,
                )
                
                return web.json_response(
                    backend_resp.body,
                    status=backend_resp.status,
                    headers={"X-Backend-Time": f"{backend_time*1000:.0f}ms"},
                )
        
        except asyncio.TimeoutError:
            self._stats["errors"] += 1
            logger.error("Timeout: %s → %s", path, target_url)
            return web.json_response({"error": "backend_timeout"}, status=504)
        
        except CircuitBreakerOpenError:
            self._stats["errors"] += 1
            logger.warning("Circuit breaker: %s", route.prefix)
            return web.json_response({"error": "service_unavailable"}, status=503)
        
        except aiohttp.ClientError as e:
            self._stats["errors"] += 1
            logger.error("Backend error: %s → %s: %s", path, target_url, e)
            return web.json_response({"error": "backend_error"}, status=502)
    
    async def health(self, request: web.Request) -> web.Response:
        """Health check."""
        return web.json_response({
            "status": "healthy",
            "stats": self._stats,
            "uptime": time.monotonic(),
        })
    
    async def stats_handler(self, request: web.Request) -> web.Response:
        """Статистика."""
        return web.json_response(self._stats)
    
    async def invalidate(self, request: web.Request) -> web.Response:
        """Инвалидация кэша по тегу."""
        tag = request.query.get("tag")
        if not tag:
            return web.json_response({"error": "tag_required"}, status=400)
        await self.cache.invalidate(tag)
        return web.json_response({"status": "invalidated", "tag": tag})


# ── Main ───────────────────────────────────────
async def main() -> None:
    gateway = Gateway()
    
    # Register routes
    gateway.add_route(Route(
        prefix="/api/users",
        target="http://user-service:8001",
        methods={"GET", "POST", "PUT", "DELETE"},
        rate_limit=200,
        cache_ttl=30,
    ))
    gateway.add_route(Route(
        prefix="/api/orders",
        target="http://order-service:8002",
        methods={"GET", "POST"},
        rate_limit=100,
        cache_ttl=60,
    ))
    gateway.add_route(Route(
        prefix="/api/payments",
        target="http://payment-service:8003",
        methods={"POST"},
        rate_limit=50,
        cache_ttl=0,  # не кэшируем
    ))
    
    await gateway.start()
    
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", gateway.handle_request)
    app.router.add_get("/health", gateway.health)
    app.router.add_get("/stats", gateway.stats_handler)
    app.router.add_post("/cache/invalidate", gateway.invalidate)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    
    logger.info("Gateway listening on :8080")
    
    await site.start()
    
    # Graceful shutdown
    stop = asyncio.Event()
    try:
        await stop.wait()
    except KeyboardInterrupt:
        pass
    finally:
        await gateway.stop()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


# ── Real-World Production Extensions ─────────────────────────────

"""Production-grade patterns for this example."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator with exponential backoff and jitter."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + (base_delay * 0.1 * hash(str(args)) % 1)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s: {e}")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Circuit breaker with half-open recovery."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _failures: int = 0
    _state: str = "closed"
    _last_failure: float = 0.0
    
    async def call(self, fn: Callable[..., Awaitable[Any]], fallback: Callable[..., Awaitable[Any]] | None = None, *args, **kwargs) -> Any:
        if self._state == "open":
            if time.monotonic() - self._last_failure >= self.recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit half-open, testing recovery")
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError("Circuit breaker is open")
        
        try:
            result = await fn(*args, **kwargs)
            self._failures = 0
            self._state = "closed"
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = "open"
                logger.error(f"Circuit opened after {self._failures} failures")
            raise


@dataclass
class GracefulShutdownManager:
    """Graceful shutdown with dependency ordering."""
    _hooks: list = None
    
    def __post_init__(self):
        self._hooks = []
        self._shutting_down = False
    
    def register(self, name: str, hook: Callable[[], Awaitable[None]], order: int = 10):
        self._hooks.append((order, name, hook))
    
    async def shutdown(self, sig: str = "SIGTERM"):
        self._shutting_down = True
        logger.info(f"Initiating graceful shutdown (signal: {sig})...")
        
        for order, name, hook in sorted(self._hooks, key=lambda x: -x[0]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                logger.info(f"  ✓ {name} stopped")
            except asyncio.TimeoutError:
                logger.warning(f"  ✗ {name} stop timed out")
            except Exception as e:
                logger.error(f"  ✗ {name} stop failed: {e}")
        
        logger.info("Graceful shutdown complete")
    
    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down
