# Dependency Injection без фреймворков

В каждом втором проекте я вижу одно и то же: импорты, завязанные на конкретные реализации. Потом приходят тесты и начинается боль. DI решает это без единого фреймворка.

## Проблема: глобальные зависимости

```python
from database import db_pool  # прямой импорт
from payment_provider import stripe_client  # прямой импорт

class OrderService:
    async def create(self, order_data: dict) -> Order:
        async with db_pool.acquire() as conn:  # жёсткая связь
            order = await create_order(conn, order_data)
        await stripe_client.charge(order.total)  # жёсткая связь
        return order
```

Этот класс нельзя протестировать без БД и Stripe. Его нельзя переиспользовать с другой БД. Он умрёт в тот момент когда мы сменим платежного провайдера.

## Решение: передавай зависимости явно

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

class Database(ABC):
    @abstractmethod
    async def fetch(self, query: str, *args) -> list[dict]: ...
    @abstractmethod
    async def execute(self, query: str, *args) -> None: ...

class PaymentGateway(ABC):
    @abstractmethod
    async def charge(self, amount: Money) -> PaymentResult: ...

@dataclass
class OrderService:
    db: Database
    payment: PaymentGateway

    async def create(self, order_data: dict) -> Order:
        async with self.db.acquire() as conn:
            order = await create_order(conn, order_data)
        await self.payment.charge(order.total)
        return order
```

Теперь у меня нет зависимостей на конкретные реализации. Я могу тестировать:

```python
class FakeDB(Database):
    async def fetch(self, query, *args):
        return [{"id": 1, "total": 100}]

class FakePayment(PaymentGateway):
    async def charge(self, amount):
        return PaymentResult(success=True)

async def test_create_order():
    service = OrderService(db=FakeDB(), payment=FakePayment())
    order = await service.create({"user_id": "1"})
    assert order.id is not None
```

## Как собирать зависимости

Без фреймворка, в одном месте:

```python
# app/dependencies.py
from dataclasses import dataclass

@dataclass
class Dependencies:
    config: AppConfig
    db: Database
    cache: Cache
    payment: PaymentGateway
    order_service: OrderService
    user_service: UserService

def build_dependencies(config: AppConfig) -> Dependencies:
    db = PostgresPool(config.database_url)
    cache = RedisCache(config.redis_url)
    payment = StripeGateway(config.stripe_key)

    user_service = UserService(db=db, cache=cache)
    order_service = OrderService(db=db, payment=payment)

    return Dependencies(
        config=config,
        db=db, cache=cache, payment=payment,
        order_service=order_service,
        user_service=user_service,
    )

# В main.py
deps = build_dependencies(config)
app = create_app(deps)
```

## Что изменилось

1. Явные зависимости - видно что нужно сервису
2. Тестируемость - каждый сервис можно замокать
3. Гибкость - замена реализации не трогает код
4. Композиция - всё собирается в одном месте

DI - это не про фреймворки. Это про то чтобы передавать зависимости явно, а не доставать их из глобального контекста.


## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation



## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation

