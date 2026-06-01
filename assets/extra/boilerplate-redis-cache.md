# Redis Cache Boilerplate

## Cache-Aside Pattern

```python
"""Redis caching patterns for async Python."""
from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable, Awaitable
from typing import Any, TypeVar
import redis.asyncio as aioredis

T = TypeVar("T")

class CacheAside:
    """Cache-Aside (Lazy Loading) pattern."""
    
    def __init__(self, redis: aioredis.Redis, default_ttl: int = 300) -> None:
        self._redis = redis
        self._default_ttl = default_ttl
    
    async def get(self, key: str, fetch: Callable[[], Awaitable[T]], ttl: int | None = None) -> T:
        """Get from cache, fallback to fetch."""
        cached = await self._redis.get(key)
        if cached is not None:
            return json.loads(cached)
        
        value = await fetch()
        await self._redis.setex(key, ttl or self._default_ttl, json.dumps(value, default=str))
        return value
    
    async def invalidate(self, key: str) -> None:
        """Invalidate cache key."""
        await self._redis.delete(key)
    
    async def get_many(self, keys: list[str], fetch: Callable[[list[str]], Awaitable[dict[str, T]]], 
                       ttl: int | None = None) -> dict[str, T]:
        """Batch get with cache."""
        cached = await self._redis.mget(*keys)
        result: dict[str, T] = {}
        missing: list[str] = []
        
        for key, value in zip(keys, cached):
            if value is not None:
                result[key] = json.loads(value)
            else:
                missing.append(key)
        
        if missing:
            fetched = await fetch(missing)
            result.update(fetched)
            async with self._redis.pipeline() as pipe:
                for key, value in fetched.items():
                    pipe.setex(key, ttl or self._default_ttl, json.dumps(value, default=str))
                await pipe.execute()
        
        return result


class WriteThrough:
    """Write-Through: write to DB and cache simultaneously."""
    
    def __init__(self, redis: aioredis.Redis, default_ttl: int = 300) -> None:
        self._redis = redis
        self._default_ttl = default_ttl
    
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self._redis.setex(key, ttl or self._default_ttl, json.dumps(value, default=str))


class CacheStampedeProtection:
    """Protect against cache stampede (thundering herd)."""
    
    def __init__(self, redis: aioredis.Redis, lock_ttl: int = 10) -> None:
        self._redis = redis
        self._lock_ttl = lock_ttl
    
    async def get_or_compute(self, key: str, fetch: Callable[[], Awaitable[T]], 
                             ttl: int = 300) -> T:
        cached = await self._redis.get(key)
        if cached is not None:
            return json.loads(cached)
        
        lock_key = f"lock:{key}"
        if await self._redis.setnx(lock_key, "1"):
            await self._redis.expire(lock_key, self._lock_ttl)
            try:
                value = await fetch()
                await self._redis.setex(key, ttl, json.dumps(value, default=str))
                return value
            finally:
                await self._redis.delete(lock_key)
        else:
            for _ in range(50):
                cached = await self._redis.get(key)
                if cached is not None:
                    return json.loads(cached)
                await asyncio.sleep(0.1)
            raise TimeoutError("Cache computation timeout")
```

## Tags-based Invalidation

```python
class TaggedCache:
    """Cache with tag-based invalidation."""
    
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
    
    async def set(self, key: str, value: Any, tags: list[str], ttl: int = 300) -> None:
        """Store value and index by tags."""
        async with self._redis.pipeline() as pipe:
            pipe.setex(key, ttl, json.dumps(value, default=str))
            for tag in tags:
                pipe.sadd(f"tag:{tag}", key)
            pipe.execute()
    
    async def invalidate_tag(self, tag: str) -> None:
        """Invalidate all keys with this tag."""
        keys = await self._redis.smembers(f"tag:{tag}")
        if keys:
            async with self._redis.pipeline() as pipe:
                pipe.delete(*keys)
                pipe.delete(f"tag:{tag}")
                pipe.execute()
```

## Rate Limiting

```python
class SlidingWindowRateLimiter:
    """Sliding window rate limiter with Redis."""
    
    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis
    
    async def check(self, key: str, max_requests: int = 100, window: int = 60) -> bool:
        now = time.monotonic()
        window_key = f"ratelimit:{key}:{int(now // window)}"
        
        count = await self._redis.incr(window_key)
        if count == 1:
            await self._redis.expire(window_key, window + 1)
        
        return count <= max_requests
```


## Production-Level Implementation

```python
"""Bonus: Production-ready pattern."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtendedImplementation:
    """Extended with error handling, logging, retry."""
    
    async def process(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(10):
                result = await self._execute()
                return result
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            raise
        except Exception:
            logger.exception("Processing failed")
            raise
