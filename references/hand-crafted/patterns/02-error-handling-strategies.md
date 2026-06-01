# Error Handling: Как не потерять ошибку

Я видел код, где ошибки глотаются. Видел код, где try/except оборачивает 200 строк. Видел код, где ошибки пробрасываются через 10 уровней без контекста. Вот что я реально делаю.

## Иерархия ошибок - мой скелет

Я создаю свою иерархию исключений. Каждое несёт контекст: что, где, почему.

```python
class AppError(Exception):
    """Базовое исключение приложения."""
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, entity: str, id: str):
        super().__init__(f"{entity} not found: {id}", "NOT_FOUND")

class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(f"Validation failed: {field} - {reason}", "VALIDATION")

class ExternalServiceError(AppError):
    def __init__(self, service: str, status: int, detail: str):
        super().__init__(f"{service} returned {status}: {detail}", "EXTERNAL_ERROR")
```

## Где ловить

Каждый уровень ловит свои ошибки и трансформирует их:

- Repository -> ошибки БД -> ExternalServiceError
- Service -> бизнес-ошибки -> NotFoundError, ValidationError
- Handler -> HTTP response -> JSON c status code

```python
class UserService:
    async def get_user_profile(self, user_id: str) -> UserProfile:
        user = await self.repo.get_by_id(user_id)
        try:
            orders = await self.order_service.get_user_orders(user_id)
        except ExternalServiceError:
            orders = []
            logger.warning("Failed to fetch orders for %s", user_id)
        return UserProfile(user=user, orders=orders)
```

## Три правила обработки

### 1. Не глотай ошибки
```python
# АД: ошибка проглочена, мы не узнаем что случилось
try:
    result = risky_operation()
except:
    pass
```

### 2. Ошибки на границе системы
Все ошибки должны быть обработаны на границе:
- HTTP handler -> JSON response c code
- Queue consumer -> ACK/NACK
- CLI command -> exit code

### 3. Fallback лучше чем падать
```python
async def get_exchange_rate(currency: str) -> float:
    try:
        rate = await exchange_api.get_rate(currency)
        await cache.set(f"rate:{currency}", rate, ttl=300)
        return rate
    except (TimeoutError, ConnectionError) as e:
        cached = await cache.get(f"rate:{currency}")
        if cached is not None:
            return cached
        raise
```

## Чеклист

- [ ] Каждый внешний вызов в try/except
- [ ] Нет голых except:
- [ ] Нет замалчивания ошибок
- [ ] Ошибки логируются с контекстом
- [ ] Fallback есть где надо
- [ ] HTTP handler возвращает правильный status code
- [ ] Ошибки не утекают в ответ пользователю


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

