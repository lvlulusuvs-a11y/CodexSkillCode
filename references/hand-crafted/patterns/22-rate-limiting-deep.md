# Rate Limiting: Complete Guide

Rate limiting protects your service from abuse and overload.

## Why Rate Limit

1. Prevent abuse - brute force attacks on login
2. Fair usage - one user cant consume all resources
3. Cost control - limit expensive operations
4. Stability - prevent cascading failures
5. Capacity management - traffic shaping

## Algorithm Comparison

Token Bucket: Allow bursts, steady rate. Good for API endpoints.
Leaky Bucket: Smooth traffic, no bursts. Good for processing pipelines.
Fixed Window: Simple but allows spikes at window boundary.
Sliding Window: More accurate than fixed window.

## Token Bucket Implementation

import time
from dataclasses import dataclass

@dataclass
class TokenBucket:
    rate: float = 10.0  # tokens per second
    burst: int = 20     # max tokens

    def __post_init__(self):
        self.tokens = self.burst
        self.last_refill = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

## Sliding Window with Redis

import time

class SlidingWindowRateLimiter:
    def __init__(self, redis, limit: int = 100, window: int = 60):
        self.redis = redis
        self.limit = limit
        self.window = window

    async def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(uuid.uuid4()): now})
        pipe.expire(key, self.window + 1)
        _, count, _, _ = await pipe.execute()

        return int(count) <= self.limit

## Rate Limiting Levels

Level 1: Global (protects your infrastructure)
Level 2: Per-user (fair usage)
Level 3: Per-endpoint (protect expensive operations)
Level 4: Per-IP (protect against IP-based attacks)

## Response for Rate-Limited Requests

HTTP 429 Too Many Requests
Retry-After: 60

{
    "error": "Too Many Requests",
    "retry_after": 60,
    "limit": 100,
    "window": 60
}

## Best Practices

1. Return Retry-After header
2. Return remaining quota in headers
3. Use different limits for different endpoints
4. Dont rate limit health checks
5. Rate limit auth endpoints strictly
6. Rate limit at the gateway level
7. Have a bypass mechanism for emergencies


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.
