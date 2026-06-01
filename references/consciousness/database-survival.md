# 🗄️ Базы данных: как не умереть в 3 часа ночи

Я работал с PostgreSQL, MySQL, Cassandra, MongoDB, SQLite, ClickHouse, Redis, Kafka, ScyllaDB. 
Каждая имеет свою душу и свои грабли.

## PostgreSQL — мой main driver

### Connection pooling — это не опция

**Плохо:**
```python
# Каждый запрос создаёт новое соединение
async def get_user(user_id: str) -> User:
    conn = await asyncpg.connect(DATABASE_URL)  # ❌ Дорого!
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    finally:
        await conn.close()
```

**Хорошо:**
```python
import asyncpg
from dataclasses import dataclass


@dataclass
class DatabasePool:
    url: str
    min_size: int = 5
    max_size: int = 20
    
    def __post_init__(self):
        self._pool: asyncpg.Pool | None = None
    
    async def connect(self):
        self._pool = await asyncpg.create_pool(
            self.url,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=30.0,
            max_inactive_connection_lifetime=300.0,
            setup=self._setup_connection,
        )
    
    async def _setup_connection(self, conn: asyncpg.Connection):
        """Настройка каждого нового соединения."""
        await conn.execute("SET statement_timeout = '10s'")
        await conn.execute("SET idle_in_transaction_session_timeout = '30s'")
    
    async def execute(self, query: str, *args) -> list:
        assert self._pool is not None, "Pool not initialized"
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def close(self):
        if self._pool:
            await self._pool.close()
```

### N+1 запросов — убийца производительности

**Плохо:**
```python
async def get_users_with_orders():
    users = await db.execute("SELECT * FROM users")
    
    for user in users:
        # Для КАЖДОГО пользователя — отдельный запрос ❌
        orders = await db.execute(
            "SELECT * FROM orders WHERE user_id = $1", user["id"]
        )
        user["orders"] = orders
    
    return users
# 1 запрос + N запросов → медленно
```

**Хорошо:**
```python
async def get_users_with_orders():
    users = await db.execute("SELECT * FROM users")
    user_ids = [u["id"] for u in users]
    
    # Один запрос на всех
    orders = await db.execute(
        "SELECT * FROM orders WHERE user_id = ANY($1)", user_ids
    )
    
    # Группируем в памяти
    orders_by_user = defaultdict(list)
    for order in orders:
        orders_by_user[order["user_id"]].append(order)
    
    for user in users:
        user["orders"] = orders_by_user.get(user["id"], [])
    
    return users
# Всегда 2 запроса, независимо от количества пользователей
```

### Правильные индексы

```sql
-- Если ты пишешь WHERE user_id = ? — должен быть индекс на user_id
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Если WHERE user_id = ? AND status = ? — композитный индекс
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Если ORDER BY created_at DESC — покрывающий индекс
CREATE INDEX idx_orders_user_status_created 
    ON orders(user_id, status, created_at DESC);

-- Если нужен full-text search — GIN/GIST
CREATE INDEX idx_users_search ON users USING GIN(to_tsvector('russian', name || ' ' || email));
```

**Как я проверяю индексы:**
```sql
-- План запроса — библия
EXPLAIN ANALYZE
SELECT * FROM orders 
WHERE user_id = '123' AND status = 'active'
ORDER BY created_at DESC;

-- Медленные запросы — главная метрика
SELECT query, calls, total_time / calls AS avg_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

Если `EXPLAIN ANALYZE` показывает `Seq Scan` на таблице >10k записей — **нужен индекс**.

### Миграции должны быть безопасными

```python
"""migration_002_add_preferences_column.py

Правило: миграция не должна ломать работающий код.
"""
import alembic.op as op

def upgrade():
    # ✅ Добавляем колонку с default (не ломает SELECT *)
    op.add_column(
        'users',
        sa.Column('preferences', sa.JSON, server_default='{}'),
    )
    
    # ✅ Создаём индекс без блокировки (CONCURRENTLY)
    op.execute(
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_preferences '
        'ON users USING GIN (preferences)'
    )

def downgrade():
    op.drop_column('users', 'preferences')
```

**Что нельзя делать в миграции:**
```sql
-- ❌ DROP COLUMN без проверки, кто использует
ALTER TABLE users DROP COLUMN old_field; -- Может сломать SELECT *

-- ❌ RENAME TABLE без синхронизации кода
ALTER TABLE users RENAME TO accounts; -- Если код ещё не обновлён — всё упало

-- ❌ Добавление NOT NULL на существующую колонку
ALTER TABLE users ALTER COLUMN email SET NOT NULL; -- Если есть NULL — упадёт
```

### Lock-проблемы

**Самый частый deadlock:**
```python
# Транзакция 1: order1 → order2
await db.execute("UPDATE orders SET status = 'processing' WHERE id = 'order1'")
await db.execute("UPDATE orders SET status = 'processing' WHERE id = 'order2'")

# Транзакция 2: order2 → order1
await db.execute("UPDATE orders SET status = 'shipped' WHERE id = 'order2'")
await db.execute("UPDATE orders SET status = 'shipped' WHERE id = 'order1'")
# 💥 DEADLOCK
```

**Решение: всегда блокируем в одном порядке**
```python
async def update_orders(order_ids: list[str], status: str):
    # Сортируем ID перед блокировкой — гарантирует порядок
    for oid in sorted(order_ids):
        await db.execute(
            "UPDATE orders SET status = $1 WHERE id = $2",
            status, oid,
        )
```

### Paging — не OFFSET, а keyset pagination

**Плохо:**
```python
# OFFSET сканирует все предыдущие строки
users = await db.execute(
    "SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 100000"
)
# O(n) — чем дальше, тем медленнее
```

**Хорошо:**
```python
# Keyset pagination — использует индекс
async def get_users_page(last_id: int | None = None, limit: int = 20):
    if last_id:
        users = await db.execute(
            "SELECT * FROM users WHERE id > $1 ORDER BY id LIMIT $2",
            last_id, limit,
        )
    else:
        users = await db.execute(
            "SELECT * FROM users ORDER BY id LIMIT $1",
            limit,
        )
    
    next_cursor = users[-1]["id"] if len(users) == limit else None
    return users, next_cursor
```

## Redis — не просто кеш

### Cache-aside pattern

```python
class UserCache:
    PREFIX = "user:"
    TTL = 300  # 5 минут
    
    def __init__(self, redis, db):
        self._redis = redis
        self._db = db
    
    async def get_user(self, user_id: str) -> User | None:
        # 1. Пытаемся из кеша
        cached = await self._redis.get(f"{self.PREFIX}{user_id}")
        if cached:
            return User.from_json(cached)
        
        # 2. Если нет — из БД
        user = await self._db.get_user(user_id)
        if user:
            # 3. Сохраняем в кеш
            await self._redis.setex(
                f"{self.PREFIX}{user_id}", 
                self.TTL, 
                user.to_json(),
            )
        
        return user
    
    async def invalidate_user(self, user_id: str):
        """Инвалидация при изменении."""
        await self._redis.delete(f"{self.PREFIX}{user_id}")
```

### Rate limiting с Redis

```python
import time


class SlidingWindowRateLimiter:
    """Rate limiter на скользящем окне через Redis.
    
    Позволяет N запросов за W секунд.
    """
    
    def __init__(self, redis, max_requests: int = 100, window: int = 60):
        self._redis = redis
        self.max_requests = max_requests
        self.window = window
    
    async def check(self, key: str) -> bool:
        """Проверяет, не превышен ли лимит."""
        now = int(time.monotonic())
        window_start = now - self.window
        
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)  # Удаляем старые
        pipe.zcard(key)                               # Считаем оставшиеся
        pipe.zadd(key, {str(now): now})               # Добавляем текущий
        pipe.expire(key, self.window)                 # TTL
        _, count, _, _ = await pipe.execute()
        
        return count < self.max_requests


# Использование
limiter = SlidingWindowRateLimiter(redis, max_requests=10, window=1)

async def handler(request):
    if not await limiter.check(f"ratelimit:{request.ip}"):
        return HTTPResponse(429, "Too many requests")
    return await process_request(request)
```

### Distributed lock (Redlock-лайт)

```python
class DistributedLock:
    """Распределённая блокировка через Redis."""
    
    def __init__(self, redis, lock_key: str, ttl: int = 10):
        self._redis = redis
        self._lock_key = f"lock:{lock_key}"
        self._ttl = ttl
        self._token = str(uuid4())
    
    async def __aenter__(self):
        acquired = await self._redis.set(
            self._lock_key,
            self._token,
            nx=True,  # Только если ключа нет
            ex=self._ttl,
        )
        if not acquired:
            raise LockNotAcquiredError(f"Could not acquire lock {self._lock_key}")
        return self
    
    async def __aexit__(self, *args):
        # Только если мы владельцы блокировки
        await self._redis.eval("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """, 1, self._lock_key, self._token)


# Использование
async def process_payment(order_id: str):
    async with DistributedLock(redis, f"payment:{order_id}", ttl=30):
        # Только один worker обрабатывает заказ
        await payment_service.charge(order_id)
```

## Что я проверяю при инциденте с БД

```bash
# 1. Есть ли соединения?
SELECT count(*) FROM pg_stat_activity;

# 2. Что сейчас выполняется?
SELECT pid, query, state, wait_event, now() - query_start AS duration
FROM pg_stat_activity 
WHERE state != 'idle'
ORDER BY duration DESC;

# 3. Есть ли блокировки?
SELECT blocked.pid AS blocked_pid, blocker.pid AS blocker_pid
FROM pg_locks blocked
JOIN pg_locks blocker ON blocked.locktype = blocker.locktype
WHERE NOT blocked.granted;

# 4. Медленные запросы?
SELECT query, calls, total_time / calls AS avg_ms
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

**Коротко:** БД — это сердце системы. Относись к ней соответственно. Каждый запрос — это ресурс. Каждая транзакция — это блокировка. Каждый индекс — это компромисс (быстрее SELECT, медленнее INSERT/UPDATE).
