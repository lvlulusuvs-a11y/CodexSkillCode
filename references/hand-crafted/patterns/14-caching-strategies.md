# Caching Strategies: Speed Up Safely

A good cache makes your service 10x faster. A bad cache serves stale data
and creates bugs that are impossible to reproduce.

## Cache-Aside Pattern (My Default)

The most common and reliable caching pattern.

```python
class UserCache:
    PREFIX = "user:"
    TTL = 300  # 5 minutes

    async def get(self, user_id: str) -> User | None:
        # 1. Try cache
        cached = await cache.get(f"{self.PREFIX}{user_id}")
        if cached:
            return User.from_json(cached)

        # 2. Try database
        user = await db.get(User, user_id)
        if user:
            # 3. Populate cache (set TTL!)
            await cache.set(
                f"{self.PREFIX}{user_id}",
                user.to_json(),
                ex=self.TTL,
            )
        return user

    async def invalidate(self, user_id: str) -> None:
        """Remove from cache when data changes."""
        await cache.delete(f"{self.PREFIX}{user_id}")
```

Pros: Simple, reliable, handles cache misses gracefully.
Cons: Every miss hits the database.

## Write-Through Pattern

Always fresh but slower writes.

```python
async def save_user(self, user: User) -> None:
    await db.save(user)              # Write to DB first
    await cache.set(                 # Then update cache
        f"user:{user.id}",
        user.to_json(),
        ex=self.TTL,
    )
```

Use when: Reads are frequent and need to be fresh.

## Write-Behind Pattern

Fast writes but risk of data loss.

```python
class WriteBehindCache:
    def __init__(self, cache, db, batch_size=100):
        self.cache = cache
        self.db = db
        self._buffer = []
        self._batch_size = batch_size

    async def set(self, key: str, data: dict) -> None:
        # Write to cache immediately
        await self.cache.set(key, data, ex=self.TTL)
        self._buffer.append((key, data))

        # Flush in batches
        if len(self._buffer) >= self._batch_size:
            await self._flush()

    async def _flush(self) -> None:
        batch = self._buffer[:]
        self._buffer = []
        try:
            async with self.db.transaction():
                for key, data in batch:
                    user_id = key.split(":")[1]
                    await self.db.save(User(id=user_id, **data))
        except Exception:
            self._buffer.extend(batch)
            raise

    async def flush_all(self) -> None:
        """Flush remaining items (call during shutdown)."""
        await self._flush()
```

Pros: Very fast writes, reduces DB load.
Cons: Data loss if cache dies before flush. Use for metrics, logs, analytics.

## Cache Invalidation

Invalidation is hard. Here is the simplest approach:

```python
class CacheManager:
    def __init__(self, cache):
        self.cache = cache

    async def on_user_updated(self, user_id: str) -> None:
        """Invalidate all cached data for a user."""
        keys = await self.cache.keys(f"user:{user_id}:*")
        if keys:
            await self.cache.delete(*keys)

    async def on_order_created(self, user_id: str) -> None:
        """Invalidate order-related cache."""
        await self.cache.delete(f"user:{user_id}:orders")
```

## Cache Anti-Patterns

### 1. No TTL
```python
await cache.set("key", value)  # Memory leak! Never expires.
```

### 2. Large Objects
```python
await cache.set("all_users", await db.get_all_users())
# Fills cache memory with rarely accessed data
```

### 3. Over-Caching
```python
await cache.set(f"balance:{user_id}", balance, ex=60)
# Account balance changes unpredictably. Cache is a lie.
```

### 4. Caching Computed Data
```python
# Better to cache the source data and compute on read
await cache.set(f"stats:{user_id}", compute_stats(user))
# Cache the user data, compute stats on the fly
```

## What I Cache

| Data | TTL | Strategy |
|------|-----|----------|
| User profile | 5 min | Cache-aside, invalidate on update |
| Product catalog | 1 hour | Write-through (admin updates) |
| Session data | Until logout | Cache-aside |
| Rate limiter counters | 1 min | Write-behind |
| Configuration | 10 min | Cache-aside, manual refresh |

## What I Never Cache

- Account balances (too sensitive)
- Inventory counts (change too fast)
- Real-time positions (always need fresh data)
- Auth tokens (security risk)
- One-time passwords (obviously)

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written
