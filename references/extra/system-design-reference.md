# System Design Reference

**Как проектировать системы. Паттерны, компромиссы, реальные примеры.**

---

## 1. CAP Theorem и выбор БД

```
Consistency (C)  ─────  Availability (A)
        ╲                ╱
         ╲   Partition  ╱
          ╲  Tolerance ╱
           ╲   (P)    ╱
            ╲        ╱
             ╲______╱

Выбирай 2 из 3, но Network Partition неизбежен → выбирай между CP и AP.

┌────────────────────┬────────────────────┬────────────────────┐
│                    │        CP          │        AP          │
├────────────────────┼────────────────────┼────────────────────┤
│ Примеры            │ etcd, Zookeeper,   │ Cassandra,         │
│                    │ Consul            │ DynamoDB, Riak     │
├────────────────────┼────────────────────┼────────────────────┤
│ Когда нужен        │ Финансы,           │ Соцсети,           │
│                    │ заказы,            │ лента новостей,    │
│                    │ блокчейн           │ аналитика          │
├────────────────────┼────────────────────┼────────────────────┤
│ Что жертвуем       │ Доступность при    │ Консистентность    │
│                    │ разделении сети    │ (eventual          │
│                    │                    │ consistency)       │
└────────────────────┴────────────────────┴────────────────────┘

PostgreSQL/MySQL: CA (без разделения сети), CP (с разделением)
MongoDB: CP по умолчанию, AP опционально
Cassandra: AP
Redis: CP (single node), AP (cluster)
```

## 2. Database Selection

```python
# ─── Выбор БД ─────────────────────────────────────────────────────
# PostgreSQL:    Структурированные данные, ACID, сложные запросы
# ClickHouse:    Аналитика, временные ряды, миллиарды строк
# MongoDB:       JSON-документы, гибкая схема, прототипирование
# Redis:         Кэш, сессии, очереди, rate limiting
# Cassandra:     Горизонтальное масштабирование, write-heavy
# Elasticsearch: Полнотекстовый поиск, логи, observability
# S3/MinIO:      Файлы, изображения, бэкапы, большие данные

# ─── SQL vs NoSQL ─────────────────────────────────────────────────
# SQL:
# + ACID, joins, constraints, standardised
# - Вертикальное масштабирование, rigid schema
# Выбирай SQL, пока не докажешь, что нужен NoSQL

# NoSQL:
# + Горизонтальное масштабирование, flexible schema
# - Нет joins, eventual consistency, vendor lock-in
# Выбирай NoSQL, когда:
#   - >10TB данных
#   - Пишешь >100K запросов/сек
#   - Схема данных постоянно меняется
#   - Нужна геораспределённость
```

## 3. API Architecture

### REST
```python
# Ресурсы, HTTP методы, stateless
# ✅ GET /users        → список
# ✅ POST /users       → создать
# ✅ GET /users/1      → один
# ✅ PUT /users/1      → полностью заменить
# ✅ PATCH /users/1    → частично изменить
# ✅ DELETE /users/1   → удалить

# Статусы:
# 200 OK             — успех
# 201 Created        — создано
# 204 No Content     — удалено
# 400 Bad Request    — невалидный запрос
# 401 Unauthorized   — не авторизован
# 403 Forbidden      — нет прав
# 404 Not Found      — не найдено
# 409 Conflict       — конфликт
# 422 Unprocessable  — валидация не прошла
# 429 Too Many       — rate limit
# 500 Internal       — сервер упал
```

### GraphQL
```python
# Один endpoint, клиент выбирает поля
# Плюс: нет over/under-fetching, типизированная схема
# Минус: сложное кэширование, N+1 через resolver'ы
# Когда: сложные клиенты с разными потребностями в данных

# Решение N+1 в GraphQL: DataLoader (batching + caching)
from typing import Any
class UserDataLoader:
    def __init__(self, db):
        self._db = db
        self._cache: dict[int, Any] = {}
        
    async def load(self, user_id: int) -> Any:
        if user_id not in self._cache:
            # Batch load: один SQL запрос для всех ID
            users = await self._db.fetch(
                "SELECT * FROM users WHERE id = ANY($1)",
                list(self._cache.keys()),
            )
            for user in users:
                self._cache[user["id"]] = user
        return self._cache.get(user_id)
```

### gRPC
```python
# Protocol Buffers, HTTP/2, streaming
# Плюс: быстрый (binary), строгая типизация, bidirectional streaming
# Минус: сложный дебаг, нет браузерной поддержки
# Когда: микросервисы, mobile, real-time
```

## 4. Caching Strategies

```
                         ┌──────────────┐
                         │   Client     │
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │  CDN Cache   │  CloudFlare, Akamai
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │  App Cache   │  Redis, Memcached
                         └──────┬───────┘
                                │
                         ┌──────▼───────┐
                         │  DB Cache    │  PostgreSQL shared buffers
                         └──────────────┘
```

### Cache-Aside (Lazy Loading)
```python
async def get_user(user_id: int) -> User:
    # 1. Попробовать кэш
    if cached := await redis.get(f"user:{user_id}"):
        return User(**json.loads(cached))
    
    # 2. Промах → БД
    user = await db.get(User, user_id)
    if not user:
        return None
    
    # 3. Заполнить кэш
    await redis.setex(f"user:{user_id}", 300, user.model_dump_json())
    
    return user
```

### Write-Through
```python
async def update_user(user_id: int, data: dict) -> User:
    # Пишем в БД
    user = await db.update(User, user_id, data)
    
    # Пишем в кэш (синхронно с БД)
    await redis.setex(f"user:{user_id}", 300, user.model_dump_json())
    
    return user
```

### Write-Behind (асинхронная запись)
```python
async def update_user(user_id: int, data: dict) -> User:
    # Сразу пишем в кэш (быстрый ответ)
    await redis.setex(f"user:{user_id}", 300, json.dumps(data))
    
    # Отправляем в очередь на запись в БД
    await queue.put(("update_user", user_id, data))
    
    return User(**data)

# Background worker пишет в БД асинхронно
```

### Cache Invalidation
```python
# Сложность: устаревшие данные
# Стратегии:
# 1. TTL (Time To Live) — данные сами умирают
# 2. Event-based — при изменении данных, инвалидировать кэш
# 3. Versioning — версионировать данные, кэш по версии

async def invalidate_by_tag(tag: str) -> None:
    """Инвалидация по тегу."""
    keys = await redis.smembers(f"tag:{tag}")
    if keys:
        await redis.delete(*keys)
        await redis.delete(f"tag:{tag}")

async def set_tagged(key: str, value: Any, tags: list[str]) -> None:
    """Сохранение с тегированием."""
    await redis.setex(key, 300, value)
    for tag in tags:
        await redis.sadd(f"tag:{tag}", key)
```

## 5. Message Queue Patterns

### Когда нужна очередь
- **Decoupling** — producer не знает consumer'ов
- **Buffering** — сглаживание пиков нагрузки
- **Guaranteed delivery** — сообщение не потеряется
- **Fan-out** — одно сообщение → много обработчиков
- **Retry + DLQ** — Dead Letter Queue для упавших сообщений

### Broker сравнение
```python
# Redis List/Stream:  5K msg/s, просто, встроенно
# RabbitMQ:          20K msg/s, routing, ACK, management UI
# Kafka:            100K+ msg/s,持久化, replay, partitioning
# SQS/SNS:           cloud, managed, auto-scaling

# ─── Выбор ───
# Нужна надёжность + routing → RabbitMQ
# Нужен stream + replay → Kafka
# Нужен FIFO просто → Redis List
# Нужен pub/sub просто → Redis Pub/Sub
```

### Пример: надёжный consumer
```python
async def process_messages() -> None:
    consumer = create_consumer("orders")
    
    while True:
        try:
            message = await consumer.receive(timeout=30)
            
            async with message.process():
                # Если упадёт → retry, если retry исчерпан → DLQ
                result = await process_order(message.body)
                
                if not result.success:
                    await message.nack(delay=5.0)  # retry через 5s
                    continue
                
                await message.ack()  # подтвердить обработку
                
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.exception("Fatal consumer error")
            await asyncio.sleep(1)
```

## 6. Microservices Communication

```
               ┌──────────────┐
               │   API GW     │
               └──────┬───────┘
          ┌───────────┼───────────┐
          │           │           │
    ┌─────▼────┐ ┌───▼───┐ ┌────▼────┐
    │  Auth    │ │ User  │ │ Order   │───→ Orders DB
    │  Service │ │ Srv   │ │ Srv     │
    └──────────┘ └───────┘ └────┬────┘
                                │ gRPC/Event
                         ┌──────▼──────┐
                         │  Payment    │───→ Payments DB
                         │  Service    │
                         └─────────────┘
```

### Sync (REST/gRPC)
```python
# Плюс: простота, понятный flow
# Минус: каскадные сбои, latency = sum of all calls

# Защита: timeouts + circuit breaker
async def get_order_details(order_id: int) -> dict:
    order = await order_service.get(order_id)
    
    try:
        payment = await asyncio.wait_for(
            payment_service.get(order.payment_id),
            timeout=3.0,
        )
        order["payment"] = payment
    except (TimeoutError, ServiceError):
        order["payment"] = {"status": "unknown"}
    
    return order
```

### Async (Events/Messages)
```python
# Плюс: слабая связанность, resilience
# Минус: eventual consistency, сложный дебаг

# Пример: Order Created → send event
async def create_order(data: dict) -> Order:
    order = Order(**data)
    await db.save(order)
    
    # Публикуем событие (не ждём обработчиков)
    await event_bus.publish("order.created", {
        "order_id": order.id,
        "user_id": order.user_id,
        "amount": order.total,
    })
    
    return order

# Payment Service слушает и обрабатывает
@event_bus.on("order.created")
async def handle_order_created(event: dict) -> None:
    try:
        payment_id = await payment_service.charge(event["amount"])
        await event_bus.publish("payment.completed", {
            "order_id": event["order_id"],
            "payment_id": payment_id,
        })
    except Exception as e:
        await event_bus.publish("payment.failed", {
            "order_id": event["order_id"],
            "error": str(e),
        })
```

## 7. Error Handling Strategies

### Retry Strategies
```python
# ─── Immediate retry ───
# Для transient errors (connection reset, timeout)
# 1-3 попытки, без задержки

# ─── Exponential backoff ───
# 1s → 2s → 4s → 8s → ...
# Для rate limiting, overload

# ─── Jitter ───
# Добавить случайность: delay ± 20%
# Избежать thundering herd (все retry одновременно)

# ─── Circuit breaker ───
# После N ошибок → не вызывать сервис M секунд
# HALF_OPEN для проверки восстановления
```

### Graceful Degradation
```python
# Вместо падения — вернуть "лучшее из доступного"

async def get_recommendations(user_id: int) -> list[Product]:
    try:
        return await ml_service.recommend(user_id)
    except ServiceError:
        # ML сервис упал — вернуть популярные
        return await product_service.get_popular(limit=10)
    except Exception:
        # Всё плохо — вернуть пусто
        return []
```

## 8. Observability

### Three Pillars
```python
# 1. Logging — структурированные логи
# 2. Metrics — счётчики, гистограммы
# 3. Tracing — трейсинг запросов через сервисы

# RED method (микроcервисы):
# Rate — запросов в секунду
# Errors — ошибки в секунду
# Duration — время обработки

# USE method (инфраструктура):
# Utilization — загрузка ресурса
# Saturation — перегрузка
# Errors — количество ошибок
```

### Minimal Monitoring Setup
```python
# Prometheus + Grafana
# - Request rate, latency (p50, p95, p99), error rate
# - CPU, Memory, DB connections
# - Business metrics (заказы/мин, регистрации/день)

# Health endpoints:
# /health — liveness (сервер жив)
# /ready — readiness (готов принимать трафик)
# /metrics — для Prometheus

from prometheus_client import Counter, Histogram, generate_latest

REQUESTS = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status"])
LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["method", "endpoint"])
```

## 9. Scaling Patterns

### Horizontal Scaling (sharding)
```python
# Деление данных по ключу
# user_id % N → шард N
# Плюс: линейное масштабирование
# Минус: сложные跨шард запросы, rebalancing

class ShardedDB:
    def __init__(self, shards: list[Database]) -> None:
        self._shards = shards
    
    def _get_shard(self, key: str) -> Database:
        return self._shards[hash(key) % len(self._shards)]
    
    async def get(self, key: str) -> Any:
        return await self._get_shard(key).get(key)
    
    async def set(self, key: str, value: Any) -> None:
        await self._get_shard(key).set(key, value)
```

### Bulkhead Pattern
```python
# Изоляция компонентов — проблема в одном не валит всё

class BulkheadPool:
    """Пул с изоляцией по типу запроса."""
    
    def __init__(self) -> None:
        self._pools: dict[str, asyncio.Semaphore] = {}
    
    def add(self, name: str, max_concurrent: int = 10) -> None:
        self._pools[name] = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, pool_name: str, func: Callable) -> Any:
        sem = self._pools.get(pool_name)
        if not sem:
            raise ValueError(f"No pool: {pool_name}")
        
        async with sem:
            return await func()

# Использование
pool = BulkheadPool()
pool.add("auth", max_concurrent=5)   # auth — редко
pool.add("orders", max_concurrent=20) # orders — часто
pool.add("payments", max_concurrent=3) # payments — медленно

await pool.execute("orders", create_order)
```

## 10. Security Patterns

### Token-based Auth
```python
# JWT: stateless, но нельзя отозвать
# Session: stateful (redis), можно отозвать

async def authenticate(request: Request) -> User | None:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return await user_repo.get(payload["user_id"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### Rate Limiting
```python
# Token bucket, Sliding window, Fixed window
# Per-IP, Per-User, Per-Endpoint

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 100, window: float = 60.0):
        self._max = max_requests
        self._window = window
        self._requests: dict[str, list[float]] = {}
    
    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - self._window
        
        # Очистить старые
        if key in self._requests:
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]
        
        # Проверить лимит
        if len(self._requests.get(key, [])) >= self._max:
            return False
        
        # Добавить запрос
        self._requests.setdefault(key, []).append(now)
        return True
```

### Input Validation
```python
# Никогда не доверяй пользовательскому вводу
# Валидация на границе системы (Pydantic, Marshmallow)

from pydantic import BaseModel, Field, EmailStr

class CreateUserSchema(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    
    # Дополнительная валидация
    def validate_name(cls, v: str) -> str:
        if any(c in v for c in "<>\"'%"):
            raise ValueError("Invalid characters in name")
        return v.strip()

# SQL injection: always use parameterized queries
await conn.execute("SELECT * FROM users WHERE id = $1", user_id)

# XSS: escape HTML при выводе
import html
safe_html = html.escape(user_input)
```

## Decision Flow

```
Нужно хранить данные?
├─ Структурированные, связи → SQL (PostgreSQL)
├─ Документы, гибкая схема → MongoDB
├─ Ключ-значение, кэш → Redis
├─ Большие файлы → S3/MinIO
├─ Поиск → Elasticsearch
└─ Time-series → ClickHouse / TimescaleDB

Нужна коммуникация?
├─ Синхронная, простые микросервисы → REST/gRPC
├─ Асинхронная, decoupling → Message Queue
├─ Real-time → WebSocket / gRPC stream

Нужна обработка?
├─ API → FastAPI / Django
├─ Batch → Celery / Airflow
├─ Stream → Kafka Streams / Flink
└─ CPU-bound → Multiprocessing / Numba / Rust
```

---

## 4. Distributed Systems Patterns

### 4.1 Leader Election

```python
"""Leader election for distributed lock."""
import asyncio
import logging
import os
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class LeaderElection:
    """Leader election via Redis SET NX with TTL.
    
    Battle Scar: Без leader election при деплое оба экземпляра
    крановшегорали SQS messages — один обрабатывал, второй дублировал.
    """
    redis_client: Any
    lock_key: str = "leader:service"
    ttl: int = 30
    hostname: str = field(default_factory=lambda: os.uname().nodename)
    _is_leader: bool = False
    
    async def try_acquire(self) -> bool:
        acquired = await self.redis_client.setnx(
            self.lock_key, 
            self.hostname,
            expire=self.ttl,
        )
        if acquired:
            self._is_leader = True
            logger.info(f"Became leader: {self.hostname}")
        return acquired
    
    async def renew(self) -> None:
        if self._is_leader:
            await self.redis_client.expire(self.lock_key, self.ttl)
    
    async def run_loop(self) -> None:
        """Background loop to maintain leadership."""
        while True:
            try:
                if not self._is_leader:
                    await self.try_acquire()
                else:
                    await self.renew()
            except Exception as e:
                logger.error(f"Leader election error: {e}")
                self._is_leader = False
            await asyncio.sleep(self.ttl // 3)
    
    @property
    def is_leader(self) -> bool:
        return self._is_leader
```

### 4.2 Distributed Cache (Redis + Local Fallback)

```python
"""Multi-layer cache with cache stampede protection."""
from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import logging
import random
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class CacheConfig:
    """Configuration for multi-layer cache."""
    redis_ttl: int = 3600          # Redis TTL (seconds)
    local_ttl: int = 60            # Local cache TTL (seconds)
    local_max_size: int = 1000     # Local LRU max entries
    stampede_protection: bool = True
    key_prefix: str = "cache:"


class MultiLayerCache:
    """Two-layer cache: local LRU + Redis with stampede protection.
    
    Battle Scar: При падении Redis (cache miss for ALL keys) ~1000
    запросов пошли в БД одновременно — DB died. С local cache + 
    stampede protection — единицы запросов.
    """
    
    def __init__(self, redis_client: Any, config: CacheConfig | None = None):
        self._redis = redis_client
        self._config = config or CacheConfig()
        self._local: OrderedDict[str, tuple[Any, float]] = OrderedDict()
    
    async def get(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[T]] | None = None,
        ttl: int | None = None,
    ) -> T | None:
        full_key = self._config.key_prefix + key
        
        # 1. Try local cache
        now = time.monotonic()
        if full_key in self._local:
            value, expires = self._local[full_key]
            if now < expires:
                self._local.move_to_end(full_key)
                return value
            del self._local[full_key]
        
        # 2. Try Redis
        try:
            raw = await self._redis.get(full_key)
            if raw:
                value = json.loads(raw)
                self._set_local(full_key, value, self._config.local_ttl)
                return value
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
        
        # 3. Fetch from source (with stampede protection)
        if fetcher:
            value = await self._fetch_with_protection(full_key, fetcher, ttl)
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        full_key = self._config.key_prefix + key
        ttl = ttl or self._config.redis_ttl
        
        self._set_local(full_key, value, self._config.local_ttl)
        
        try:
            await self._redis.set(full_key, json.dumps(value), expire=ttl)
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
    
    async def delete(self, key: str) -> None:
        full_key = self._config.key_prefix + key
        self._local.pop(full_key, None)
        try:
            await self._redis.delete(full_key)
        except Exception:
            pass
    
    async def _fetch_with_protection(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[T]],
        ttl: int | None = None,
    ) -> T:
        ttl = ttl or self._config.redis_ttl
        
        if self._config.stampede_protection:
            # Redis SET NX with short TTL for stampede protection
            lock_key = f"{key}:lock"
            acquired = await self._redis.setnx(lock_key, "1", expire=10)
            
            if acquired or not self._local.get(key):
                # We are the lucky one to fetch
                try:
                    value = await fetcher()
                    await self.set(key, value, ttl)
                    return value
                finally:
                    await self._redis.delete(lock_key)
            else:
                # Wait and use stale value
                await asyncio.sleep(random.uniform(0.05, 0.15))
                if key in self._local:
                    return self._local[key][0]
                value = await fetcher()
                await self.set(key, value, ttl)
                return value
        else:
            value = await fetcher()
            await self.set(key, value, ttl)
            return value
    
    def _set_local(self, key: str, value: Any, ttl: int) -> None:
        while len(self._local) >= self._config.local_max_size:
            self._local.popitem(last=False)
        self._local[key] = (value, time.monotonic() + ttl)
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching pattern."""
        # Clear local matching keys
        to_delete = [k for k in self._local if pattern in k]
        for k in to_delete:
            del self._local[k]
        
        # Clear Redis matching keys
        try:
            keys = await self._redis.keys(self._config.key_prefix + pattern)
            if keys:
                await self._redis.delete(*keys)
        except Exception:
            pass
```

### 4.3 Message Queue with Ordering Guarantees

```python
"""Message queue with per-key ordering (like Kafka per-partition)."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrderedMessageQueue:
    """Process messages with ordering guarantees per partition key.
    
    Battle Scar: Обработка событий одного user_id разными воркерами
    приводила к race condition (заказ → оплата приходили в разном порядке).
    С ordered queue — гарантия per-key ordering.
    """
    
    workers: int = 5
    max_queue_size: int = 1000
    _queues: dict[str, asyncio.Queue] = field(default_factory=dict, init=False)
    _workers: dict[str, asyncio.Task] = field(default_factory=dict, init=False)
    
    async def start(self, handler: Callable[[str, Any], Awaitable[None]]) -> None:
        """Start processing messages."""
        pass  # Each partition has its own queue+worker
    
    async def publish(self, key: str, message: Any) -> None:
        """Publish message to ordered queue."""
        if key not in self._queues:
            self._queues[key] = asyncio.Queue(maxsize=self.max_queue_size)
        await self._queues[key].put(message)
    
    async def _process_partition(
        self,
        key: str,
        handler: Callable[[str, Any], Awaitable[None]],
    ) -> None:
        queue = self._queues[key]
        while True:
            message = await queue.get()
            try:
                await handler(key, message)
            except Exception as e:
                logger.error(f"Error processing {key}: {e}")
                # Re-queue for retry
                await asyncio.sleep(1)
                await queue.put(message)
            finally:
                queue.task_done()
```

### 4.4 Event Bus (In-process Pub/Sub)

```python
"""In-process event bus for domain events."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    name: str
    data: Any
    correlation_id: str = ""
    timestamp: float = 0.0


class EventBus:
    """Domain event bus with async handlers.
    
    Используется для: Event-Driven Architecture внутри сервиса,
    CQRS command handlers, Domain Events (DDD).
    """
    
    def __init__(self):
        self._handlers: dict[str, list[Callable[[Event], Awaitable[None]]]] = defaultdict(list)
        self._middleware: list[Callable] = []
    
    def register(self, event_name: str, handler: Callable[[Event], Awaitable[None]]) -> None:
        self._handlers[event_name].append(handler)
    
    def use(self, middleware: Callable) -> None:
        self._middleware.append(middleware)
    
    async def publish(self, event: Event) -> None:
        """Publish event to all registered handlers."""
        for middleware in self._middleware:
            middleware(event)
        
        handlers = self._handlers.get(event.name, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {event.name}: {e}")
    
    async def publish_all(self, events: list[Event]) -> None:
        for event in events:
            await self.publish(event)
```

## 5. API Design Patterns

### 5.1 Idempotency Key

```python
"""Idempotency support for payment-like APIs."""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class IdempotencyStore:
    """Store for idempotency keys.
    
    Battle Scar: Клиент отправил запрос на оплату дважды (TCP retry).
    Без idempotency — двойной charge. С ключом — второй запрос вернул 
    оригинальный результат.
    """
    
    def __init__(self, redis_client: Any, ttl: int = 86400):
        self._redis = redis_client
        self._ttl = ttl
    
    async def get_or_process(
        self,
        key: str,
        processor: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Get existing result or process and store."""
        # Check if already processed
        existing = await self._redis.get(f"idempotent:{key}")
        if existing:
            return json.loads(existing)
        
        # Process and store
        result = await processor()
        await self._redis.set(
            f"idempotent:{key}",
            json.dumps(result),
            expire=self._ttl,
        )
        return result
    
    def make_key(self, method: str, path: str, body: dict) -> str:
        """Create deterministic key from request."""
        content = f"{method}:{path}:{json.dumps(body, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
```

### 5.2 Pagination (Cursor-based)

```python
"""Cursor-based pagination — production standard."""
from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass
class CursorPage(Generic[T]):
    items: list[T]
    cursor: str | None  # Next page cursor
    has_more: bool
    total: int | None = None


class CursorPagination:
    """Cursor-based pagination.
    
    Почему не offset: offset смещается при вставке, 
    дубли/пропуски записей. Cursor — стабилен.
    """
    
    @staticmethod
    def encode_cursor(values: dict[str, Any]) -> str:
        return base64.urlsafe_b64encode(
            json.dumps(values).encode()
        ).decode()
    
    @staticmethod
    def decode_cursor(cursor: str) -> dict[str, Any]:
        return json.loads(
            base64.urlsafe_b64decode(cursor.encode())
        )
    
    @staticmethod
    def build_query(
        table: str,
        columns: list[str],
        cursor: str | None = None,
        cursor_column: str = "id",
        limit: int = 50,
        where: str | None = None,
    ) -> tuple[str, list[Any]]:
        """Build SQL query with cursor."""
        params: list[Any] = []
        
        query = f"SELECT {', '.join(columns)} FROM {table}"
        
        conditions: list[str] = []
        if where:
            conditions.append(f"({where})")
        
        if cursor:
            cursor_val = CursorPagination.decode_cursor(cursor)
            conditions.append(f"{cursor_column} > %s")
            params.append(cursor_val[cursor_column])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += f" ORDER BY {cursor_column} ASC"
        query += f" LIMIT %s"
        params.append(limit + 1)  # +1 to detect has_more
        
        return query, params
```

### 5.3 API Versioning Strategy

```text
API Versioning:
  URL:      /v1/users, /v2/users
  Header:   Accept: application/vnd.api+json;version=2
  Query:    /users?version=2

Рекомендация: URL versioning — просто, наглядно, легко routing.

Когда менять версию:
  - Изменение полей (remove/rename)
  - Изменение поведения (breaking change)
  - Изменение формата ошибок

Когда НЕ менять:
  - Добавление полей (клиенты их просто игнорируют)
  - Исправление багов
  - Оптимизация производительности

Compatibility policy:
  - v1 → v2: минимум 6 месяцев overlap
  - Deprecation notice: за 3 месяца до удаления
  - Sunset header: Warning: 299 api/v1 will be removed on 2025-01-01
```

### 5.4 Rate Limiting Headers

```python
"""Standard rate limiting headers (RFC 6585)."""
from dataclasses import dataclass


@dataclass
class RateLimitHeaders:
    """Rate limit HTTP headers."""
    limit: int       # X-RateLimit-Limit
    remaining: int   # X-RateLimit-Remaining
    reset: int       # X-RateLimit-Reset (Unix timestamp)
    
    def to_headers(self) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(self.reset),
            "Retry-After": str(max(0, self.reset - int(time.time()))),
        }
```

## 6. Data Intensive Applications

### 6.1 Batch Processing Pipeline

```python
"""Batch processing with checkpointing and recovery."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BatchProcessor:
    """Process items in batches with checkpoint recovery.
    
    Battle Scar: Пайплайн обработки 10M записей падал на 80%.
    Без checkpoint — старт с начала. С checkpoint — продолжение с 80%.
    """
    
    batch_size: int = 1000
    checkpoint_key: str = "batch:checkpoint"
    
    async def process(
        self,
        items: list[Any],
        processor: Callable[[list[Any]], Awaitable[None]],
    ) -> int:
        """Process items in batches, checkpointing after each."""
        checkpoint = await self._get_checkpoint()
        start_idx = checkpoint or 0
        
        processed = 0
        for i in range(start_idx, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            for attempt in range(3):
                try:
                    await processor(batch)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(10)
            
            await self._save_checkpoint(i + len(batch))
            processed += len(batch)
            
            logger.info(f"Processed {processed}/{len(items)}")
        
        await self._clear_checkpoint()
        return processed
```

### 6.2 Change Data Capture (CDC) Pattern

```python
"""CDC — capture database changes to event bus."""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ChangeType(Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class ChangeEvent:
    table: str
    change_type: ChangeType
    old_data: dict[str, Any] | None
    new_data: dict[str, Any] | None
    timestamp: float


class CDCProcessor:
    """Process database changes.
    
    Использование: синхронизация search index, 
    инвалидация кэша, обновление read models (CQRS).
    """
    
    async def handle_change(self, event: ChangeEvent) -> None:
        match (event.table, event.change_type):
            case ("users", ChangeType.UPDATE):
                await self.search_index.update_user(event.new_data)
                await self.cache.invalidate(f"user:{event.new_data['id']}")
            case ("orders", ChangeType.INSERT):
                await self.analytics.track_order(event.new_data)
                await self.notification.send_order_confirmation(event.new_data)
            case ("products", ChangeType.DELETE):
                await self.search_index.remove_product(event.old_data['id'])
                await self.cache.invalidate(f"product:{event.old_data['id']}")

```

## 7. Monitoring & Observability Patterns

### 7.1 Structured Logging

```python
"""Structured logging with context propagation."""
from __future__ import annotations

import json
import logging
import sys
import time
from collections.abc import MutableMapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any


# Context propagation via ContextVar (Python 3.7+)
_request_id: ContextVar[str] = ContextVar("request_id", default="")
_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_user_id: ContextVar[str] = ContextVar("user_id", default="")


def set_request_context(request_id: str, trace_id: str = "", user_id: str = "") -> None:
    _request_id.set(request_id)
    if trace_id:
        _trace_id.set(trace_id)
    if user_id:
        _user_id.set(user_id)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for machine-readable logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": _request_id.get(),
            "trace_id": _trace_id.get(),
            "user_id": _user_id.get(),
        }
        
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry, default=str)


def setup_json_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=getattr(logging, level), handlers=[handler])
```

### 7.2 Metrics Collection

```python
"""Application metrics for Prometheus."""
from dataclasses import dataclass, field
from typing import Any


class MetricsRegistry:
    """In-process metrics registry.
    
    Collect: Prometheus + Grafana
    Alerts:  Prometheus AlertManager
    """
    
    def __init__(self):
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
    
    def increment(self, name: str, labels: dict | None = None, value: int = 1) -> None:
        key = self._label_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value
    
    def gauge(self, name: str, value: float, labels: dict | None = None) -> None:
        key = self._label_key(name, labels)
        self._gauges[key] = value
    
    def observe(self, name: str, value: float, labels: dict | None = None) -> None:
        key = self._label_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
    
    def _label_key(self, name: str, labels: dict | None) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"


# Key metrics per service:
METRICS = {
    "http_requests_total": "Total HTTP requests",
    "http_request_duration_seconds": "Request latency",
    "http_requests_in_flight": "Current in-flight requests",
    "db_connections_active": "Active DB connections",
    "db_queries_total": "Total database queries",
    "db_query_duration_seconds": "Query latency",
    "cache_hit_ratio": "Cache hit ratio",
    "queue_depth": "Message queue depth",
    "queue_processing_time": "Message processing latency",
    "errors_total": "Total errors by type",
}
```

### 7.3 Structured Error Response

```python
"""Standard error response format (RFC 7807 Problem Details)."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProblemDetail:
    """RFC 7807 Problem Details for HTTP APIs."""
    type: str = "about:blank"
    title: str = ""
    status: int = 500
    detail: str = ""
    instance: str = ""
    extra: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        result = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }
        if self.instance:
            result["instance"] = self.instance
        result.update(self.extra)
        return result


# Common problem types:
ERRORS = {
    "validation": ProblemDetail(
        type="https://api.example.com/errors/validation",
        title="Validation Error",
        status=422,
    ),
    "not_found": ProblemDetail(
        type="https://api.example.com/errors/not-found",
        title="Resource Not Found",
        status=404,
    ),
    "rate_limited": ProblemDetail(
        type="https://api.example.com/errors/rate-limited",
        title="Rate Limited",
        status=429,
    ),
}
```

## 8. Database Scaling Patterns

### 8.1 Read Replicas

```python
"""Read/write splitting with read replicas."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatabaseRouter:
    """Route queries to appropriate database.
    
    Writes → Primary
    Reads → Replica (eventually consistent)
    Critical reads → Primary (strong consistency)
    """
    
    primary: Any
    replicas: list[Any]
    
    async def execute_write(self, query: str, *params) -> Any:
        return await self.primary.execute(query, params)
    
    async def execute_read(self, query: str, *params, 
                           strong_consistency: bool = False) -> Any:
        if strong_consistency:
            return await self.primary.execute(query, params)
        replica = random.choice(self.replicas)
        return await replica.execute(query, params)
```

### 8.2 Sharding

```python
"""Application-level sharding."""
import hashlib


class ShardManager:
    """Consistent hashing-based shard manager.
    
    Shard key → hash ring → shard → database.
    """
    
    def __init__(self, shards: list[str]):
        self._shards = shards
        self._ring = self._build_ring()
    
    def _build_ring(self) -> dict[int, str]:
        ring = {}
        for i, shard in enumerate(self._shards):
            for j in range(100):  # Virtual nodes
                key = hashlib.md5(f"{shard}:{j}".encode()).hexdigest()
                ring[int(key[:8], 16)] = shard
        return dict(sorted(ring.items()))
    
    def get_shard(self, key: str) -> str:
        hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
        for ring_key in sorted(self._ring.keys()):
            if hash_val <= ring_key:
                return self._ring[ring_key]
        return self._ring[sorted(self._ring.keys())[0]]
```

## 9. Security Patterns

### 9.1 JWT Authentication

```python
"""Secure JWT implementation."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
from typing import Any


@dataclass
class JWTConfig:
    secret_key: str
    algorithm: str = "HS256"
    access_token_ttl: int = 900       # 15 minutes
    refresh_token_ttl: int = 2592000  # 30 days
    issuer: str = "https://api.example.com"


class JWTHandler:
    """JWT token management.
    
    Battle Scar: Long-lived JWT (30 days) без refresh механизма.
    При утечке токена — доступ на 30 дней. 
    С short-lived access + refresh — окно уязвимости 15 минут.
    """
    
    def __init__(self, config: JWTConfig):
        self._config = config
    
    def create_access_token(self, user_id: str, claims: dict | None = None) -> str:
        payload = {
            "sub": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=self._config.access_token_ttl),
            "iss": self._config.issuer,
            "type": "access",
        }
        if claims:
            payload.update(claims)
        return jwt.encode(payload, self._config.secret_key, algorithm=self._config.algorithm)
    
    def verify_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._config.secret_key,
            algorithms=[self._config.algorithm],
            issuer=self._config.issuer,
        )
```

## 10. Cost & Capacity Planning

### 10.1 Capacity Estimation Formulas

```python
# Daily active users (DAU) estimation:
def estimate_dau(total_users: int, engagement_pct: float = 0.3) -> int:
    return int(total_users * engagement_pct)

# Peak RPS (requests per second):
def estimate_peak_rps(dau: int, requests_per_user: int = 10, peak_factor: float = 5.0) -> int:
    avg_rps = (dau * requests_per_user) / 86400
    return int(avg_rps * peak_factor)

# Storage needed:
def estimate_storage(
    records_per_day: int,
    record_size_bytes: int,
    retention_days: int = 90,
    replication_factor: int = 3,
) -> str:
    daily = records_per_day * record_size_bytes
    total = daily * retention_days * replication_factor
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if total < 1024:
            return f"{total:.1f} {unit}"
        total /= 1024
    return f"{total:.1f} EB"

# Cost estimation (AWS):
AWS_COST = {
    "rds_postgres": {"per_gb_month": 0.115, "per_vcpu_hour": 0.14},
    "ec2": {"per_vcpu_hour": 0.05, "per_gb_ram": 0.007},
    "elasticache_redis": {"per_gb_month": 0.125, "per_vcpu_hour": 0.10},
    "msk_kafka": {"per_broker_hour": 0.21, "per_gb_storage": 0.10},
    "s3": {"per_gb_month": 0.023},
}

def estimate_monthly_cost(db_size_gb: int, compute_vcpu: int, compute_ram_gb: int) -> dict:
    return {
        "database": db_size_gb * AWS_COST["rds_postgres"]["per_gb_month"] + 
                    compute_vcpu * AWS_COST["rds_postgres"]["per_vcpu_hour"] * 730,
        "compute": compute_vcpu * AWS_COST["ec2"]["per_vcpu_hour"] * 730 +
                   compute_ram_gb * AWS_COST["ec2"]["per_gb_ram"] * 730,
    }
```

## 11. Real-World System Designs

### 11.1 URL Shortener (bit.ly/tinyurl)

```text
Requirements:
  - 100M URLs created/month
  - 10B redirects/month
  - p99 latency < 10ms
  - 99.99% availability

Design:
  - Pre-generate keys (base62, 7 chars = 3.5T combinations)
  - Write: Apache Kafka → batch to PostgreSQL
  - Read: Redis cache (LRU, TTL 24h) → PostgreSQL fallback
  - Redirect: 301 (permanent) or 302 (analytics)
  - Analytics: Kafka → ClickHouse

Scaling:
  - Writes: 38/sec → 1 partition enough
  - Reads: 3800/sec → cache 99% hit rate → 38/sec to DB
  - Storage: 10B × 500 bytes = 5TB → shard by hash
```

### 11.2 Chat System (WhatsApp/Discord)

```text
Requirements:
  - 500M MAU
  - 50B messages/day
  - Real-time delivery (< 100ms)
  - Multi-device sync

Design:
  - WebSocket for real-time (long-lived connections)
  - Message storage: Cassandra (time-series optimized)
  - Presence: Redis (TTL-based)
  - Push notifications: Firebase/APNs
  - Attachments: S3/CDN
  
Key challenges:
  - Message ordering: per-conversation sequence number
  - Read receipts: async, eventual consistency
  - Online/offline: heartbeat каждые 30 секунд
  - Multi-device: conflict resolution (last-write-wins)
```

### 11.3 Payment System (Stripe/Adyen)

```text
Requirements:
  - 99.999% consistency (no lost payments)
  - 10K transactions/sec
  - Dual-writes to multiple providers
  - Compliance (PCI-DSS, GDPR)

Design:
  - Idempotency key on all writes
  - State machine: created → processing → captured/failed → refunded
  - Dual-write: primary + fallback provider
  - Reconciliation: daily batch job matching
  - Audit log: immutable event store
  
Key patterns:
  - Outbox pattern: write to DB → publish event → async processing
  - Saga for multi-step payments
  - Dead letter queue for failed payments
```

### 11.4 Rate Limiter (Cloudflare/API Gateway)

```text
Requirements:
  - 1M+ rules
  - 50K requests/sec/node
  - p99 latency < 1ms per check
  - Distributed consistency

Algorithm (Sliding Window Log):
  - Per user_id + endpoint, store timestamp list
  - Clean expired timestamps
  - Count requests in window
  - Throttle if over limit

Optimization:
  - Local cache + Redis backend
  - Lazy cleanup (clean only on read)
  - Async replication between datacenters
  - Bloom filter for known-good keys
```

## 12. Real World Complexity Analysis

### Проект: E-commerce Platform Migration

```text
Monolith → Microservices (200 services, 2 years)

Фазы:
  Phase 0 (M0-M3): Infrastructure + CI/CD
  Phase 1 (M3-M6): Extract read path (catalog, search)
  Phase 2 (M6-M12): Extract write path (cart, checkout)
  Phase 3 (M12-M18): Payment + order management
  Phase 4 (M18-M24): Monolith decommission

Результаты:
  + Deploy frequency: weekly → 50x/day
  + MTTR: 4 hours → 15 minutes
  + Team autonomy: 1 team → 20 teams
  - Complexity: significantly higher
  - Cost: +40% infrastructure
  - Needed: service mesh, observability, chaos engineering

Вывод: Microservices — это цена, которую платишь за autonomy.
Если нет проблемы с scaling team — монолит лучше.
```

### Проект: Real-time Analytics Platform

```text
Requirements: 1B events/day, p99 query < 1s

Stack:
  - Ingestion: Kafka (100 partitions)
  - Stream: Flink (windowed aggregations)
  - Storage: ClickHouse (columnar, materialized views)
  - Serving: Redis (hot data) + ClickHouse (cold data)
  - Dashboard: Grafana + custom React

Results:
  - Throughput: 50K events/sec → 2M events/sec
  - Query latency: 30s → 200ms
  - Cost: $200K/month → $45K/month (ClickHouse compression)
  - Data: 5TB/day → 500GB/day (after compression)

Key lessons:
  - OLAP vs OLTP: разные БД для разных задач
  - Columnar storage: 10x compression, 100x query speed
  - Materialized views: pre-compute aggregates
  - Hot/warm/cold tiers: оптимизация cost/performance
```

## 13. Architectural Decision Records

### ADR Template

```markdown
# ADR-NNN: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[Problem description, constraints, forces]

## Decision
[What we decided]

## Consequences
[Positive and negative outcomes]

## Alternatives Considered
[Other options and why not chosen]

## References
[Links to docs, RFCs, PRs]
```

### ADR Examples

```markdown
# ADR-001: Use PostgreSQL over MongoDB for Order Service

## Status: Accepted

## Context
Order service needs ACID transactions, complex queries (joins),
and strong consistency. Team has PostgreSQL experience.

## Decision
Use PostgreSQL 16 with connection pooling (PgBouncer).

## Consequences
+ ACID compliance
+ Rich query capabilities  
+ Known operational expertise
- Vertical scaling limits
- Manual sharding needed at > 10TB

## Alternatives
MongoDB: flexible schema, but no ACID across documents
CockroachDB: too complex for current team size

# ADR-002: Kafka for Event Bus (not RabbitMQ)

## Status: Accepted

## Context
Need event sourcing, replay capability, and 100K msg/s throughput.

## Decision
Kafka with 24 partitions, 3x replication, Schema Registry.

## Consequences
+ Event replay
+ High throughput
+ Long retention
- Higher latency than RabbitMQ
- More complex operations

## Alternatives
RabbitMQ: better for task distribution, but no replay
Redis Streams: smaller operational overhead, but less durable
```


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
