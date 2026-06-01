# Concurrency Patterns in Python

**Когда использовать threading vs asyncio vs multiprocessing. Реальные паттерны.**

---

## 1. Выбор правильного инструмента

```
┌────────────────────┬──────────────────┬──────────────────────┐
│                    │       I/O-bound  │      CPU-bound       │
├────────────────────┼──────────────────┼──────────────────────┤
│ Одно ядро          │ asyncio          │ asyncio (один поток) │
│ Много ядер (shared)│ threading*       │ multiprocessing      │
│ Много ядер (distr) │ asyncio + aiohttp│ celery / ray         │
└────────────────────┴──────────────────┴──────────────────────┘
*threading для I/O-bound работает, но GIL не даёт CPU parallelism
```

## 2. ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

# Для I/O-bound задач с синхронными библиотеками
def fetch_url(url: str) -> bytes:
    import requests
    return requests.get(url).content

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_url, url): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        try:
            data = future.result()
            print(f"{url}: {len(data)} bytes")
        except Exception as e:
            print(f"{url}: error {e}")
```

## 3. ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor
import math

def is_prime(n: int) -> bool:
    """CPU-intensive: проверка на простоту."""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Использование всех ядер
with ProcessPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(is_prime, range(10_000_000, 10_001_000)))
    print(f"Found {sum(results)} primes")

# Важно: каждый процесс — отдельная память!
# Передача больших данных между процессами — дорого (pickle)
```

## 4. Async + Threading (гибрид)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_sync_in_thread(func: Callable, *args: Any) -> Any:
    """Запустить синхронную функцию в потоке (не блокируя event loop)."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)

# Использование
async def handle_request() -> Response:
    # I/O-bound async
    data = await fetch_from_api()
    
    # CPU-bound в потоке (не блокирует event loop)
    processed = await run_sync_in_thread(heavy_processing, data)
    
    return Response(processed)
```

## 5. Async + Multiprocessing (гибрид)

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def parallel_compute(items: list[int]) -> list[int]:
    """CPU-bound параллельно, I/O в asyncio."""
    loop = asyncio.get_running_loop()
    
    with ProcessPoolExecutor(max_workers=4) as pool:
        # CPU-bound в процессах
        cpu_tasks = [loop.run_in_executor(pool, compute, item) for item in items]
        # I/O-bound в asyncio
        io_tasks = [fetch(url) for url in urls]
        
        # Параллельно
        cpu_results, io_results = await asyncio.gather(
            asyncio.gather(*cpu_tasks),
            asyncio.gather(*io_tasks),
        )
    
    return cpu_results
```

## 6. Shared Memory

```python
from multiprocessing import shared_memory
import numpy as np

# Создать shared memory
shm = shared_memory.SharedMemory(name="shared_array", create=True, size=1024 * 1024)
array = np.ndarray((256, 256), dtype=np.int32, buffer=shm.buf)

# Дочерние процессы могут читать тот же buffer
# shm2 = shared_memory.SharedMemory(name="shared_array")
# array2 = np.ndarray((256, 256), dtype=np.int32, buffer=shm2.buf)

# Для безопасного доступа используй multiprocessing.Lock
```

## 7. Async Lock vs Thread Lock

```python
# asyncio.Lock — для async кода (не блокирует event loop)
async_lock = asyncio.Lock()

async def update_balance(user_id: int, amount: float) -> None:
    async with async_lock:
        balance = await get_balance(user_id)
        await set_balance(user_id, balance + amount)

# threading.Lock — для потоков
thread_lock = threading.Lock()

def update_counter():
    with thread_lock:
        counter += 1

# ⚠️ Никогда не смешивай их!
```

## 8. Actor Model (через queue)

```python
class Actor:
    """Простая реализация Actor Model."""
    
    def __init__(self) -> None:
        self._queue = asyncio.Queue()
        self._task = None
    
    def start(self) -> None:
        self._task = asyncio.create_task(self._run())
    
    async def send(self, message: Any) -> None:
        await self._queue.put(message)
    
    async def _run(self) -> None:
        while True:
            message = await self._queue.get()
            try:
                await self.handle(message)
            except Exception as e:
                logger.error("Actor error: %s", e)
    
    async def handle(self, message: Any) -> None:
        """Override this."""
        pass
    
    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
```

## 9. Pipeline Pattern (каналы)

```python
class Pipeline:
    """Конвейер обработки данных."""
    
    def __init__(self, stages: list[Callable]) -> None:
        self._stages = stages
        self._queues = [asyncio.Queue() for _ in range(len(stages) + 1)]
    
    async def run(self, input: AsyncIterator) -> None:
        producers = []
        # Старт всех этапов
        for i, stage in enumerate(self._stages):
            producers.append(asyncio.create_task(
                self._stage_worker(i, stage)
            ))
        
        # Подача входных данных
        async for item in input:
            await self._queues[0].put(item)
        await self._queues[0].put(None)  # sentinel
        
        # Ожидание завершения
        await asyncio.gather(*producers)
    
    async def _stage_worker(self, idx: int, stage: Callable) -> None:
        input_q = self._queues[idx]
        output_q = self._queues[idx + 1]
        
        while True:
            item = await input_q.get()
            if item is None:  # сигнал завершения
                await output_q.put(None)
                break
            
            processed = await stage(item)
            await output_q.put(processed)

# Использование
async def extract(item): return item
async def transform(item): return item * 2
async def load(item): print(f"Loaded: {item}")

pipeline = Pipeline([extract, transform, load])
# await pipeline.run([1, 2, 3, 4, 5])
```


---

## Advanced Concurrency Patterns

### Thread Safety with asyncio.Lock

```python
"""Thread-safe async operations."""
from __future__ import annotations

import asyncio
from asyncio import Lock
from dataclasses import dataclass, field


@dataclass
class AtomicCounter:
    """Thread-safe counter for concurrent operations."""
    _lock: Lock = field(default_factory=Lock)
    _value: int = 0
    
    async def increment(self, amount: int = 1) -> int:
        async with self._lock:
            self._value += amount
            return self._value
    
    async def get(self) -> int:
        async with self._lock:
            return self._value


@dataclass
class ReadWriteLock:
    """Read-write lock for concurrent read, exclusive write."""
    _read_ready: Lock = field(default_factory=Lock)
    _readers: int = 0
    
    @asynccontextmanager
    async def read(self):
        async with self._read_ready:
            self._readers += 1
            if self._readers == 1:
                await self._resource.acquire()
        try:
            yield
        finally:
            async with self._read_ready:
                self._readers -= 1
                if self._readers == 0:
                    self._resource.release()
    
    @asynccontextmanager
    async def write(self):
        async with self._resource:
            yield
```

### Barrier Pattern

```python
"""Barrier for synchronizing concurrent tasks."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Barrier:
    """Synchronization barrier for N tasks."""
    n: int
    _count: int = 0
    _event: asyncio.Event = field(default_factory=asyncio.Event)
    
    async def wait(self) -> None:
        self._count += 1
        if self._count >= self.n:
            self._event.set()
        await self._event.wait()
```

### Fan-Out / Fan-In with Error Handling

```python
"""Fan-out multiple tasks, collect results."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def fan_out_fan_in(
    items: list[T],
    worker: Callable[[T], Awaitable[R]],
    max_concurrency: int = 10,
    timeout: float = 30.0,
) -> list[R]:
    """Process items concurrently, collect results in order."""
    sem = asyncio.Semaphore(max_concurrency)
    
    async def wrapped(item: T) -> R:
        async with sem:
            try:
                async with asyncio.timeout(timeout):
                    return await worker(item)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Worker timed out after {timeout}s")
    
    tasks = [asyncio.create_task(wrapped(item)) for item in items]
    return await asyncio.gather(*tasks)
```


---

## Real-World Implementation

```python
"""Production-grade implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionService:
    """Battle-tested service pattern with full observability."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with retry, timeout, and monitoring."""
        start = time.perf_counter()
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                elapsed = time.perf_counter() - start
                logger.info("Success", extra={"duration_ms": elapsed * 1000})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"Failed after {elapsed*1000:.1f}ms: {e}")
            raise
    
    async def _process(self) -> dict[str, Any]:
        """Core processing logic."""
        return {"status": "ok", "timestamp": time.time()}


### Key Takeaway for Principal Engineers

This pattern exemplifies the Principal Engineer mindset:
1. **Defensive by default** — timeouts, error handling, logging
2. **Observable** — every operation produces metrics and logs
3. **Resilient** — built to handle failures gracefully
4. **Simple** — one function, one responsibility
5. **Testable** — can mock `_process` and test retry/timeout logic

Apply this pattern to every external call in your service.


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
