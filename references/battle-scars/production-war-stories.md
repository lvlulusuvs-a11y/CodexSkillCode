# 🔥 Battle Scars: Production War Stories

**Реальные истории из продакшена в Big Tech. Не теория — кровь, пот и слёзы.**

---

## 1. Connection Pool: Как мы уронили прод в 3 часа ночи

### Ситуация
Python-сервис с PostgreSQL. Нагрузка выросла в 2 раза — сервис лёг.

### Что пошло не так
```python
# Было:
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)  # pool_size=5 по умолчанию
```

5 соединений в пуле. Новый трафик = очередь в пул. Время ответа: 10ms → 30s.  
Каждый новый запрос ждал соединения — queue росла бесконечно.  
Таймаут через 30 секунд → retry от клиента → ещё больше запросов.

### Что сделали
```python
# Стало:
from sqlalchemy import create_engine, QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,    # проверка здоровья перед выдачей
    pool_recycle=3600,     # пересоздание через час
    pool_timeout=5,        # не ждать дольше 5 секунд
)
```

### Что добавили потом (после 2-го инцидента)
```python
# Circuit breaker на уровне приложения
class DBCircuitBreaker:
    def __init__(self, pool):
        self.pool = pool
        self.failures = 0
        self.threshold = 5
        self.last_failure = None
        self.cooldown = 30  # секунд
    
    @asynccontextmanager
    async def acquire(self):
        if self.failures >= self.threshold:
            if time.time() - self.last_failure < self.cooldown:
                raise ServiceUnavailable("DB is down, try later")
            self.failures = 0  # half-open
        
        try:
            async with self.pool.acquire() as conn:
                yield conn
                self.failures = 0
        except Exception:
            self.failures += 1
            self.last_failure = time.time()
            raise
```

### Уроки
1. **Всегда настраивай pool** — дефолты убивают
2. **pool_pre_ping=True** — мёртвые соединения не выдаются
3. **Circuit breaker обязателен** — иначе cascade failure
4. **Мониторинг pool utilisation** — если > 80% — всё

---

## 2. Как Parse, don't Validate спас нам прод

### Ситуация
Сервис принимал User JSON с фронта. Одно поле `role: "admin"` попало не туда.

### Было
```python
def create_user(data: dict) -> User:
    # data — сырой dict, может быть что угодно
    user = User(
        name=data.get("name", ""),
        email=data.get("email", ""),
        role=data.get("role", "user"),
    )
    db.save(user)
    return user
```

### Что случилось
Фронтенд прислал `{"name": "Hacker", "email": "test@test.com", "role": "admin"}`.  
Роль не валидировалась. Получили админский доступ.

### Стало
```python
from dataclasses import dataclass
from enum import Enum
import re

class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    # ADMIN не здесь — нельзя создать из API

@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.value):
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class CreateUserCommand:
    name: str
    email: Email
    role: Role = Role.USER
    
    def __post_init__(self):
        if len(self.name) < 2:
            raise ValueError("Name too short")
        if self.role != Role.USER:  # API может создать только USER
            raise ValueError("Cannot create non-user role via API")

def create_user_handler(cmd: CreateUserCommand) -> User:
    # Команда уже валидна — parse, don't validate
    repo.save(User(name=cmd.name, email=cmd.email.value, role=cmd.role.value))
```

### Уроки
1. **Parse на границе системы** — сырые данные превращаются в типы
2. **Make illegal states unrepresentable** — `CreateUserCommand` не может быть невалидным
3. **Frozen dataclass** — иммутабельность = безопасность

---

## 3. Async vs Sync: Как мы уронили payment-сервис

### Ситуация
Payment-сервис на FastAPI + asyncpg. Под нагрузкой latency p50 был 50ms, но p99 — 30 секунд.

### Расследование
```python
# Проблема: блокирующий вызов в async функции
@app.post("/charge")
async def charge(amount: int, repo=Depends(get_repo)):
    user = await repo.get_user(...)
    # ⚠️ БЛОКАДА!
    fraud_score = fraud_check(user)  # sync библиотека — CPU-bound
    # 🚨 Вся event loop заблокирован на 2 секунды
    result = await payment_gateway.charge(amount)
    return result
```

### Почему это больно
`fraud_check()` — синхронная функция, которая выполняет ML inference 2 секунды.  
Весь async event loop заблокирован на это время.  
100 запросов = 200 секунд очереди.

### Решение
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)

@app.post("/charge")
async def charge(amount: int, repo=Depends(get_repo)):
    user = await repo.get_user(...)
    
    # ✅ CPU-bound в thread pool
    loop = asyncio.get_event_loop()
    fraud_score = await loop.run_in_executor(
        _executor, fraud_check, user
    )
    
    result = await payment_gateway.charge(amount)
    return result
```

### Уроки
1. **Async не магия** — CPU-bound блокирует event loop
2. **Знай свои зависимости** — если библиотека sync, не вызывай её в async
3. **ThreadPoolExecutor для CPU-bound**, asyncio для I/O-bound
4. **Мониторинг event loop delay** — если > 100ms, ты в беде

---

## 4. Retry Storm: Как 3 микросервиса убили друг друга

### Ситуация
Service A → Service B → Service C. B упал на 30 секунд.

### Каскад
1. B упал → A получил 503 → retry через 100ms
2. 100 клиентов × retry × 10 попыток = 1000 запросов в секунду на A
3. A лёг от нагрузки → C тоже лёг
4. 3 сервиса мертвы. Полный downtime.

### Почему
```python
# В каждом сервисе:
@retry(stop=stop_after_attempt(10), wait=wait_fixed(0.1))
def call_downstream():
    ...
```

### Фикс
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

@retry(
    stop=stop_after_attempt(3),        # максимум 3 попытки
    wait=wait_exponential(multiplier=1, min=1, max=30),  # 1s, 2s, 4s...
    retry=retry_if_exception(lambda e: isinstance(e, TransientError)),
)
def call_downstream():
    ...

# + Jitter чтобы запросы не приходили одновременно
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=30) + wait_random(0, 1),
)
def call_with_jitter():
    ...
```

### Уроки
1. **Retry — с exponential backoff, не fixed**
2. **Jitter обязателен** — иначе все ретраят одновременно
3. **Не retry NonRetryableError** — 404 не станет 200
4. **Stochastic retry** — randomize delays
5. **Circuit breaker на upstream** — не посылать запросы мёртвому сервису

---

## 5. Memory Leak: Как 200GB RAM исчезли за ночь

### Ситуация
Сервис обрабатывал события из Kafka. После деплоя память росла линейно.

### Расследование
```python
class EventProcessor:
    def __init__(self):
        self.cache = {}  # ❌ бесконечный кэш
    
    async def process(self, event):
        # Сохраняем все события в памяти
        self.cache[event.id] = event
        # Никогда не чистим
        result = await do_work(event)
        return result
```

Через 6 часов: 200GB, OOM, pod restart.  
После restart: снова 6 часов до OOM.

### Решение
```python
from collections import OrderedDict
import time

class LRUCache:
    def __init__(self, max_size: int = 10000, ttl: int = 3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key: str):
        if key not in self.cache:
            return None
        value, ts = self.cache[key]
        if time.time() - ts > self.ttl:
            del self.cache[key]
            return None
        self.cache.move_to_end(key)
        return value
    
    def set(self, key: str, value):
        self.cache[key] = (value, time.time())
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
```

### Уроки
1. **Любой dict — потенциальная утечка**, если не чистить
2. **Memory profiler обязателен** при деплое новых фич
3. **LRU + TTL** — стандартное решение
4. **Limit для кэша** — не бывает бесконечной памяти

---

## 6. Database Deadlock: Как один `SELECT FOR UPDATE` положил всё

### Ситуация
PostgreSQL сервис. Под нагрузкой — 50% запросов падали с deadlock.

### Почему
```sql
-- Транзакция 1:
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
SELECT * FROM accounts WHERE id = 2 FOR UPDATE;
-- ОБНОВИТЬ
COMMIT;

-- Транзакция 2:
BEGIN;
SELECT * FROM accounts WHERE id = 2 FOR UPDATE;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Deadlock! Т1 ждёт 2, Т2 ждёт 1
```

### Решение
```python
def transfer(from_id: int, to_id: int, amount: Decimal):
    # ✅ Всегда блокировать в одном порядке
    first, second = sorted([from_id, to_id])
    
    async with db.transaction():
        row1 = await db.fetch(f"SELECT * FROM accounts WHERE id = {first} FOR UPDATE")
        row2 = await db.fetch(f"SELECT * FROM accounts WHERE id = {second} FOR UPDATE")
        # safely update
```

### Уроки
1. **Всегда lock в одинаковом порядке** — сортируй ID
2. **Keep transactions short** — чем дольше lock, тем больше шанс deadlock
3. **Deadlock detection** — PostgreSQL детектит и отменяет транзакцию
4. **Retry on deadlock** — приложение должно быть готово к этому

---

## 7. Configuration Drift: 3 окружения, 3 разных поведения

### Ситуация
Баг на проде, который не воспроизводился на staging.

### Почему
```yaml
# prod:
DB_POOL_SIZE: 20
DB_TIMEOUT: 5

# staging:
DB_POOL_SIZE: 5
DB_TIMEOUT: 30

# dev:
DB_POOL_SIZE: 2
DB_TIMEOUT: 60
```

Staging работал с pool_size=5, timeout=30. Прод с pool_size=20, timeout=5.  
На проде при пиковой нагрузке пул исчерпывался за 2 секунды — timeout 5 секунд не спасал.

### Решение
```yaml
# Всегда одинаковые параметры, разные только ресурсы
# prod:
DB_POOL_SIZE: 20
DB_TIMEOUT: 10
DB_MAX_OVERFLOW: 10

# staging:
DB_POOL_SIZE: 20
DB_TIMEOUT: 10
DB_MAX_OVERFLOW: 10

# dev:
DB_POOL_SIZE: 5
DB_TIMEOUT: 30
DB_MAX_OVERFLOW: 3
```

### Уроки
1. **Staging = prod по конфигурации** (уменьшаются только ресурсы)
2. **Infrastructure as Code** — все конфиги в git
3. **Drift detection** — оповещение о расхождении конфигов
4. **Canary deploy** — сначала 1% трафика, потом 100%

---

## 8. Timeout: Как мы отключали сервисы в неправильном порядке

### Ситуация
Graceful shutdown. Сервис завершался, но терял запросы.

### Проблема
```python
# Порядок shutdown:
# 1. Закрыть HTTP сервер (новые запросы не принимаются)
# 2. Закрыть DB pool
# 3. Закрыть Kafka consumer

# ⚠️ Проблема: Kafka consumer держит handler, который использует DB
# После закрытия DB — handler падает
```

### Решение
```python
GRACEFUL_SHUTDOWN_ORDER = {
    "health_check": 0,    # 1. перестать отвечать 200
    "load_balancer": 1,   # 2. deregister из LB
    "http_server": 5,     # 3. закрыть HTTP (ждать 5s)
    "kafka_consumer": 10, # 4. consumer ещё может отправлять в DLQ
    "db_pool": 15,        # 5. DB закрываем последним — может понадобиться
    "cache": 16,          # 6. Redis
}
```

### Уроки
1. **Порядок shutdown важен** — зависимости закрываются в обратном порядке
2. **Grace period должен быть достаточно долгим** — 60 секунд минимум
3. **Health check должен показывать draining** — LB не шлёт трафик

---

## 📊 Статистика: что убивает продакшен

| Причина | Частота | Влияние | 
|---------|---------|---------|
| Connection pool exhaustion | 25% | Высокое |
| Missing timeout | 20% | Среднее |
| Memory leak | 15% | Высокое |
| Retry storm | 12% | Критическое |
| Configuration drift | 10% | Среднее |
| Deadlock | 8% | Критическое |
| Async blocking call | 5% | Высокое |
| Other | 5% | Разное |

**Вывод:** 80% инцидентов — это базовые паттерны, которые можно предотвратить код-ревью и правильными инструментами.


---

## 9. How We Lost $50K in One Hour (Caching Gone Wrong)

### Ситуация
E-commerce flash sale. 100K concurrent users. Cache was too aggressive.

### Что пошло не так
```python
# Cache with 1 hour TTL for ALL products
@lru_cache(maxsize=10000)
def get_product_price(product_id: int) -> float:
    return db.fetch_one("SELECT price FROM products WHERE id = ?", [product_id])
```

Prices changed during flash sale, but cache returned stale prices for 1 hour.  
Customers bought at old prices. $50K revenue loss.

### Что сделали
```python
# Short TTL + cache invalidation on update
from datetime import timedelta

class ProductCache:
    def __init__(self, redis):
        self.redis = redis
    
    async def get_price(self, product_id: int) -> float:
        cached = await self.redis.get(f"price:{product_id}")
        if cached:
            return float(cached)
        
        price = await db.fetch_val("SELECT price FROM products WHERE id = ?", [product_id])
        
        # Short TTL for products on sale
        ttl = 60 if self._is_on_sale(product_id) else 3600
        await self.redis.setex(f"price:{product_id}", ttl, price)
        return price
    
    async def invalidate_price(self, product_id: int) -> None:
        """Invalidate cache on price update."""
        await self.redis.delete(f"price:{product_id}")
```

### Уроки
1. **Cache invalidation is hard** — one of the 2 hard problems in CS
2. **Know your data** — different data needs different TTLs
3. **Cache is not a silver bullet** — sometimes you need fresh data
4. **Monitor cache hit ratio** — if it's 100%, something is wrong

## 10. The Great Dependency Upgrade (Breaking Changes)

### Ситуация
Major library dependency had a CVE. "Quick upgrade" turned into 3-day nightmare.

### Что пошло не так
- Library v2 → v3 changed 15 public APIs
- 47 files needed changes (not the 5 we estimated)
- Tests caught 89 compilation errors
- 3 teams had to coordinate

### Что сделали
```python
# Adapter pattern to isolate dependency changes
class ExternalSDKAdapter:
    """Adapter between our code and external SDK.
    
    When SDK changes, only this file changes.
    Everything else is protected by the interface.
    """
    
    def __init__(self):
        self._client = ExternalSDKv3.Client(
            api_key=settings.SDK_KEY,
            timeout=10,
            retries=3,
        )
    
    async def create_payment(self, amount: int, currency: str) -> PaymentResult:
        # Translate between SDK v3 and our interface
        result = await self._client.charge(
            amount_cents=amount,
            currency_code=currency,
        )
        return PaymentResult(
            id=result.transaction_id,
            amount=result.amount,
            status="completed" if result.success else "failed",
        )
```

### Уроки
1. **Adapter/anti-corruption layer** is worth the investment
2. **Always estimate migration time × 3** for dependency upgrades
3. **Lock versions** — never use `>=` in requirements
4. **Test the upgrade in isolation** before committing

## 11. Dead Letter Queue to the Rescue

### Ситуация
Kafka consumer failed to process 5% of messages silently.

### Что пошло не так
```python
# Silent failure — messages just disappeared
async def process_order(msg):
    try:
        data = json.loads(msg.value)
        await create_order(data)
    except Exception:
        pass  # Bad! Error swallowed
```

### Что сделали
```python
class KafkaConsumer:
    async def process_with_dlq(self, msg):
        try:
            data = json.loads(msg.value)
            await create_order(data)
        except json.JSONDecodeError as e:
            # Non-retryable → DLQ immediately
            await self.dlq.send(
                topic="orders-dlq",
                value=msg.value,
                headers=[("error", str(e)), ("original_topic", "orders")],
            )
            await self.consumer.commit()
        except TransientError as e:
            # Retryable → retry with backoff
            for attempt in range(3):
                try:
                    await create_order(data)
                    return
                except TransientError:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
            
            # Failed after retries → DLQ
            await self.dlq.send(
                topic="orders-dlq",
                value=msg.value,
                headers=[("error", str(e)), ("retries", "3")],
            )
```

### Уроки
1. **Never swallow exceptions silently**
2. **DLQ is your safety net** for messages that can't be processed
3. **Differentiate retryable vs non-retryable errors**
4. **Monitor DLQ size** — if it grows, something's broken
