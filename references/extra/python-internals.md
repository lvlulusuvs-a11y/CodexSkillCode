# Python Internals for Senior Developers

**Что происходит под капотом CPython. Знание internals = понимание почему код быстрый или медленный.**

---

## 1. GIL (Global Interpreter Lock)

### Что это
Один lock на весь процесс Python. Только один поток может выполнять bytecode в любой момент.

### Когда GIL мешает
- **CPU-bound задачи** в потоках — не работают параллельно (нужен multiprocessing)
- **I/O-bound задачи** — GIL отдаётся при ожидании I/O, поэтому asyncio/threading работают

### Как обойти
```python
# 1. Multiprocessing — отдельный GIL на процесс
from multiprocessing import Pool
with Pool(4) as pool:
    results = pool.map(cpu_intensive, data)

# 2. C-extension — отпускает GIL (numpy, pandas, Cython)
import numpy as np
result = np.array(data).sum()  # GIL отпущен в C коде

# 3. asyncio — кооперативная многозадачность в одном потоке
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
```

## 2. Object Model

### Всё — объект (даже типы)
```python
# type — метакласс, который создаёт классы
# object — базовый класс для всего

class MyClass: pass
print(type(MyClass))      # <class 'type'>
print(type(MyClass()))    # <class '__main__.MyClass'>
print(type(type))         # <class 'type'> — type — свой собственный метакласс
```

### __dict__ vs __slots__
```python
# Каждый объект хранит атрибуты в __dict__ (словарь)
# __slots__ заменяет __dict__ на tuple дескрипторов — меньше памяти

class WithDict:
    def __init__(self):
        self.a = 1
        self.b = 2

class WithSlots:
    __slots__ = ("a", "b")
    def __init__(self):
        self.a = 1
        self.b = 2

# >>> sys.getsizeof(WithDict())  # ~56 bytes + __dict__
# >>> sys.getsizeof(WithSlots()) # ~48 bytes (без __dict__)
```

## 3. Bytecode

Посмотреть, во что компилируется функция:
```python
import dis

def example(a, b):
    return a + b

dis.dis(example)
#   3 LOAD_FAST    0 (a)
#   6 LOAD_FAST    1 (b)
#   9 BINARY_OP    0 (+)
#  12 RETURN_VALUE
```

### Почему comprehension быстрее цикла
```python
# list comprehension компилируется в:
# MAKE_FUNCTION + CALL + специальный LIST_APPEND (C-level)
# А ручной цикл:
# SETUP_LOOP + много инструкций для append

# Компилятор может оптимизировать comprehension
result = [x * 2 for x in range(100)]  # быстрее
```

## 4. Reference Counting

CPython использует подсчёт ссылок + GC для циклов:
```python
import sys
a = []
b = [a]
print(sys.getrefcount(a))  # 3: a, b[0], временная в getrefcount

# del уменьшает счётчик
del a  # b[0] всё ещё ссылается → объект жив
del b  # счётчик = 0 → объект удалён
```

### Циклические ссылки
```python
# GC (сборщик циклов) нужен только для циклических ссылок
class Node:
    def __init__(self):
        self.child = None
        self.parent = None

a = Node()
b = Node()
a.child = b
b.parent = a  # Цикл: a → b → a

del a  # b.parent всё ещё ссылается на a
del b  # никто не ссылается на них, но refcount не 0
# GC соберёт их при следующем запуске

# weakref — без увеличения счётчика
import weakref
parent = weakref.ref(node)  # не мешает GC
```

## 5. MRO (Method Resolution Order)

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass

print(D.__mro__)
# (D, B, C, A, object)

# C3 linearization:
# D → B → C → A → object
```

## 6. Descriptors (дескрипторы)

Дескрипторы — основа property, classmethod, staticmethod:
```python
class Descriptor:
    """Дескриптор: объект с __get__ и/или __set__."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, f"_{self.name}")
    
    def __set__(self, obj: Any, value: Any) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be str")
        setattr(obj, f"_{self.name}", value)

class User:
    name = Descriptor("name")  # дескриптор на уровне класса
    
    def __init__(self, name: str):
        self.name = name  # вызывает Descriptor.__set__
```

### Аналог через property:
```python
class User:
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("name must be str")
        self._name = value
```

## 7. Метаклассы (редко, но мощно)

```python
# Метакласс — это type "custom"
class SingletonMeta(type):
    """Метакласс для Singleton паттерна."""
    _instances: dict[type, Any] = {}
    
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        self.value = 42

# Все инстансы Config — один и тот же объект
a = Config()
b = Config()
assert a is b  # True
```

## 8. String Interning

Малые строки кэшируются CPython:
```python
a = "hello"
b = "hello"
print(a is b)  # True — CPython интернирует короткие строки

c = "hello world!" * 100
d = "hello world!" * 100
print(c is d)  # False — длинные строки не интернируются

# Можно принудительно:
import sys
e = sys.intern("long string " * 100)
f = sys.intern("long string " * 100)
print(e is f)  # True — интернировано
```

## 9. Function Call Overhead

Вызов функции в Python — дорого:
```python
# ❌ Тысячи вызовов в цикле
def double(x): return x * 2
values = [double(x) for x in range(1000000)]

# ✅ Inline операция (без вызова функции)
values = [x * 2 for x in range(1000000)]  # ~2x быстрее

# Ещё пример:
# sorted() вызывает cmp-функцию миллионы раз
# if/elif быстрее, чем match/case для 1-2 условий (match требует build_map)
```

## 10. Async Internals

```python
# coroutine — это объект с __await__
async def example():
    pass

print(type(example()))  # <class 'coroutine'>

# await — это yield из generator-based coroutine
# event loop — это while True, который делает:
#   1. Берёт задачу из очереди
#   2. Выполняет до следующего await/yield
#   3. Добавляет коллбек для продолжения

# asyncio.gather() создаёт Task для каждой корутины
# Task оборачивает coroutine и управляет её жизненным циклом

# Неблокирующий I/O:
# select/epoll/kqueue — системные вызовы "есть ли данные?"
# Сокеты переключаются в non-blocking режим
# asyncio регистрирует fd в epoll и ждёт событий
```

## 11. Garbage Collection

```python
import gc

# GC собирает только циклические ссылки
# Раз в некоторое количество аллокаций (порог)

# Включить отладку
gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)

# Ручной запуск
collected = gc.collect()
print(f"Collected {collected} objects")

# Отключить GC (если нет циклов)
gc.disable()

# Поколения: 0 (молодые), 1 (средние), 2 (старые)
# Большинство объектов умирают в поколении 0
```

## 12. Import System

```python
# import module:
# 1. Ищет в sys.modules (кэш)
# 2. Ищет по sys.meta_path (finders: zip, frozen, path)
# 3. PathFinder ищет в sys.path
# 4. Выполняет модуль
# 5. Добавляет в sys.modules

import sys
print(list(sys.meta_path))
# [_frozen_importlib.BuiltinImporter, 
#  _frozen_importlib.FrozenImporter,
#  _frozen_importlib.PathFinder]

# PEP 302: finder → loader
# PEP 451: module spec (finder + loader + path)

# Можно подменить импорт:
import sys
original_import = __import__

def patched_import(name, *args, **kwargs):
    if name.startswith("secret"):
        raise ImportError(f"Not allowed: {name}")
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = patched_import
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

## Extended Enterprise Patterns

### Production-Grade Connection Management

```python
"""Enterprise connection and resource management."""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


@dataclass
class ResourcePool:
    """Generic resource pool with health checks."""
    
    async def acquire(self) -> Any:
        """Acquire resource with timeout."""
        async with asyncio.timeout(5):
            return await self._acquire()
    
    async def release(self, resource: Any) -> None:
        """Release resource back to pool."""
        await self._release(resource)
    
    @asynccontextmanager
    async def use(self) -> AsyncIterator[Any]:
        """Context manager for safe resource usage."""
        resource = await self.acquire()
        try:
            yield resource
        except Exception as e:
            logger.error(f"Resource error: {e}")
            await self.invalidate(resource)
            raise
        finally:
            await self.release(resource)


### Error Handling Framework

class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, id: Any):
        super().__init__(
            message=f"{resource} not found: {id}",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for {field}: {reason}",
            code="VALIDATION_ERROR",
            status_code=422,
        )


class ServiceUnavailableError(AppError):
    def __init__(self, service: str):
        super().__init__(
            message=f"{service} is unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


def error_handler(func):
    """Decorator for uniform error handling."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            raise
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("Database")
        except Exception as e:
            logger.exception("Unhandled error")
            raise AppError(str(e), "INTERNAL_ERROR", 500)
    return wrapper


### Async Task Management

class TaskManager:
    """Manage background tasks with proper cleanup."""
    
    def __init__(self):
        self._tasks: set[asyncio.Task] = set()
    
    def create_task(self, coro) -> asyncio.Task:
        task = asyncio.create_task(self._wrap(coro))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
    
    async def cancel_all(self) -> None:
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
    
    async def _wrap(self, coro):
        try:
            return await coro
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Background task failed: {e}")
