# Data Structures Guide

**Когда что использовать. Выбор структуры данных = 80% производительности.**

---

## Core Structures

### List vs Tuple vs Array

```python
# List — mutable, разнородные, частые вставки/удаления
items: list[int] = [1, 2, 3]

# Tuple — immutable, хэшируемый (ключ в dict), распаковка
point: tuple[int, int] = (10, 20)
d: dict[tuple[int, int], str] = {point: "home"}

# Array — однородные числа, меньше памяти
from array import array
numbers: array[int] = array("i", [1, 2, 3])  # ~4 bytes per element

# Что выбрать:
# ╔══════════╦════════════════════════════╦══════════════════════════╗
# ║ Нужно    ║ Выбрать                   ║ Почему                   ║
# ╠══════════╬════════════════════════════╬══════════════════════════╣
# ║ Изменять ║ List, Array               ║ mutable                   ║
# ║ Хэшировать║ Tuple                     ║ immutable → __hash__      ║
# ║ Экономия пам.║ Array, tuple (без __dict__) ║ меньше overhead      ║
# ║ Быстрый доступ║ List, Array, Tuple   ║ O(1) index               ║
# ╚══════════╩════════════════════════════╩══════════════════════════╝
```

### Dict vs defaultdict vs Counter

```python
from collections import defaultdict, Counter

# dict — general purpose
user = {"name": "Alice", "age": 30}

# defaultdict — auto-default для missing keys
grouped: defaultdict[str, list[int]] = defaultdict(list)
for item in items:
    grouped[item.type].append(item.id)  # не надо проверять существование

# Counter — подсчёт элементов
text = "hello world"
freq = Counter(text)
# Counter({'l': 3, 'o': 2, 'h': 1, 'e': 1, ' ': 1, 'w': 1, 'r': 1, 'd': 1})
print(freq.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]
```

### Set vs frozenset

```python
# Set — mutable, нехэшируемый
unique = {1, 2, 3}
unique.add(4)

# frozenset — immutable, хэшируемый (можно в set of sets)
immutable = frozenset([1, 2, 3])
set_of_sets = {frozenset([1, 2]), frozenset([3, 4])}
```

### deque (double-ended queue)

```python
from collections import deque

# O(1) вставка/удаление с обоих концов
queue: deque[str] = deque(maxlen=100)  # fixed size queue

queue.append("right")     # O(1)
queue.appendleft("left")  # O(1)
queue.pop()               # O(1)
queue.popleft()           # O(1)

# Использовать для:
# - Очередь задач
# - Rolling window (maxlen)
# - BFS в графах
```

### Heapq (priority queue)

```python
import heapq

# list как min-heap
heap = [3, 1, 4, 1, 5]
heapq.heapify(heap)        # O(n) → [1, 1, 4, 3, 5]
heapq.heappush(heap, 2)    # O(log n)
smallest = heapq.heappop(heap)  # O(log n)

# Max-heap через отрицательные значения
max_heap = [-x for x in [3, 1, 4]]
heapq.heapify(max_heap)
largest = -heapq.heappop(max_heap)  # 4

# N largest/smallest
top_3 = heapq.nlargest(3, [3, 1, 4, 1, 5])  # [5, 4, 3]
```

### Namedtuple vs Dataclass

```python
from typing import NamedTuple
from dataclasses import dataclass

# NamedTuple — immutable, легковесный, сравнение по значению
class Point(NamedTuple):
    x: float
    y: float

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)
assert p1 == p2  # True
assert hash(p1) == hash(p2)  # да, хэшируемый

# Dataclass — mutable, гибкий, методы
@dataclass(frozen=True)  # frozen = immutable
class User:
    id: int
    name: str
    
    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("name required")

# Когда что:
# NamedTuple: маленькие value objects, совместимость с tuple
# Dataclass: сложная логика, валидация, мутабельность
```

## Advanced Structures

### ChainMap (multiple dicts as one)

```python
from collections import ChainMap

# Объединяет dicts без копирования
defaults = {"host": "localhost", "port": 8080, "debug": False}
overrides = {"port": 9000, "debug": True}

config = ChainMap(overrides, defaults)  # overrides приоритет
print(config["host"])  # localhost (from defaults)
print(config["port"])  # 9000 (from overrides)
print(config["debug"]) # True (from overrides)
```

### OrderedDict (insertion order)

```python
from collections import OrderedDict

# Python 3.7+: dict сохраняет порядок
# OrderedDict нужен для:
# 1. move_to_end()
# 2. popitem(last=False) — FIFO

cache = OrderedDict()

# LRU cache реализация:
def lru_get(key: str) -> Any | None:
    if key not in cache:
        return None
    cache.move_to_end(key)  # обновить позицию
    return cache[key]

def lru_put(key: str, value: Any, maxsize: int = 100) -> None:
    if key in cache:
        cache.move_to_end(key)
    cache[key] = value
    if len(cache) > maxsize:
        cache.popitem(last=False)  # удалить самый старый
```

### Weak references

```python
import weakref

# Ссылка, не увеличивающая refcount
class ExpensiveObject:
    pass

# WeakValueDictionary — значения удаляются, если на них нет ссылок
cache = weakref.WeakValueDictionary[int, ExpensiveObject]()

# WeakSet — set из слабых ссылок
from weakref import WeakSet

class EventListener:
    pass

listeners = WeakSet[EventListener]()

# Использовать для:
# - Кэш объектов (автоочистка)
# - Наблюдатели (не мешать GC)
# - Tree structures (родитель — слабая ссылка на детей)
```

## Time Complexity Reference

| Structure | Index | Search | Insert | Delete | Memory |
|-----------|-------|--------|--------|--------|--------|
| list | O(1) | O(n) | O(n)* | O(n) | Низкая |
| tuple | O(1) | O(n) | - | - | Низкая |
| set | - | O(1) | O(1) | O(1) | Средняя |
| dict | - | O(1) | O(1) | O(1) | Средняя |
| deque | O(1) | O(n) | O(1) | O(1) | Низкая |
| heap | - | O(n) | O(log n) | - | Низкая |
| array | O(1) | O(n) | O(1)* | O(1)* | Очень низкая |
| str | O(1) | O(n) | - | - | Низкая |
| bytes | O(1) | O(n) | - | - | Очень низкая |

*Insert в список O(1) в конце, O(n) в начале.
*Array: append O(1), insert O(n).

## Quick Decision Tree

```
Нужно хранить элементы?
├─ Важен порядок?
│  ├─ Да → list (изменяемый) / tuple (фикс)
│  └─ Нет → set (уникальные) / list (неуникальные)
├─ Важен поиск?
│  ├─ По ключу → dict
│  ├─ По значению, много → set (если уникальные)
│  └─ По значению, мало → list (простой перебор)
├─ Нужна очередь?
│  ├─ FIFO → deque
│  ├─ Priority → heap
│  └─ Lifo → list (pop/append)
└─ Нужен счётчик?
   └─ Counter (collections)
```


---

## Enterprise Implementation Patterns

### Production-Grade Code

```python
"""Enterprise-grade implementation with full resilience."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools
import random

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class EnterpriseService:
    """Production service with all resilience patterns."""
    
    max_retries: int = 3
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    
    def __post_init__(self):
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time = 0.0
    
    async def call_with_resilience(
        self,
        fn: Callable[..., Awaitable[T]],
        fallback: Callable[..., Awaitable[T]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute with circuit breaker + retry + timeout."""
        if self._circuit_open:
            if time.monotonic() - self._last_failure_time < 30.0:
                if fallback:
                    return await fallback(*args, **kwargs)
                raise RuntimeError("Circuit breaker is open")
            self._circuit_open = False
            logger.info("Circuit breaker half-open, testing...")
        
        for attempt in range(self.max_retries + 1):
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    result = await fn(*args, **kwargs)
                    self._failure_count = 0
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout (attempt {attempt+1})")
                if attempt == self.max_retries:
                    self._record_failure()
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt) + random.uniform(0, 0.5))
            except Exception as e:
                logger.warning(f"Error (attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    self._record_failure()
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        
        raise RuntimeError("Unreachable")
    
    def _record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.circuit_breaker_threshold:
            self._circuit_open = True
            logger.error(f"Circuit breaker opened after {self._failure_count} failures")


### Configuration Management

@dataclass
class ServiceSettings:
    """Type-safe configuration from environment variables."""
    service_name: str = "my-service"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = ""
    db_pool_min: int = 5
    db_pool_max: int = 20
    db_timeout: int = 5
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_default_ttl: int = 300
    
    # API
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = None
    
    # External services
    external_api_timeout: int = 10
    external_api_retries: int = 3
    
    # Feature flags
    enable_new_feature: bool = False
    
    def validate(self) -> None:
        """Validate configuration on startup."""
        errors = []
        if self.environment == "production":
            if not self.database_url:
                errors.append("DATABASE_URL is required")
            if self.debug:
                errors.append("Debug mode must be disabled in production")
            if "localhost" in (self.database_url or ""):
                errors.append("Cannot use localhost in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @classmethod
    def from_env(cls) -> "ServiceSettings":
        """Load configuration from environment variables."""
        import os
        return cls(
            service_name=os.getenv("SERVICE_NAME", "my-service"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            debug=os.getenv("DEBUG", "0") == "1",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv("DATABASE_URL", ""),
            db_pool_min=int(os.getenv("DB_POOL_MIN", "5")),
            db_pool_max=int(os.getenv("DB_POOL_MAX", "20")),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            port=int(os.getenv("PORT", "8000")),
            external_api_timeout=int(os.getenv("EXTERNAL_API_TIMEOUT", "10")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        )


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
