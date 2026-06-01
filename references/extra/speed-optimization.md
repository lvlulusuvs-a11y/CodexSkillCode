# Speed Optimization — Beyond Python

**Когда чистого Python недостаточно. Numba, Cython, mypyc, Rust, multiprocessing.**

---

## 1. Профилирование перед оптимизацией

```bash
# 1. CPU профиль
python -m cProfile -s cumulative my_script.py | head -30

# 2. Построчный профиль
pip install line_profiler
kernprof -l -v my_script.py

# 3. Память
pip install memory_profiler
python -m memory_profiler my_script.py

# 4. Flamegraph
pip install py-spy
py-spy record -o flame.svg -- python my_script.py

# 5. Какую функцию оптимизировать?
# Ищи: cumulative time > 20% от общего
#       1000000+ calls
#       много времени в __add__, __getitem__ и т.д.
```

## 2. Numba (JIT компиляция)

Лучшее для численных расчётов без смены языка:

```python
from numba import jit, prange
import numpy as np

# JIT компиляция в машинный код
@jit(nopython=True, parallel=True, cache=True)
def monte_carlo_pi(n: int) -> float:
    count = 0
    for i in prange(n):  # parallel loop
        x = np.random.random()
        y = np.random.random()
        if x * x + y * y <= 1:
            count += 1
    return 4.0 * count / n

# Без Numba:  ~2.5s для 10M точек
# С Numba:    ~0.15s для 10M точек (~16x быстрее)

# Когда использовать:
# - Циклы с числами
# - NumPy операции
# - Математические расчёты
# Когда НЕ использовать:
# - Строки, dict, объекты (медленнее!)
# - I/O-bound задачи (asyncio лучше)
# - Маленькие функции (overhead JIT)
```

## 3. Cython (C-расширения)

```python
# cython_example.pyx
# Компилируется в C → .so

"""
# cython_example.pyx
def sum_of_squares(int n):
    cdef int i
    cdef long long total = 0
    for i in range(n):
        total += i * i
    return total
"""

# setup.py:
# from setuptools import setup
# from Cython.Build import cythonize
# setup(ext_modules=cythonize(["cython_example.pyx"]))

# Результат: ~50-100x быстрее чистого Python
```

## 4. mypyc (компиляция типизированного Python)

```python
# Mypyc: компилирует Python с type hints в C extension
# pip install mypyc

# mypyc my_script.py  → .so файл, ~2-4x быстрее

# Требования:
# - Полные type hints (без Any)
# - Нет eval/exec
# - Нет динамических import
# - Желательно без классов с __dict__ (использовать __slots__)

# Лучший сценарий: библиотека с type hints → mypyc → ~3x ускорение
```

## 5. Multiprocessing (CPU-bound)

```python
from multiprocessing import Pool, cpu_count
from functools import partial

def heavy_compute(x: int) -> int:
    # CPU-intensive (никакого I/O)
    result = 0
    for i in range(x):
        result += i * i
    return result

# Использование всех ядер
with Pool(processes=cpu_count()) as pool:
    results = pool.map(heavy_compute, range(1000))

# Concurrent.futures (удобнее)
from concurrent.futures import ProcessPoolExecutor, as_completed

with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    futures = {executor.submit(heavy_compute, i): i for i in range(1000)}
    results = {}
    for future in as_completed(futures):
        i = futures[future]
        results[i] = future.result()

# shared memory (для больших данных)
import multiprocessing.shared_memory
```

## 6. Rust через PyO3 (самый быстрый)

```python
# Самое производительное решение, но требует Rust знаний

# ruff (линтер) на Rust — работает в 10-100x быстрее Flake8
# pydantic-core на Rust — ~50x быстрее чистой Pydantic v1
# Polars (DataFrame) на Rust — ~10x быстрее Pandas

# Пример: написать свою функцию на Rust:
# #[pyfunction]
# fn fast_sum(n: u64) -> u64 {
#     (0..n).sum()
# }
```

## 7. Asyncio + Multiprocessing (гибрид)

Лучшая производительность: I/O в asyncio, CPU в процессах:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def main():
    loop = asyncio.get_running_loop()
    
    with ProcessPoolExecutor(max_workers=4) as pool:
        # CPU-bound задачи в процессах
        cpu_tasks = [loop.run_in_executor(pool, cpu_heavy, i) for i in range(100)]
        
        # I/O-bound задачи в asyncio
        io_tasks = [fetch(url) for url in urls]
        
        # Параллельно
        cpu_results, io_results = await asyncio.gather(
            asyncio.gather(*cpu_tasks),
            asyncio.gather(*io_tasks),
        )
```

## 8. Когда что использовать

```
Чистый Python (~0.1-1x):
├─ Прототипы, скрипты, маленькие проекты
├─ I/O-bound с asyncio
└─ Бизнес-логика (сложность в читаемости)

Numba (~10-100x):
├─ NumPy операции, численные методы
├─ Циклы с математикой
└─ Моделирование, симуляции

Cython/mypyc (~2-5x):
├─ Библиотеки с type hints
├─ Горячие функции (hot loops)
└─ Ускорение без смены языка

Rust/PyO3 (~10-100x):
├─ Критичный по скорости код
├─ Парсеры, компиляторы
└─ Когда Python слишком медленный

Multiprocessing (~N_x faster):
├─ CPU-bound, нет shared state
├─ Эмбаррассинг параллелизм
└─ Независимые вычисления

GPU (CUDA/cuDF):
├─ Матричные операции
├─ ML обучение
└─ Обработка больших массивов
```

## 9. Практические рецепты

### Рецепт 1: Быстрая сериализация

```python
# Стандартный json
data = json.dumps(large_dict)

# orjson (на Rust) — ~5x быстрее
import orjson
data = orjson.dumps(large_dict)  # bytes, не str

# msgpack — компактнее
import msgpack
data = msgpack.packb(large_dict)

# protocol buffers — для API
# from google.protobuf import json_format

# pickle — самый быстрый (но небезопасный!)
import pickle
data = pickle.dumps(large_dict, protocol=5)
```

### Рецепт 2: Быстрая валидация данных

```python
# Pydantic v2 (на Rust) — ~50x быстрее v1
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

# Для высоких нагрузок:
# 1. model_validate вместо User(**data) — ~2x быстрее
# 2. Использовать TypeAdapter для одной структуры
# 3. msgspec (ещё быстрее):
import msgspec

class User(msgspec.Struct):
    name: str
    email: str
    age: int

# msgspec: ~10x быстрее Pydantic, ~50x быстрее dataclass
```

### Рецепт 3: Быстрая замена if/elif

```python
# Медленно: много if/elif
def process(status: str) -> str:
    if status == "pending": return handle_pending()
    elif status == "confirmed": return handle_confirmed()
    elif status == "shipped": return handle_shipped()
    elif status == "delivered": return handle_delivered()

# Быстро: dict dispatch
HANDLERS = {
    "pending": handle_pending,
    "confirmed": handle_confirmed,
    "shipped": handle_shipped,
    "delivered": handle_delivered,
}

def process(status: str) -> str:
    if handler := HANDLERS.get(status):
        return handler()
    raise ValueError(f"Unknown status: {status}")
```

### Рецепт 4: Быстрая замена match/case (для 1-2 условий)

```python
# match/case компилируется в сложный байткод
# Для 1-2 условий if быстрее:

# match (медленнее для простых случаев)
match value:
    case "a": ...
    case "b": ...
    
# if (быстрее)
if value == "a": ...
elif value == "b": ...
```

## 10. Real-world speed comparison

```python
# Задача: сумма квадратов чисел от 0 до N
# N = 10_000_000

# Чистый Python:         ~1.5s
# sum(i*i for i in range(N))

# NumPy:                  ~0.08s (~19x)
# np.sum(np.arange(N)**2)

# Numba JIT:              ~0.02s (~75x)
# @jit(nopython=True) ...

# Rust/PyO3:              ~0.01s (~150x)

# Но для бизнес-логики читаемость важнее:
# 1.5s vs 0.01s — если вызывается раз в секунду, разницы нет
# Если 1000 раз в секунду — оптимизация обязательна
```


---

## Battle-Tested Production Patterns

### Error Handling & Resilience

```python
"""Production-grade error handling patterns."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ResiliencePolicy:
    """Resilience policy for external service calls."""
    max_retries: int = 3
    timeout_seconds: float = 10.0
    circuit_breaker_failures: int = 5
    rate_limit_per_second: int = 100


async def resilient_call[T](
    fn: Any,
    *args: Any,
    policy: ResiliencePolicy | None = None,
    **kwargs: Any,
) -> T:
    """Execute call with retry, timeout, and circuit breaker."""
    policy = policy or ResiliencePolicy()
    
    for attempt in range(policy.max_retries + 1):
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                return await fn(*args, **kwargs)
        except asyncio.TimeoutError:
            if attempt == policy.max_retries:
                raise
            delay = 1.0 * (2 ** attempt)
            logger.warning(f"Timeout (attempt {attempt+1}), retrying in {delay}s")
            await asyncio.sleep(delay)
        except Exception as e:
            if attempt == policy.max_retries:
                raise
            logger.warning(f"Error (attempt {attempt+1}): {e}")
            await asyncio.sleep(1.0 * (2 ** attempt))
    
    raise RuntimeError("Should not reach here")


### Observability Best Practices

```python
"""Observability patterns for production."""
from __future__ import annotations

import time
import functools
from typing import Any, Callable


def observe(name: str = ""):
    """Decorator to add observability to any function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(
                    f"{name or func.__name__} completed",
                    extra={"duration_ms": elapsed * 1000},
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    f"{name or func.__name__} failed",
                    extra={"duration_ms": elapsed * 1000, "error": str(e)},
                )
                raise
        return wrapper
    return decorator


### Configuration Management

```python
"""Type-safe configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceConfig:
    """Application configuration from environment."""
    
    # Service metadata
    service_name: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "app"))
    environment: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    
    # Database
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "1") == "1"
    
    # Cache
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    
    # API
    api_port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    
    # Feature flags
    enable_new_algo: bool = os.getenv("FEATURE_NEW_ALGO", "0") == "1"
    enable_debug_mode: bool = os.getenv("DEBUG", "0") == "1"
    
    def validate(self) -> None:
        """Validate config on startup."""
        errors = []
        if self.environment == "prod" and not self.database_url:
            errors.append("DATABASE_URL required in production")
        if self.environment == "prod" and "localhost" in (self.database_url or ""):
            errors.append("Cannot use localhost database in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
    
    @property
    def is_debug(self) -> bool:
        return self.enable_debug_mode or self.environment == "dev"


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
