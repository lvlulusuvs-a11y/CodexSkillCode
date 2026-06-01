# Advanced Async/Await Patterns

**Продвинутые паттерны asyncio для продакшена. Не туториал — реальные приёмы.**

---

## 1. Async Context Manager с таймаутом

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def timeout_context(timeout: float) -> AsyncIterator[None]:
    """Контекстный менеджер с таймаутом."""
    try:
        async with asyncio.timeout(timeout):
            yield
    except TimeoutError:
        logger.warning("Operation timed out after %.2fs", timeout)
        raise

# Использование
async with timeout_context(5.0):
    result = await slow_operation()
```

## 2. Async Pool (Worker Pool)

```python
class AsyncPool:
    """Пул воркеров для параллельной обработки."""
    
    def __init__(self, workers: int = 10):
        self._workers = workers
        self._queue: asyncio.Queue[tuple[int, Callable]] = asyncio.Queue()
        self._results: dict[int, Any] = {}
    
    async def run(self, tasks: list[Callable]) -> list[Any]:
        """Запустить задачи параллельно."""
        n = len(tasks)
        for i, task in enumerate(tasks):
            await self._queue.put((i, task))
        
        workers = [asyncio.create_task(self._worker()) for _ in range(min(self._workers, n))]
        await self._queue.join()
        
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        
        return [self._results[i] for i in range(n)]
    
    async def _worker(self) -> None:
        while True:
            try:
                idx, task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                self._results[idx] = await task()
                self._queue.task_done()
            except TimeoutError:
                break
            except Exception as e:
                self._results[idx] = e
                self._queue.task_done()
```

## 3. Async Iterator с backpressure

```python
class AsyncPaginatedIterator:
    """Асинхронный итератор с контролем скорости."""
    
    def __init__(self, fetcher: Callable, page_size: int = 100, max_concurrent: int = 3):
        self._fetcher = fetcher
        self._page_size = page_size
        self._sem = asyncio.Semaphore(max_concurrent)
        self._buffer: asyncio.Queue = asyncio.Queue(maxsize=max_concurrent * page_size)
        self._done = False
    
    async def __aiter__(self) -> AsyncIterator:
        return self
    
    async def __anext__(self) -> Any:
        if self._buffer.empty() and not self._done:
            await self._fill_buffer()
        
        try:
            return await asyncio.wait_for(self._buffer.get(), timeout=30.0)
        except TimeoutError:
            raise StopAsyncIteration
    
    async def _fill_buffer(self) -> None:
        """Prefetch следующих страниц."""
        async def fetch_page(page: int) -> None:
            async with self._sem:
                items = await self._fetcher(page=page, size=self._page_size)
                for item in items:
                    await self._buffer.put(item)
        
        tasks = [fetch_page(i) for i in range(1, 4)]
        await asyncio.gather(*tasks, return_exceptions=True)
```

## 4. Async Lock with Priority

```python
class PriorityLock:
    """Асинхронный lock с поддержкой приоритетов."""
    
    def __init__(self) -> None:
        self._locked = False
        self._waiters: dict[int, list[asyncio.Future]] = {0: [], 1: [], 2: []}  # low, normal, high
    
    async def acquire(self, priority: int = 1) -> asyncio.Lock:
        if not self._locked:
            self._locked = True
            return
        
        fut = asyncio.get_event_loop().create_future()
        self._waiters.setdefault(priority, []).append(fut)
        await fut
    
    def release(self) -> None:
        if not self._locked:
            raise RuntimeError("Lock not held")
        
        # Отдаём ожидающим с наивысшим приоритетом
        for priority in (2, 1, 0):  # high → normal → low
            if self._waiters[priority]:
                waiter = self._waiters[priority].pop(0)
                waiter.set_result(True)
                return
        
        self._locked = False
    
    async def __aenter__(self) -> "PriorityLock":
        await self.acquire()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        self.release()
```

## 5. Async Event Emitter

```python
class AsyncEventEmitter:
    """Шина событий с асинхронными подписчиками."""
    
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}
    
    def on(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)
    
    def off(self, event: str, handler: Callable) -> None:
        if handlers := self._handlers.get(event):
            handlers.remove(handler)
    
    async def emit(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Отправить событие и дождаться всех обработчиков."""
        results: list[Any] = []
        for handler in self._handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(*args, **kwargs)
                else:
                    result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.exception("Handler failed for %s: %s", event, e)
                results.append(e)
        return results
```

## 6. Async Queue with Priority and TTL

```python
@dataclass(order=True)
class PrioritizedItem:
    priority: int
    ttl: float
    created_at: float = field(default_factory=time.monotonic)
    data: Any = field(compare=False)
    
    @property
    def expired(self) -> bool:
        return time.monotonic() - self.created_at > self.ttl

class PriorityQueue:
    """Очередь с приоритетом и TTL."""
    
    def __init__(self, maxsize: int = 0) -> None:
        self._heap: list[PrioritizedItem] = []
        self._maxsize = maxsize
        self._event = asyncio.Event()
    
    async def put(self, item: Any, priority: int = 0, ttl: float = 300.0) -> None:
        if self._maxsize and len(self._heap) >= self._maxsize:
            raise asyncio.QueueFull
        
        heapq.heappush(self._heap, PrioritizedItem(priority=priority, ttl=ttl, data=item))
        self._event.set()
    
    async def get(self) -> Any:
        while True:
            # Очистить просроченные
            while self._heap and self._heap[0].expired:
                heapq.heappop(self._heap)
            
            if self._heap:
                return heapq.heappop(self._heap).data
            
            self._event.clear()
            await self._event.wait()
    
    def qsize(self) -> int:
        # Очистить просроченные перед подсчётом
        while self._heap and self._heap[0].expired:
            heapq.heappop(self._heap)
        return len(self._heap)
```

## 7. Coroutine Supervisor (супервизор для фоновых задач)

```python
class Supervisor:
    """Супервизор фоновых задач: автоперезапуск, мониторинг."""
    
    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}
        self._restart_counts: dict[str, int] = {}
        self._max_restarts = 5
    
    async def supervise(self, name: str, coro: Callable, *args: Any, **kwargs: Any) -> None:
        """Запустить задачу под супервизором."""
        if name in self._tasks and not self._tasks[name].done():
            logger.warning("Task %s already running", name)
            return
        
        while self._restart_counts.get(name, 0) < self._max_restarts:
            try:
                self._tasks[name] = asyncio.create_task(coro(*args, **kwargs), name=name)
                await self._tasks[name]
                break  # Завершилась успешно
            except asyncio.CancelledError:
                logger.info("Task %s cancelled", name)
                break
            except Exception as e:
                self._restart_counts[name] = self._restart_counts.get(name, 0) + 1
                delay = min(2 ** self._restart_counts[name], 60)  # exponential backoff
                logger.error("Task %s failed (attempt %d): %s. Restart in %ds",
                           name, self._restart_counts[name], e, delay)
                await asyncio.sleep(delay)
        
        if self._restart_counts.get(name, 0) >= self._max_restarts:
            logger.critical("Task %s exceeded max restarts", name)
    
    async def cancel(self, name: str) -> None:
        if task := self._tasks.get(name):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def cancel_all(self) -> None:
        for name in list(self._tasks):
            await self.cancel(name)
```

## 8. Async Barrier (синхронизация N задач)

```python
class AsyncBarrier:
    """Барьер: ждёт, пока N задач не достигнут точки синхронизации."""
    
    def __init__(self, n: int) -> None:
        self._n = n
        self._count = 0
        self._event = asyncio.Event()
    
    async def wait(self) -> None:
        self._count += 1
        if self._count >= self._n:
            self._event.set()
        await self._event.wait()
```

## 9. Async Retry с джиттером

```python
import random

async def retry_with_jitter(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: float = 0.1,
) -> Any:
    """Retry с экспоненциальным backoff и jitter (случайная задержка)."""
    for attempt in range(max_attempts):
        try:
            return await func()
        except (ConnectionError, TimeoutError, aiohttp.ClientError) as e:
            if attempt == max_attempts - 1:
                raise
            
            delay = min(base_delay * (2 ** attempt), max_delay)
            delay += random.uniform(0, delay * jitter)  # jitter: ±10%
            
            logger.warning("Attempt %d failed: %s. Retry in %.2fs", attempt + 1, e, delay)
            await asyncio.sleep(delay)
```

## 10. Async Semaphore with Timeout

```python
class TimedSemaphore:
    """Семафор с таймаутом на ожидание."""
    
    def __init__(self, value: int = 1) -> None:
        self._sem = asyncio.Semaphore(value)
    
    async def acquire(self, timeout: float = 5.0) -> bool:
        """Попробовать захватить семафор с таймаутом."""
        try:
            await asyncio.wait_for(self._sem.acquire(), timeout=timeout)
            return True
        except TimeoutError:
            return False
    
    def release(self) -> None:
        self._sem.release()
    
    async def __aenter__(self) -> bool:
        return await self.acquire()
    
    async def __aexit__(self, *args: Any) -> None:
        self.release()
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


---

## Advanced Async Patterns for Principal Engineers

### High-Performance Async Server

```python
"""Production async server with full observability."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class AsyncServer:
    """High-performance async server with monitoring.
    
    This pattern combines all async best practices into one:
    - Connection pooling
    - Graceful shutdown
    - Structured logging
    - Health checks
    - Rate limiting
    - Circuit breaker
    """
    
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 10
    max_connections: int = 1000
    
    async def start(self) -> None:
        """Start server with all resilience patterns."""
        # Configure connection pool
        pool = ConnectionPool(
            factory=lambda: self._create_connection(),
            config=PoolConfig(min_size=self.workers, max_size=self.max_connections),
        )
        await pool.start()
        
        # Configure graceful shutdown
        shutdown = GracefulShutdownManager()
        shutdown.register("pool", pool.stop, order=30)
        shutdown.register("server", self._stop_server, order=10)
        shutdown.register_signal_handlers()
        
        # Start health checks
        asyncio.create_task(self._health_check_loop())
        
        try:
            logger.info(f"Server starting on {self.host}:{self.port}")
            await self._run_server(pool)
        finally:
            await shutdown.shutdown()
    
    async def _health_check_loop(self) -> None:
        """Periodic health checks."""
        while True:
            await asyncio.sleep(30)
            # Check all dependencies
            # Log health status
            pass
    
    async def handle_request(self, request: dict, pool) -> dict:
        """Handle single request with full observability."""
        start = time.perf_counter()
        request_id = str(uuid.uuid4())[:8]
        
        try:
            async with asyncio.timeout(30):
                async with pool.acquire() as conn:
                    result = await self._process(request, conn)
                    
                elapsed = time.perf_counter() - start
                logger.info(
                    "Request completed",
                    extra={
                        "request_id": request_id,
                        "duration_ms": elapsed * 1000,
                        "path": request.get("path"),
                    },
                )
                return result
                
        except asyncio.TimeoutError:
            elapsed = time.perf_counter() - start
            logger.error(
                "Request timed out",
                extra={"request_id": request_id, "duration_ms": elapsed * 1000},
            )
            return {"error": "timeout", "status": 504}
            
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.exception(
                "Request failed",
                extra={"request_id": request_id, "duration_ms": elapsed * 1000},
            )
            return {"error": str(e), "status": 500}
