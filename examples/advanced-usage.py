#!/usr/bin/env python3
"""Advanced Usage — production patterns in action.

Включает:
  1. Structured logging with context
  2. Caching with TTL and tags
  3. State machine for order processing
  4. Connection pool pattern
  5. Circuit breaker for external calls
  6. Batch processing with retry
"""
from __future__ import annotations

import asyncio
import enum
import json
import logging
import random
import time
import uuid
from collections.abc import AsyncIterator, Callable, Awaitable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypeVar

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# 1. Structured Logging
# ═══════════════════════════════════════════════

class StructuredLogger:
    """JSON-structured logger with async context support."""
    
    def __init__(self, name: str) -> None:
        self._log = logging.getLogger(name)
    
    def _log(self, level: int, msg: str, **extra: Any) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(level).lower(),
            "logger": self._log.name,
            "msg": msg,
            **extra,
        }
        self._log.log(level, json.dumps(record, default=str))
    
    def info(self, msg: str, **kw: Any) -> None:
        self._log(logging.INFO, msg, **kw)
    
    def error(self, msg: str, exc: Exception | None = None, **kw: Any) -> None:
        if exc:
            kw["error"] = str(exc)
            kw["traceback"] = getattr(exc, "__traceback__", None)
        self._log(logging.ERROR, msg, **kw)
    
    def warning(self, msg: str, **kw: Any) -> None:
        self._log(logging.WARNING, msg, **kw)

log = StructuredLogger("advanced")


# ═══════════════════════════════════════════════
# 2. Caching with TTL
# ═══════════════════════════════════════════════

@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    tags: set[str] = field(default_factory=set)

class TaggedCache:
    """Кэш с TTL и инвалидацией по тегам."""
    
    def __init__(self, default_ttl: float = 300.0) -> None:
        self._default_ttl = default_ttl
        self._data: dict[str, CacheEntry] = {}
        self._tag_index: dict[str, set[str]] = {}
    
    def get(self, key: str) -> Any | None:
        if entry := self._data.get(key):
            if entry.expires_at > time.monotonic():
                return entry.value
            del self._data[key]
        return None
    
    def set(self, key: str, value: Any, ttl: float | None = None, tags: list[str] | None = None) -> None:
        entry_tags = set(tags or [])
        self._data[key] = CacheEntry(
            value=value,
            expires_at=time.monotonic() + (ttl or self._default_ttl),
            tags=entry_tags,
        )
        for tag in entry_tags:
            self._tag_index.setdefault(tag, set()).add(key)
    
    def invalidate(self, tag: str) -> None:
        if keys := self._tag_index.pop(tag, None):
            for key in keys:
                self._data.pop(key, None)
    
    def clear(self) -> None:
        self._data.clear()
        self._tag_index.clear()


# ═══════════════════════════════════════════════
# 3. State Machine
# ═══════════════════════════════════════════════

class OrderState(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.PENDING:     {OrderState.CONFIRMED, OrderState.CANCELLED},
    OrderState.CONFIRMED:   {OrderState.PROCESSING, OrderState.CANCELLED},
    OrderState.PROCESSING:  {OrderState.SHIPPED, OrderState.CANCELLED},
    OrderState.SHIPPED:     {OrderState.DELIVERED},
    OrderState.DELIVERED:   {OrderState.REFUNDED},
    OrderState.CANCELLED:   {OrderState.REFUNDED},
    OrderState.REFUNDED:    set(),
}

class StateMachine:
    """Finate State Machine with transition guards."""
    
    def __init__(self, initial: OrderState = OrderState.PENDING) -> None:
        self._state = initial
        self._history: list[tuple[OrderState, OrderState, str]] = []
    
    @property
    def state(self) -> OrderState:
        return self._state
    
    def can_transition(self, target: OrderState) -> bool:
        return target in TRANSITIONS.get(self._state, set())
    
    def transition(self, target: OrderState, reason: str = "") -> None:
        if not self.can_transition(target):
            raise ValueError(
                f"Invalid transition: {self._state.value} → {target.value}"
            )
        self._history.append((self._state, target, reason))
        log.info("state_change", from_state=self._state.value, to_state=target.value, reason=reason)
        self._state = target
    
    def history(self) -> list[dict[str, str]]:
        return [
            {"from": f.value, "to": t.value, "reason": r, "at": datetime.now(timezone.utc).isoformat()}
            for f, t, r in self._history
        ]


# ═══════════════════════════════════════════════
# 4. Connection Pool
# ═══════════════════════════════════════════════

T = TypeVar("T")

@dataclass
class Pool(AsyncIterator[T]):
    """Generic async connection pool."""
    factory: Callable[[], Awaitable[T]]
    min_size: int = 2
    max_size: int = 10
    
    _sem: asyncio.Semaphore = field(init=False, repr=False)
    _idle: list[T] = field(default_factory=list, init=False, repr=False)
    _used: set[T] = field(default_factory=set, init=False, repr=False)
    _closed: bool = False
    
    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.max_size)
    
    async def __aenter__(self) -> Pool[T]:
        for _ in range(self.min_size):
            conn = await self.factory()
            self._idle.append(conn)
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        self._closed = True
        for conn in [*self._idle, *self._used]:
            if hasattr(conn, "close"):
                await conn.close()
        self._idle.clear()
        self._used.clear()
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[T]:
        async with self._sem:
            conn = await self._get()
            try:
                yield conn
            except Exception:
                await self._close_conn(conn)
                self._used.discard(conn)
                raise
    
    async def _get(self) -> T:
        if self._idle:
            return self._idle.pop()
        conn = await self.factory()
        self._used.add(conn)
        return conn
    
    async def _close_conn(self, conn: T) -> None:
        if hasattr(conn, "close"):
            await conn.close()
    
    async def __anext__(self) -> T:
        raise StopAsyncIteration


# ═══════════════════════════════════════════════
# 5. Circuit Breaker
# ═══════════════════════════════════════════════

class CircuitState(enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker with auto-recovery."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure = 0.0
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        if self._state is CircuitState.OPEN:
            if time.monotonic() - self._last_failure > self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                log.info("circuit_half_open")
            else:
                raise CircuitBreakerError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self._failure_threshold:
                self._state = CircuitState.OPEN
                log.warning("circuit_opened", failures=self._failures)
            raise
        
        if self._state is CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failures = 0
            log.info("circuit_closed")
        
        return result

class CircuitBreakerError(Exception):
    pass


# ═══════════════════════════════════════════════
# 6. Batch Processor with Retry
# ═══════════════════════════════════════════════

@dataclass
class BatchResult:
    processed: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

class BatchProcessor:
    """Batch processing with retry and error handling."""
    
    def __init__(self, batch_size: int = 100, max_retries: int = 3) -> None:
        self._batch_size = batch_size
        self._max_retries = max_retries
    
    async def process(self, items: list[Any], handler: Callable[[list[Any]], Awaitable[None]]) -> BatchResult:
        """Process items in batches with retry."""
        result = BatchResult()
        
        for i in range(0, len(items), self._batch_size):
            batch = items[i:i + self._batch_size]
            
            for attempt in range(self._max_retries):
                try:
                    await handler(batch)
                    result.processed += len(batch)
                    break
                except Exception as e:
                    if attempt == self._max_retries - 1:
                        result.failed += len(batch)
                        result.errors.append(f"Batch {i//self._batch_size} failed after {self._max_retries} attempts: {e}")
                        log.error("batch_failed", batch_idx=i // self._batch_size, error=str(e))
                    else:
                        delay = 2 ** attempt
                        log.warning("batch_retry", batch_idx=i // self._batch_size, attempt=attempt + 1, delay=delay)
                        await asyncio.sleep(delay)
        
        return result


# ═══════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════

async def demo() -> None:
    print("Advanced Usage Demo\n")
    
    # 1. Cache
    cache = TaggedCache(default_ttl=60)
    cache.set("user:1", {"name": "Alice"}, tags=["users", "premium"])
    cache.set("user:2", {"name": "Bob"}, tags=["users"])
    
    print(f"1. Cache: {cache.get('user:1')}")
    cache.invalidate("premium")
    print(f"   After invalidation: {cache.get('user:1')}")
    
    # 2. State machine
    sm = StateMachine(OrderState.PENDING)
    sm.transition(OrderState.CONFIRMED)
    sm.transition(OrderState.PROCESSING)
    print(f"\n2. State machine: {sm.state.value}")
    print(f"   Can cancel: {sm.can_transition(OrderState.CANCELLED)}")
    
    # 3. Batch processing
    processor = BatchProcessor(batch_size=3, max_retries=2)
    
    async def handler(batch: list[int]) -> None:
        await asyncio.sleep(0.1)
        if random.random() < 0.3:
            raise ConnectionError("Simulated error")
    
    items = list(range(10))
    result = await processor.process(items, handler)
    print(f"\n3. Batch: processed={result.processed}, failed={result.failed}")
    
    # 4. Circuit breaker
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=2)
    call_count = 0
    
    async def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 4:
            raise ConnectionError("Timeout")
        return "Success"
    
    print("\n4. Circuit breaker:")
    for i in range(6):
        try:
            result = await cb.call(flaky)
            print(f"   Call {i+1}: ✅ {result}")
        except CircuitBreakerError:
            print(f"   Call {i+1}: ❌ Circuit open (skipped)")
        except Exception as e:
            print(f"   Call {i+1}: ❌ {e}")
    
    print("\nDone! 🎉")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(demo())


# ── Extended Production Example ─────────────────────────────────────

"""Extended with error handling, retry, logging, and monitoring.
This is what production-grade code looks like in Big Tech.
"""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
import functools

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        wait = delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} after {wait:.1f}s")
                        await asyncio.sleep(wait)
            raise last_error
        return wrapper
    return decorator


def timed(func):
    """Log execution time."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed*1000:.1f}ms")
    return wrapper


@dataclass
class ProductionService:
    """Production-grade service with full observability."""
    
    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
        }
    
    @retry(max_attempts=3)
    @timed
    async def process_with_resilience(self, data: dict) -> dict:
        """Process data with retry and timing."""
        async with asyncio.timeout(30):
            result = await self._process(data)
            logger.info("Processed", extra={"data_size": len(data)})
            return result
    
    async def _process(self, data: dict) -> dict:
        """Core processing logic."""
        return {"status": "ok", "data": data}


# Использование:
# service = ProductionService()
# result = await service.process_with_resilience({"key": "value"})
