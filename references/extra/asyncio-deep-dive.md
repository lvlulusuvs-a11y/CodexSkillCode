# asyncio Deep Dive

**Полное руководство по asyncio. От event loop до production patterns.**

---

## 1. Event Loop Fundamentals

```python
import asyncio

# Получение event loop
loop = asyncio.get_running_loop()  # внутри async функции
loop = asyncio.get_event_loop()    # вне async (deprecated в 3.10+)
loop = asyncio.new_event_loop()    # создать новый

# Что делает event loop:
# 1. Берёт задачу из очереди
# 2. Выполняет до первого await (или yield)
# 3. Регистрирует callback для продолжения
# 4. Ждёт I/O событий через epoll/kqueue/IOCP
# 5. Повторяет

# Event loop фазы (в порядке выполнения):
# 1. Callbacks (call_soon)
# 2. IO (select)
# 3. Timeouts (scheduled)
# 4. Idle handlers
```

## 2. Coroutines Deep Dive

```python
# coroutine function (определение)
async def my_coro() -> str:
    return "result"

# coroutine object (экземпляр)
coro = my_coro()  # <class 'coroutine'>

# Coroutine — это generator-based
# await = yield from
# async def = генератор с флагами

# Внутренности:
# coro.cr_code      # байткод
# coro.cr_frame     # фрейм выполнения
# coro.cr_running   # выполняется ли
# coro.cr_await     # на чём ожидает

# Coroutine states:
# CORO_CREATED     — создана
# CORO_RUNNING     — выполняется
# CORO_SUSPENDED   — ожидает (await)
# CORO_CLOSED      — завершена

# Можно отправить значение:
coro = my_coro()
coro.send(None)  # запустить до первого await
# coro.throw(RuntimeError)  # бросить исключение
coro.close()     # закрыть
```

## 3. Tasks

```python
import asyncio

# Task — обёртка над coroutine, управляемая event loop
task = asyncio.create_task(my_coro())
task = asyncio.ensure_future(my_coro())  # alternative

# Task API
task.get_name()        # имя задачи
task.set_name("my")
task.done()            # завершена?
task.cancelled()       # отменена?
task.cancel()          # отменить
task.result()          # результат (если done)
task.exception()       # исключение (если done)

# Task states
# PENDING — создана
# RUNNING — выполняется
# DONE — завершена (result, exception, cancelled)

# Task lifecycle
task = asyncio.create_task(work())
# Task добавляется в event loop
# Event loop выбирает задачу из очереди
# Выполняет до await
# Возвращает управление event loop
# Повторяет пока задача не завершится
```

## 4. Awaitables

```python
# Что можно await:
# 1. coroutine
await my_coro()

# 2. Task
task = asyncio.create_task(work())
await task

# 3. Future
future = loop.create_future()
# future.set_result(value)
# future.set_exception(error)
await future

# 4. awaitable объект с __await__
class MyAwaitable:
    def __await__(self):
        yield from something

# asyncio.Future — низкоуровневый awaitable
# Это обещание результата в будущем
# Task наследует Future
```

## 5. Running Multiple Tasks

```python
# gather — параллельное выполнение
results = await asyncio.gather(
    task1(),
    task2(),
    return_exceptions=True,  # не отменять остальные при ошибке
)

# as_completed — по мере готовности
for coro in asyncio.as_completed([task1(), task2()]):
    first_result = await coro
    print(first_result)

# wait — ожидание с условиями
done, pending = await asyncio.wait(
    [task1(), task2()],
    timeout=5.0,
    return_when=asyncio.FIRST_COMPLETED,
)
# return_when: FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED

# TaskGroup (Python 3.11+)
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(task1())
    t2 = tg.create_task(task2())
# При ошибке в одной задаче — все отменяются
```

## 6. Timeouts

```python
# Python 3.11+ (recomended)
async def fetch_with_timeout(url: str) -> dict:
    async with asyncio.timeout(5.0):
        return await fetch(url)

# Python 3.10 и ниже
async def fetch_with_timeout(url: str) -> dict:
    return await asyncio.wait_for(fetch(url), timeout=5.0)

# Partial timeout
async def process():
    async with asyncio.timeout(10.0):
        step1 = await fetch_data()  # не ограничено отдельно
        async with asyncio.timeout(2.0):
            step2 = await process_step(step1)  # ограничено 2с

# Shielding от timeout
async def critical():
    await asyncio.shield(save_to_db())  # не будет отменена
```

## 7. Synchronization Primitives

```python
# Lock — взаимное исключение
lock = asyncio.Lock()
async with lock:
    critical_section()

# Event — сигнализация
event = asyncio.Event()
# ... worker: await event.wait()
# ... main: event.set()

# Semaphore — ограничение параллелизма
sem = asyncio.Semaphore(10)
async with sem:
    await limited_operation()

# Condition — событие + блокировка
cond = asyncio.Condition()
async with cond:
    await cond.wait()  # ждать сигнала
    # cond.notify()  # сигнал одному
    # cond.notify_all()  # сигнал всем

# Barrier (3.11+)
barrier = asyncio.Barrier(3)  # 3 участника
async def worker():
    print("ready")
    await barrier.wait()  # ждёт всех
    print("go!")
```

## 8. Queues

```python
from asyncio import Queue, PriorityQueue, LifoQueue

# FIFO Queue
queue = Queue(maxsize=100)
await queue.put(item)
item = await queue.get()
queue.task_done()  # отметить обработку
await queue.join()  # ждать, пока всё обработается

# Priority Queue
pq = PriorityQueue()
await pq.put((priority, item))

# LIFO Queue (Stack)
stack = LifoQueue()
await stack.put(item)

# Пример: producer-consumer
async def producer(queue: Queue) -> None:
    for i in range(100):
        await queue.put(i)
        await asyncio.sleep(0.1)
    await queue.put(None)  # sentinel

async def consumer(queue: Queue) -> None:
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await process(item)
        queue.task_done()
```

## 9. Subprocesses

```python
import asyncio

# Run command
proc = await asyncio.create_subprocess_exec(
    "python", "script.py",
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
)
stdout, stderr = await proc.communicate()

# Shell command
proc = await asyncio.create_subprocess_shell(
    "ls -la | grep py",
    stdout=asyncio.subprocess.PIPE,
)
stdout = await proc.stdout.read()

# Streaming output
proc = await asyncio.create_subprocess_exec(
    "ping", "8.8.8.8",
    stdout=asyncio.subprocess.PIPE,
)
async for line in proc.stdout:
    print(line.decode().strip())
```

## 10. Synchronous ↔ Async Bridge

```python
import asyncio

# Из sync в async
def sync_function():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(async_func())
        return result
    finally:
        loop.close()

# Из async в sync (не блокируя event loop)
async def async_function():
    # Запустить CPU-bound в потоке
    result = await asyncio.to_thread(cpu_bound_func, arg)
    
    # Или через executor
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_bound, arg)
    
    # Синхронный I/O в потоке
    data = await asyncio.to_thread(requests.get, url)
    return data
```

## 11. Common Pitfalls

### Blocking the Event Loop
```python
# ❌ Блокирует event loop
async def bad():
    time.sleep(1)  # синхронный!
    result = heavy_cpu()  # блокирует!
    import requests
    return requests.get(url).json()  # блокирует!

# ✅ Асинхронные альтернативы
async def good():
    await asyncio.sleep(1)
    result = await asyncio.to_thread(heavy_cpu)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

### Coroutine Not Awaited
```python
# ❌ Корутина не запущена
async def main():
    my_coro()  # создана, не await → warning

# ✅
async def main():
    await my_coro()
    # или
    task = asyncio.create_task(my_coro())
```

### Race Conditions
```python
# ❌ Гонка
counter = 0
async def increment():
    global counter
    temp = counter  # может быть прервано
    await asyncio.sleep(0)  # переключение!
    counter = temp + 1

# ✅ Защита
lock = asyncio.Lock()
async def increment():
    global counter
    async with lock:
        temp = counter
        await asyncio.sleep(0)
        counter = temp + 1
```

### Deadlocks
```python
# ❌ Deadlock
async def bad():
    async with lock:
        await another_func()  # если another_func тоже берёт lock → deadlock

# ✅ Избегать
async def good():
    async with lock:
        # не вызывать функции, которые могут взять этот же lock
        result = simple_calculation()
```

## 12. Performance Tips

```python
# Не создавать задачи для каждой мелочи
# ❌
for item in items:
    asyncio.create_task(process(item))  # слишком много задач

# ✅ Использовать Semaphore
sem = asyncio.Semaphore(100)
async def limited(item):
    async with sem:
        await process(item)
tasks = [limited(item) for item in items]
await asyncio.gather(*tasks)

# Использовать asyncio.run() правильно
# ✅
def main():
    asyncio.run(async_main())

# ❌
def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_main())
    # утечка ресурсов
```

## 13. Debugging asyncio

```python
import asyncio
import os

# Включить debug режим
# Python любой:
asyncio.run(main(), debug=True)
# Или: PYTHONASYNCIODEBUG=1 python script.py

# Найти не-awaited корутины
import warnings
warnings.filterwarnings("error", message="coroutine.*was never awaited")

# Профилирование
async def main():
    loop = asyncio.get_running_loop()
    loop.slow_callback_duration = 0.05  # логировать медленные callbacks (>50ms)

# Мониторинг Task
for task in asyncio.all_tasks():
    print(f"Task: {task.get_name()}, Done: {task.done()}")
```

## 14. Best Practices Summary

```python
# 1. Используй asyncio.run() — не управляй loop вручную
# 2. Используй Timeout для всех I/O операций
# 3. Используй Semaphore для ограничения параллелизма
# 4. Используй return_exceptions=True в gather
# 5. Не блокируй event loop (time.sleep, requests, CPU)
# 6. Используй asyncio.to_thread для синхронного кода
# 7. Используй TaskGroup (3.11+) вместо gather для структурированного
# 8. Не создавай задачи без лимита
# 9. Всегда логируй исключения в фоновых задачах
# 10. Используй структурированный конкурентный код
```


---

## Advanced Asyncio Patterns

### Event Loop Customization

```python
"""Custom event loop configuration."""
from __future__ import annotations

import asyncio
import uvloop


def configure_event_loop() -> None:
    """Configure event loop for production.
    
    uvloop: 2x faster than default asyncio loop.
    """
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    loop = asyncio.get_event_loop()
    loop.set_debug(os.getenv("ASYNCIO_DEBUG", "0") == "1")
    
    # Custom executor for CPU-bound tasks
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=4)
    loop.set_default_executor(executor)


# Usage: configure_event_loop() before any async code
```

### Advanced Semaphore Patterns

```python
"""Semaphore patterns for controlling concurrency."""
from __future__ import annotations

import asyncio
from typing import Any


class AdaptiveSemaphore:
    """Semaphore that adapts to system load."""
    
    def __init__(self, max_size: int = 100):
        self._sem = asyncio.Semaphore(max_size)
        self._max = max_size
        self._current_load = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        await self._sem.acquire()
        async with self._lock:
            self._current_load += 1
    
    def release(self) -> None:
        self._sem.release()
        async with self._lock:
            self._current_load -= 1
    
    @property
    def load_percent(self) -> float:
        return (self._current_load / self._max) * 100


class PrioritySemaphore:
    """Semaphore with priority queue."""
    
    def __init__(self, max_size: int):
        self._sem = asyncio.Semaphore(max_size)
        self._queue: list[tuple[int, asyncio.Event]] = []
    
    async def acquire(self, priority: int = 0) -> None:
        event = asyncio.Event()
        heapq.heappush(self._queue, (priority, event, id(event)))
        self._queue.sort()
        
        while self._queue[0][2] != id(event):
            await event.wait()
            event.clear()
        
        heapq.heappop(self._queue)
        await self._sem.acquire()
```

### Async Context Manager Patterns

```python
"""Production async context manager patterns."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


@asynccontextmanager
async def timeout_context(timeout: float, message: str = "Operation timed out") -> AsyncIterator[None]:
    """Context manager with timeout."""
    try:
        async with asyncio.timeout(timeout):
            yield
    except asyncio.TimeoutError:
        raise TimeoutError(message)


@asynccontextmanager
async def retry_context(max_retries: int = 3, base_delay: float = 1.0) -> AsyncIterator[None]:
    """Context manager with automatic retry."""
    for attempt in range(max_retries):
        try:
            yield
            return
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(base_delay * (2 ** attempt))


@asynccontextmanager
async def traced_context(tracer, name: str, tags: dict = None) -> AsyncIterator[None]:
    """Context manager with tracing."""
    span = tracer.start_span(name, tags)
    try:
        yield
    except Exception:
        span.tags["error"] = True
        raise
    finally:
        tracer.end_span(span)
```

### Async Iterator Patterns

```python
"""Production async iterator patterns."""
from __future__ import annotations

import asyncio
from typing import AsyncIterator, TypeVar

T = TypeVar("T")


async def batch_iterator(items: list[T], batch_size: int = 100) -> AsyncIterator[list[T]]:
    """Yield items in batches."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


async def throttle_iterator(iterable: AsyncIterator[T], calls_per_second: float) -> AsyncIterator[T]:
    """Throttle iteration to N calls per second."""
    interval = 1.0 / calls_per_second
    last_call = 0.0
    
    async for item in iterable:
        now = time.monotonic()
        if now - last_call < interval:
            await asyncio.sleep(interval - (now - last_call))
        last_call = time.monotonic()
        yield item


async def retry_iterator(
    iterable: AsyncIterator[T],
    max_retries: int = 3,
    max_delay: float = 30.0,
) -> AsyncIterator[T]:
    """Retry on failure during iteration."""
    retries = 0
    while retries <= max_retries:
        try:
            async for item in iterable:
                yield item
                retries = 0  # Reset on success
            return  # Iterator exhausted
        except (ConnectionError, TimeoutError) as e:
            retries += 1
            if retries > max_retries:
                raise
            delay = min(1.0 * (2 ** (retries - 1)), max_delay)
            await asyncio.sleep(delay)
```


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
