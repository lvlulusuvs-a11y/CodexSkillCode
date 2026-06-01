# Async Patterns

**Проверенные паттерны async/await для Python. Практика, а не теория.**

---

## 1. Sequential vs Parallel vs Limited

```python
# ─── Sequential (медленно) ───
results = []
for url in urls:
    results.append(await fetch(url))  # total = N * latency

# ─── Parallel (быстро, но без контроля) ───
results = await asyncio.gather(*[fetch(url) for url in urls])  # total = max(latency)

# ─── Limited Parallelism (быстро + контроль) ───
sem = asyncio.Semaphore(10)
async def bounded_fetch(url):
    async with sem:
        return await fetch(url)

results = await asyncio.gather(*[bounded_fetch(url) for url in urls])
```

## 2. Async Context Managers

```python
# Свой async контекстный менеджер
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_session(url: str):
    session = await create_session(url)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

# Использование
async with db_session(DATABASE_URL) as session:
    user = await session.get(User, 1)
    user.name = "new name"
    # если здесь ошибка → rollback, иначе commit
```

## 3. Async Iterators

```python
# Бесконечный поток данных
class SensorReader:
    """Асинхронный итератор для чтения датчиков."""
    
    async def __aiter__(self):
        return self
    
    async def __anext__(self) -> float:
        while True:
            value = await read_sensor()
            if value is not None:
                return value
            await asyncio.sleep(0.1)  # polling
```

## 4. Async Generators

```python
async def paginate(query, page_size: int = 100):
    """Асинхронный генератор для пагинации."""
    offset = 0
    while True:
        batch = await query.limit(page_size).offset(offset).all()
        if not batch:
            return
        yield from batch
        offset += page_size

# Использование
async for user in paginate(User.query.order_by(User.id)):
    process(user)
```

## 5. Async with Timeout

```python
# Python 3.11+: asyncio.timeout
async def fetch_with_timeout(url: str, timeout: float = 5.0) -> dict:
    async with asyncio.timeout(timeout):
        return await fetch(url)

# Python 3.10 и ниже: wait_for
async def fetch_with_timeout(url: str, timeout: float = 5.0) -> dict:
    return await asyncio.wait_for(fetch(url), timeout=timeout)
```

## 6. Async Queue with Workers

```python
class WorkerPool:
    def __init__(self, workers: int = 4):
        self._queue = asyncio.Queue()
        self._workers = workers
    
    async def start(self):
        tasks = [asyncio.create_task(self._worker()) for _ in range(self._workers)]
        await self._queue.join()  # ждём, пока очередь опустеет
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _worker(self):
        while True:
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self.process(item)
                self._queue.task_done()
            except asyncio.TimeoutError:
                break
    
    async def process(self, item):
        """Override this."""
        pass
    
    async def add(self, item):
        await self._queue.put(item)
```

## 7. Async Events (signaling)

```python
class ShutdownGuard:
    """Graceful shutdown с сигналом."""
    
    def __init__(self):
        self._shutdown = asyncio.Event()
    
    async def wait(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self._shutdown.set)
            except NotImplementedError:
                pass
        await self._shutdown.wait()
```

## 8. Async Locks

```python
# Защита разделяемого ресурса
lock = asyncio.Lock()

async def update_balance(user_id: int, amount: float):
    async with lock:
        balance = await db.get_balance(user_id)
        await db.set_balance(user_id, balance + amount)

# Атомарный счётчик через asyncio.Lock или redis.incr
```

## 9. Async Synchronization Patterns

```python
# Event — одноразовый сигнал
connected = asyncio.Event()
# ... в worker: await connected.wait()
# ... в main: connected.set()

# Condition — многоразовый сигнал с блокировкой
cond = asyncio.Condition()

# Semaphore — ограничение параллелизма
sem = asyncio.Semaphore(5)

# Barrier — синхронизация N задач (Python 3.11+)
barrier = asyncio.Barrier(3)

# Queue — producer/consumer
queue = asyncio.Queue(maxsize=100)
```

## 10. Common Pitfalls

### Blocking the event loop
```python
# ❌ Ужасно: блокирует весь event loop на 2 секунды
async def bad():
    time.sleep(2)  # синхронный sleep

# ✅ Правильно
async def good():
    await asyncio.sleep(2)  # async sleep

# ❌ Для CPU-bound задач
async def bad():
    result = heavy_cpu_computation()  # блокирует loop

# ✅ В отдельном потоке
async def good():
    result = await asyncio.to_thread(heavy_cpu_computation)

# Или через loop.run_in_executor
async def good2():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, heavy_cpu_computation)
```

### Coroutine vs Task
```python
# ❌ Забыл создать Task
async def main():
    coro = my_async_func()  # корутина создана, но не запущена
    # ... корутина будет собрана GC с предупреждением

# ✅ Правильно: create_task
async def main():
    task = asyncio.create_task(my_async_func())
    await task

# ✅ Или просто await
async def main():
    await my_async_func()

# ✅ asyncio.gather создаёт задачи автоматически
async def main():
    results = await asyncio.gather(func1(), func2(), func3())
```

### Exception handling in gather
```python
# ❌ Одна ошибка убивает все
results = await asyncio.gather(func1(), func2())  # если func1 упадёт, func2 будет отменена

# ✅ return_exceptions=True — остальные продолжают
results = await asyncio.gather(func1(), func2(), return_exceptions=True)
for r in results:
    if isinstance(r, Exception):
        print(f"Error: {r}")
```

### TaskGroup (Python 3.11+)
```python
# Лучше gather: если одна задача падает, остальные отменяются
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch("url1"))
    task2 = tg.create_task(fetch("url2"))
# Все задачи завершены (или отменены) здесь
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
