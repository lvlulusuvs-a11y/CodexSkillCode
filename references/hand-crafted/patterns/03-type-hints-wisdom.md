# Type Hints: Когда писать, когда нет

Я добавляю type hints не потому что так принято, а потому что они экономят время. Вот где они реально нужны.

## Когда я всегда пишу типы

### Публичное API

```python
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class Result(Generic[T]):
    """Кто угодно будет использовать этот класс - тут типы обязательны."""
    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        self.value = value
        self.error = error

    @property
    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error:
            raise ValueError(self.error)
        assert self.value is not None
        return self.value
```

### Функции с непонятным возвратом
```python
# Что возвращает? Список? Генератор? None?
def parse_logs(path): ...

# Ясно
def parse_logs(path: Path) -> AsyncIterator[LogEntry]: ...
```

## Когда я НЕ пишу типы

### Внутренние хелперы
```python
def _normalize(data):
    """Однострочный хелп, видно что делает."""
    return data.strip().lower()
```

### Где это Only Adds Noise
```python
# Ад: тип занимает больше строки чем сигнатура
def x(a: List[Dict[str, Union[str, int, None]]]) -> Optional[Tuple[int, ...]]: ...

# Лучше: type alias
UserData = dict[str, str | int | None]
def x(a: list[UserData]) -> tuple[int, ...] | None: ...
```

## TypeVar и Protocol

```python
T = TypeVar('T')

def first_or_default(items: Iterable[T], default: T) -> T:
    for item in items:
        return item
    return default

class CanSerialize(Protocol):
    def to_dict(self) -> dict: ...

def serialize(obj: CanSerialize) -> dict:
    return obj.to_dict()
```

Protocol - это как interface в Go. Не нужно наследовать, нужно просто иметь метод.

## Моё правило

Если type hint помогает понять код - пишу. Если type hint мешает читать код - не пишу. Если type hint занимает больше строки чем сигнатура - выношу в type alias.

Типы для людей, а не для mypy.


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

