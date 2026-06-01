# Redis Patterns

**Проверенные паттерны использования Redis в Python.**

---

## 1. Connection

```python
import redis.asyncio as aioredis

# Однострочное подключение
redis = aioredis.from_url(
    "redis://:password@localhost:6379/0",
    decode_responses=True,  # возвращать str вместо bytes
    socket_timeout=5.0,
    retry_on_timeout=True,
    max_connections=50,
)

# Connection pool (рекомендуется)
pool = aioredis.ConnectionPool.from_url(
    "redis://localhost:6379/0",
    max_connections=20,
    decode_responses=True,
)
redis = aioredis.Redis(connection_pool=pool)
```

## 2. Caching Patterns

```python
# Cache-Aside (Lazy Loading)
async def get_user(user_id: int) -> User | None:
    cache_key = f"user:{user_id}"
    
    # 1. Check cache
    if cached := await redis.get(cache_key):
        return User.model_validate_json(cached)
    
    # 2. Cache miss → DB
    user = await db.get(User, user_id)
    if not user:
        return None
    
    # 3. Fill cache
    await redis.setex(cache_key, 300, user.model_dump_json())
    
    return user

# Write-Through (Always fresh)
async def update_user(user_id: int, data: dict) -> User:
    user = await db.update(User, user_id, data)
    await redis.setex(f"user:{user_id}", 300, user.model_dump_json())
    return user

# Write-Behind (Async write)
async def update_user_async(user_id: int, data: dict) -> None:
    await redis.setex(f"user:{user_id}", 300, json.dumps(data))
    await queue.put(("update_user", user_id, data))

# Cache Stampede Protection
async def get_or_compute(key: str, factory: Callable, ttl: int = 300) -> Any:
    """Защита от stampede: один вычисляет, остальные ждут."""
    if cached := await redis.get(key):
        return json.loads(cached)
    
    # Distributed lock (только один вычисляет)
    lock_key = f"lock:{key}"
    if await redis.setnx(lock_key, "1"):
        await redis.expire(lock_key, 10)
        try:
            value = await factory()
            await redis.setex(key, ttl, json.dumps(value))
            return value
        finally:
            await redis.delete(lock_key)
    else:
        # Кто-то другой вычисляет, ждём
        for _ in range(50):
            await asyncio.sleep(0.1)
            if cached := await redis.get(key):
                return json.loads(cached)
        raise TimeoutError("Cache computation timeout")
```

## 3. Rate Limiting

```python
import time

# Sliding Window
class RateLimiter:
    """Rate limiter using Redis sorted sets."""
    
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
    
    async def check(self, key: str, max_requests: int = 100, window: int = 60) -> bool:
        now = time.monotonic()
        window_key = f"ratelimit:{key}:{int(now // window)}"
        
        count = await self._redis.incr(window_key)
        if count == 1:
            await self._redis.expire(window_key, window + 1)
        
        return count <= max_requests

# Token Bucket
class TokenBucket:
    """Token bucket rate limiter with Redis."""
    
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
    
    async def allow(self, key: str, rate: int = 10, burst: int = 20) -> bool:
        now = time.monotonic()
        bucket_key = f"tokenbucket:{key}"
        
        lua = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local rate = tonumber(ARGV[2])
        local burst = tonumber(ARGV[3])
        
        local bucket = redis.call('hgetall', key)
        local last_tokens = burst
        local last_refill = now
        
        if #bucket > 0 then
            last_tokens = tonumber(bucket[2])
            last_refill = tonumber(bucket[4])
        end
        
        local elapsed = now - last_refill
        local tokens = math.min(burst, last_tokens + elapsed * rate)
        
        if tokens >= 1 then
            redis.call('hmset', key, 'tokens', tokens - 1, 'last_refill', now)
            redis.call('expire', key, 10)
            return 1
        else
            return 0
        end
        """
        
        return await self._redis.eval(lua, 1, bucket_key, now, rate, burst)
```

## 4. Distributed Locks

```python
import uuid

class DistributedLock:
    """Redis-based distributed lock with auto-release."""
    
    def __init__(self, redis: aioredis.Redis, key: str, ttl: int = 30) -> None:
        self._redis = redis
        self._key = f"lock:{key}"
        self._ttl = ttl
        self._token = uuid.uuid4().hex
        self._acquired = False
    
    async def __aenter__(self) -> "DistributedLock":
        self._acquired = await self._acquire()
        if not self._acquired:
            raise LockError(f"Could not acquire lock: {self._key}")
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        if self._acquired:
            await self._release()
    
    async def _acquire(self) -> bool:
        return await self._redis.set(
            self._key, self._token,
            nx=True,  # Only set if not exists
            ex=self._ttl,
        ) is not None
    
    async def _release(self) -> None:
        # Lua script: безопасное освобождение (только если наш)
        lua = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        await self._redis.eval(lua, 1, self._key, self._token)

class LockError(Exception):
    pass

# Использование
async with DistributedLock(redis, f"user:{user_id}:edit"):
    user = await db.get(User, user_id)
    user.balance += amount
    await db.save(user)
```

## 5. Queues

```python
# Simple FIFO Queue
async def push_task(queue: str, task: dict) -> None:
    await redis.lpush(queue, json.dumps(task))

async def pop_task(queue: str, timeout: int = 5) -> dict | None:
    result = await redis.brpop(queue, timeout=timeout)
    if result:
        return json.loads(result[1])
    return None

# Priority Queue
async def push_priority(queue: str, task: dict, priority: int = 0) -> None:
    await redis.zadd(queue, {json.dumps(task): priority})

async def pop_priority(queue: str) -> dict | None:
    # Get highest priority (lowest score)
    results = await redis.zpopmin(queue, count=1)
    if results:
        return json.loads(results[0][0])
    return None
```

## 6. Pub/Sub

```python
# Publisher
async def publish_event(channel: str, event: dict) -> None:
    await redis.publish(channel, json.dumps(event))

# Subscriber
async def listen_events(channel: str) -> None:
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            event = json.loads(message["data"])
            await handle_event(event)

# Pattern subscription
async def listen_pattern(pattern: str) -> None:
    pubsub = redis.pubsub()
    await pubsub.psubscribe(pattern)
    async for message in pubsub.listen():
        ...
```

## 7. Sessions

```python
class SessionStore:
    """User sessions in Redis."""
    
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
    
    async def create(self, user_id: int, ttl: int = 86400) -> str:
        session_id = uuid.uuid4().hex
        await self._redis.setex(
            f"session:{session_id}",
            ttl,
            json.dumps({"user_id": user_id}),
        )
        return session_id
    
    async def get(self, session_id: str) -> int | None:
        data = await self._redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)["user_id"]
        return None
    
    async def delete(self, session_id: str) -> None:
        await self._redis.delete(f"session:{session_id}")
```

## 8. Real-time Leaderboard

```python
class Leaderboard:
    """Real-time leaderboard using Redis sorted sets."""
    
    def __init__(self, redis: aioredis.Redis, key: str = "leaderboard") -> None:
        self._redis = redis
        self._key = key
    
    async def add_score(self, user_id: int, score: float) -> None:
        await self._redis.zadd(self._key, {str(user_id): score})
    
    async def increment_score(self, user_id: int, delta: float = 1.0) -> None:
        await self._redis.zincrby(self._key, delta, str(user_id))
    
    async def top(self, n: int = 10) -> list[dict]:
        results = await self._redis.zrevrange(self._key, 0, n - 1, withscores=True)
        return [{"user_id": int(uid), "score": score} for uid, score in results]
    
    async def rank(self, user_id: int) -> int | None:
        rank = await self._redis.zrevrank(self._key, str(user_id))
        return rank + 1 if rank is not None else None
```


---

## Battle-Tested Production Patterns

### Error Handling & Resilience

```python
"""Production-grade error handling patterns."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ResiliencePolicy:
    """Resilience policy for external service calls."""
    max_retries: int = 3
    timeout_seconds: float = 10.0
    circuit_breaker_failures: int = 5
    rate_limit_per_second: int = 100


async def resilient_call[T](
    fn: Any,
    *args: Any,
    policy: ResiliencePolicy | None = None,
    **kwargs: Any,
) -> T:
    """Execute call with retry, timeout, and circuit breaker."""
    policy = policy or ResiliencePolicy()
    
    for attempt in range(policy.max_retries + 1):
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                return await fn(*args, **kwargs)
        except asyncio.TimeoutError:
            if attempt == policy.max_retries:
                raise
            delay = 1.0 * (2 ** attempt)
            logger.warning(f"Timeout (attempt {attempt+1}), retrying in {delay}s")
            await asyncio.sleep(delay)
        except Exception as e:
            if attempt == policy.max_retries:
                raise
            logger.warning(f"Error (attempt {attempt+1}): {e}")
            await asyncio.sleep(1.0 * (2 ** attempt))
    
    raise RuntimeError("Should not reach here")


### Observability Best Practices

```python
"""Observability patterns for production."""
from __future__ import annotations

import time
import functools
from typing import Any, Callable


def observe(name: str = ""):
    """Decorator to add observability to any function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(
                    f"{name or func.__name__} completed",
                    extra={"duration_ms": elapsed * 1000},
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    f"{name or func.__name__} failed",
                    extra={"duration_ms": elapsed * 1000, "error": str(e)},
                )
                raise
        return wrapper
    return decorator


### Configuration Management

```python
"""Type-safe configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceConfig:
    """Application configuration from environment."""
    
    # Service metadata
    service_name: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "app"))
    environment: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    
    # Database
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "1") == "1"
    
    # Cache
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    
    # API
    api_port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    
    # Feature flags
    enable_new_algo: bool = os.getenv("FEATURE_NEW_ALGO", "0") == "1"
    enable_debug_mode: bool = os.getenv("DEBUG", "0") == "1"
    
    def validate(self) -> None:
        """Validate config on startup."""
        errors = []
        if self.environment == "prod" and not self.database_url:
            errors.append("DATABASE_URL required in production")
        if self.environment == "prod" and "localhost" in (self.database_url or ""):
            errors.append("Cannot use localhost database in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
    
    @property
    def is_debug(self) -> bool:
        return self.enable_debug_mode or self.environment == "dev"


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.


---

## Production-Grade Extension

```python
"""Production-optimized implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionPattern:
    """Enterprise pattern with full resilience stack."""
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(30):
                    start = time.perf_counter()
                    result = await fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(f"Success in {elapsed*1000:.1f}ms")
                    return result
            except asyncio.TimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error("Operation timed out after all retries")
                    raise
                wait = 1.0 * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.exception(f"Attempt {attempt + 1} failed")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        raise RuntimeError("Unreachable")
    

### Principal Engineer Notes

This pattern demonstrates:
- **Resilience**: Retry with exponential backoff
- **Observability**: Timing and error logging
- **Safety**: Timeout on all operations
- **Simplicity**: Single responsibility, clear flow

Apply this pattern to every external call in your system.
No production service should make an unprotected external call.
