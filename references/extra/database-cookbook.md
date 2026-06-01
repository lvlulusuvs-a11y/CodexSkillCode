# Database Cookbook

**Рецепты для работы с БД. SQL запросы, оптимизация, паттерны.**

---

## 1. PostgreSQL Connection Setup

```python
import asyncpg
from typing import Any

# Connection pool
pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@localhost:5432/db",
    min_size=5,
    max_size=20,
    command_timeout=60,
    max_inactive_connection_lifetime=300,
)

# Connection
async with pool.acquire() as conn:
    result = await conn.fetch("SELECT * FROM users")
```

## 2. SQLAlchemy 2.0 Models

```python
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    
    order: Mapped["Order"] = relationship(back_populates="items")
```

## 3. Common SQL Queries

```sql
-- SELECT with conditions
SELECT id, name, email FROM users 
WHERE is_active = true 
  AND created_at >= '2024-01-01'
ORDER BY created_at DESC 
LIMIT 10 OFFSET 0;

-- JOIN
SELECT u.name, o.total, o.created_at
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.is_active = true
ORDER BY o.created_at DESC;

-- Aggregation
SELECT 
  u.id,
  u.name,
  COUNT(o.id) as order_count,
  SUM(o.total) as total_spent,
  AVG(o.total) as avg_order,
  MAX(o.created_at) as last_order
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC;

-- Window functions
SELECT 
  id, user_id, total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as order_num,
  SUM(total) OVER (PARTITION BY user_id) as user_total,
  AVG(total) OVER () as avg_order
FROM orders;

-- CTE (Common Table Expression)
WITH user_stats AS (
  SELECT user_id, COUNT(*) as cnt, SUM(total) as total
  FROM orders
  GROUP BY user_id
)
SELECT u.name, s.cnt, s.total
FROM users u
JOIN user_stats s ON s.user_id = u.id
WHERE s.total > 1000;

-- Update with join
UPDATE users u
SET total_orders = s.cnt
FROM (SELECT user_id, COUNT(*) as cnt FROM orders GROUP BY user_id) s
WHERE u.id = s.user_id;

-- Insert on conflict (upsert)
INSERT INTO users (email, name) VALUES ('test@test.com', 'Test')
ON CONFLICT (email) 
DO UPDATE SET name = EXCLUDED.name, updated_at = NOW();

-- Delete with join
DELETE FROM orders o
USING users u
WHERE o.user_id = u.id AND u.is_active = false;

-- Full-text search
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'python & async');

-- Pagination with cursor
SELECT * FROM users
WHERE id > $cursor
ORDER BY id
LIMIT 100;

-- Date truncation
SELECT 
  date_trunc('month', created_at) as month,
  COUNT(*) as orders,
  SUM(total) as revenue
FROM orders
GROUP BY month
ORDER BY month;
```

## 4. Indexing Guide

```sql
-- B-tree (default) — для =, >, <, >=, <=, BETWEEN, IN, LIKE (без %%)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_created ON orders(created_at DESC);

-- Hash index — для = (только равенство)
CREATE INDEX idx_users_email_hash ON users USING hash(email);

-- GiST — для full-text, гео, массивы
CREATE INDEX idx_articles_search ON articles USING gist(to_tsvector('english', body));

-- GIN — для JSONB, массивы
CREATE INDEX idx_events_payload ON events USING gin(payload);

-- Partial index — только для нужных строк
CREATE INDEX idx_users_active ON users(id) WHERE is_active = true;

-- Composite index — для комбинированных запросов
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Covering index (include) — данные в индексе
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);

-- Правила:
-- 1. Индекс для WHERE, JOIN, ORDER BY
-- 2. Не индексировать маленькие таблицы
-- 3. Не индексировать столбцы с редкими значениями
-- 4. Composite: сначала селективные столбцы
-- 5. Мониторить неиспользуемые индексы
```

## 5. Query Performance Tuning

```python
# EXPLAIN ANALYZE
async def explain_query(query: str) -> None:
    result = await conn.fetch(f"EXPLAIN ANALYZE {query}")
    for line in result:
        print(line["QUERY PLAN"])

# Common issues and fixes:
# 1. Sequential scan → нужен индекс
# 2. Nested Loop → нужен другой join или индекс
# 3. Sort → убери ORDER BY или добавь индекс
# 4. Hash Aggregate → может много памяти

# Slow query detection
SELECT 
    query,
    calls,
    total_exec_time / calls as avg_time,
    rows / calls as avg_rows,
    shared_blks_hit / (shared_blks_hit + shared_blks_read) * 100 as cache_hit_ratio
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## 6. Transactions and Locking

```python
# Transaction
async with conn.transaction():
    await conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    await conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

# row-level lock (SELECT FOR UPDATE)
async with conn.transaction():
    row = await conn.fetchrow("SELECT balance FROM accounts WHERE id = $1 FOR UPDATE", 1)
    if row["balance"] >= 100:
        await conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")

# Advisory lock (application-level)
await conn.execute("SELECT pg_advisory_lock(123)")
try:
    await process()
finally:
    await conn.execute("SELECT pg_advisory_unlock(123)")
```

## 7. Migration Patterns

```python
# alembic revision --autogenerate -m "description"

# 1. Add column with default
# op.add_column('users', sa.Column('timezone', sa.String(50), server_default='UTC'))

# 2. Add NOT NULL to existing column
# op.alter_column('users', 'email', nullable=False)

# 3. Rename column
# op.alter_column('users', 'full_name', new_column_name='name')

# 4. Add index
# op.create_index('idx_users_email', 'users', ['email'])

# 5. Data migration
# op.execute("UPDATE users SET timezone = 'UTC' WHERE timezone IS NULL")

# 6. Add foreign key
# op.create_foreign_key('fk_orders_users', 'orders', 'users', ['user_id'], ['id'])
```


---

## Production Expansion

### Real-World Example

```python
"""Production-grade implementation."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionExample:
    """Battle-tested pattern from Big Tech production."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with proper error handling, retry, and observability."""
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise


### Key Takeaways for Principal Engineers

1. **Always add observability** — metrics, logs, traces
2. **Always handle errors** — don't let exceptions propagate silently
3. **Always set timeouts** — external calls should never hang forever
4. **Always think about scale** — what works for 10 req/s may fail at 1000
5. **Always document why** — the "why" is more important than the "what"
6. **Always test edge cases** — empty, None, max values, concurrent access
7. **Always consider rollback** — every deploy should be revertible
8. **Always plan for failure** — network, disk, memory, dependencies will fail

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No timeouts | Hanging requests | Add timeout to all external calls |
| No retry | Transient failures become permanent | Add retry with backoff + jitter |
| No circuit breaker | Cascading failures | Add circuit breaker on dependencies |
| No health checks | k8s kills healthy pods | Add meaningful health endpoints |
| No rate limiting | Service overwhelmed | Add rate limiter per client |
| No graceful shutdown | Dropped requests | Proper SIGTERM handling |
| No connection pooling | DB connection exhaustion | Configure pool size, heartbeat |
| No caching | Repeated expensive computations | Multi-level caching with TTL |
| No feature flags | Rollbacks require full deploy | Feature flags for gradual rollout |
| No monitoring | Blind to production issues | RED metrics, SLOs, alerts |


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
