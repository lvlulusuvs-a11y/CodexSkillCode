# Структурированное логирование: что, куда, зачем

Я перестал использовать print() лет 10 назад. И голые logging.info() - тоже лет 5 назад. Structured logs - единственный правильный формат.

## Плохо: текстовые логи

```
[2026-05-31 12:00:00] INFO: Order created for user 123
[2026-05-31 12:00:01] INFO: Payment processed for order 456
[2026-05-31 12:00:02] ERROR: Database connection failed
```

Попробуй найти все заказы пользователя 123 в таком формате. Или посчитать ошибки за 5 минут. Или построить дашборд.

## Хорошо: JSON логи

```json
{"level":"INFO","time":"2026-05-31T12:00:00Z","message":"Order created","order_id":"ord_456","user_id":"usr_123","total":49.99,"currency":"USD","duration_ms":150}
{"level":"ERROR","time":"2026-05-31T12:00:01Z","message":"Payment failed","order_id":"ord_456","error_code":"card_declined","attempt":2,"service":"stripe"}
{"level":"WARN","time":"2026-05-31T12:00:02Z","message":"Database pool exhausted","pool_used":20,"pool_max":20,"waiters":5}
```

Теперь могу:
- `grep "user_id":"usr_123""` - найти все действия пользователя
- Считать количество ошибок в Grafana/Loki
- Строить дашборды по длительности операций
- Искать correlation между событиями

## Как я логирую

```python
import structlog
from datetime import datetime, timezone

# Настройка структурированного логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Использование
async def create_order(user_id: str, items: list[dict]) -> Order:
    log = logger.bind(user_id=user_id)

    try:
        order = await order_service.create(user_id, items)
        log.info("order_created",
            order_id=order.id,
            total=str(order.total),
            items_count=len(items),
            duration_ms=(datetime.now(timezone.utc) - order.created_at).total_seconds() * 1000,
        )
        return order
    except PaymentError as e:
        log.error("payment_failed",
            error_code=e.code,
            error_detail=str(e),
            items_count=len(items),
        )
        raise
    except Exception as e:
        log.critical("unexpected_error", error=str(e), exc_info=True)
        raise
```

## Что логировать

### Обязательно
- Каждый вход и выход из сервиса (HTTP request/response)
- Каждый external call (куда, сколько длилось, ошибка)
- Каждая бизнес-операция (order_created, payment_processed)
- Каждая ошибка (код, контекст, stacktrace)

### Никогда
- Пароли, токены, ключи
- Персональные данные (имя, email, телефон)
- Данные кредитных карт
- Тела запросов целиком (только summary)

## Correlation ID

Каждый запрос получает уникальный ID, который пробрасывается через все сервисы:

```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id")

class RequestIdMiddleware:
    async def __call__(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_var.set(request_id)
        with structlog.contextvars.bind_contextvars(request_id=request_id):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
```

Теперь один request_id пробегает через все сервисы. Можно соединить логи разных сервисов в одну историю.

## Мои уровни логирования

- **DEBUG**: детали для разработки (не включать в production)
- **INFO**: бизнес-события (order_created, user_registered)
- **WARN**: аномалии которые не ломают систему (retry, cache miss, degraded performance)
- **ERROR**: ошибки которые влияют на одного пользователя (payment declined)
- **CRITICAL**: системные ошибки (DB down, out of memory, circuit breaker open)


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

