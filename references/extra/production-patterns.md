# Production Patterns

**Боевые паттерны Python для продакшена. Не теория — код, который работает под нагрузкой.**

---

## 1. Connection Pool

```python
"""Пул соединений с автоматическим восстановлением."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")

@dataclass
class Pool(AsyncIterator[T]):
    factory: Any  # Callable[[], Awaitable[T]]
    min_size: int = 2
    max_size: int = 10
    max_idle: float = 60.0  # секунд бездействия до закрытия
    
    _sem: asyncio.Semaphore = field(init=False)
    _idle: list[T] = field(default_factory=list, init=False)
    _used: set[T] = field(default_factory=set, init=False)
    _closed: bool = False
    
    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.max_size)
    
    async def __aenter__(self) -> Pool[T]:
        # Создать минимальное количество соединений
        for _ in range(self.min_size):
            conn = await self.factory()
            self._idle.append(conn)
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        self._closed = True
        for conn in self._idle:
            await self._close_conn(conn)
        for conn in self._used:
            await self._close_conn(conn)
        self._idle.clear()
        self._used.clear()
    
    async def _close_conn(self, conn: T) -> None:
        if hasattr(conn, "close"):
            await conn.close()
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[T]:
        async with self._sem:
            conn = await self._get()
            try:
                yield conn
            except Exception:
                # Закрыть сбойное соединение, создать новое
                await self._close_conn(conn)
                self._used.discard(conn)
                raise
            finally:
                if conn in self._used:
                    self._used.remove(conn)
                    self._idle.append(conn)
    
    async def _get(self) -> T:
        if self._idle:
            return self._idle.pop()
        conn = await self.factory()
        self._used.add(conn)
        return conn
    
    async def __anext__(self) -> T:
        raise StopAsyncIteration

# Использование:
# pool = Pool(factory=lambda: asyncpg.connect(DSN))
# async with pool:
#     async with pool.acquire() as conn:
#         await conn.fetch("SELECT 1")
```

## 2. Retry with Circuit Breaker

```python
"""Retry + Circuit Breaker для внешних вызовов."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable

class CircuitState(Enum):
    CLOSED = auto()     # Работает нормально
    OPEN = auto()       # Сломан, пропускаем
    HALF_OPEN = auto()  # Проверяем, починился ли

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    
    _failures: int = 0
    _state: CircuitState = CircuitState.CLOSED
    _last_failure_time: float = 0.0
    
    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self._state is CircuitState.OPEN:
            if asyncio.get_event_loop().time() - self._last_failure_time > self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            self._failures += 1
            self._last_failure_time = asyncio.get_event_loop().time()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
            raise
        
        # Успех в HALF_OPEN → CLOSED
        if self._state is CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failures = 0
        
        return result

class CircuitBreakerOpenError(Exception):
    """Запрос не выполнен: circuit breaker open."""

def with_retry_and_circuit_breaker(
    max_retries: int = 3,
    base_delay: float = 1.0,
    circuit_breaker: CircuitBreaker | None = None,
) -> Callable:
    """Декоратор: retry + circuit breaker."""
    cb = circuit_breaker or CircuitBreaker()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await cb.call(func, *args, **kwargs)
                except (ConnectionError, TimeoutError, CircuitBreakerOpenError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(base_delay * (2 ** attempt))  # exponential backoff
                    continue
            raise last_error  # type: ignore
        return wrapper
    return decorator
```

## 3. Caching with TTL and Invalidation

```python
"""Кэш с TTL, инвалидацией по тегам и защитой от cache stampede."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

@dataclass
class CacheEntry(Generic[V]):
    value: V
    expires_at: float
    tags: set[str] = field(default_factory=set)

@dataclass
class SmartCache(Generic[K, V]):
    """Кэш с TTL, тегами и защитой от stampede."""
    default_ttl: float = 300.0  # 5 минут
    
    _data: dict[K, CacheEntry[V]] = field(default_factory=dict, init=False)
    _locks: dict[K, asyncio.Lock] = field(default_factory=dict, init=False)
    _tag_index: dict[str, set[K]] = field(default_factory=dict, init=False)
    
    async def get_or_compute(
        self,
        key: K,
        factory: Callable[[], Any],
        ttl: float | None = None,
        tags: list[str] | None = None,
    ) -> V:
        """Получить из кэша или вычислить. Защита от stampede."""
        # Быстрый путь: есть в кэше
        if entry := self._data.get(key):
            if entry.expires_at > time.monotonic():
                return entry.value
        
        # Медленный путь: блокировка, чтобы только один вычислял
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
            # Double-check: мог уже появиться
            if entry := self._data.get(key):
                if entry.expires_at > time.monotonic():
                    return entry.value
            
            # Вычислить
            value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
            entry_ttl = ttl or self.default_ttl
            entry_tags = set(tags or [])
            
            self._data[key] = CacheEntry(
                value=value,
                expires_at=time.monotonic() + entry_ttl,
                tags=entry_tags,
            )
            
            # Индексировать по тегам
            for tag in entry_tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(key)
            
            return value
    
    def invalidate(self, key: K) -> None:
        """Инвалидировать один ключ."""
        if entry := self._data.pop(key, None):
            for tag in entry.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(key)
    
    def invalidate_tag(self, tag: str) -> None:
        """Инвалидировать все ключи с тегом."""
        for key in self._tag_index.pop(tag, set()):
            self._data.pop(key, None)
    
    def invalidate_all(self) -> None:
        """Полная инвалидация."""
        self._data.clear()
        self._tag_index.clear()

# Использование:
# cache = SmartCache[str, dict]()
# users = await cache.get_or_compute(
#     key="users:active",
#     factory=lambda: db.fetch("SELECT * FROM users WHERE active=true"),
#     ttl=60,
#     tags=["users", "active"],
# )
# cache.invalidate_tag("users")  # Когда пользователь изменился
```

## 4. Structured Logging with Context

```python
"""Структурированное логирование с контекстом запроса."""
from __future__ import annotations

import contextvars
import logging
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

# Контекст запроса (thread-safe, asyncio-safe)
_request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
_user_id: contextvars.ContextVar[int | None] = contextvars.ContextVar("user_id", default=None)

def get_request_id() -> str:
    if not (rid := _request_id.get()):
        rid = uuid.uuid4().hex[:12]
        _request_id.set(rid)
    return rid

class StructLogger:
    """Структурированный логгер с автоматическим контекстом."""
    
    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)
    
    def _log(self, level: int, msg: str, **extra: Any) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(level).lower(),
            "logger": self._logger.name,
            "msg": msg,
            "request_id": get_request_id(),
        }
        if uid := _user_id.get():
            record["user_id"] = uid
        record.update(extra)
        self._logger.log(level, json.dumps(record, default=str))
    
    def info(self, msg: str, **kw: Any) -> None:
        self._log(logging.INFO, msg, **kw)
    
    def error(self, msg: str, **kw: Any) -> None:
        self._log(logging.ERROR, msg, **kw)
    
    def warning(self, msg: str, **kw: Any) -> None:
        self._log(logging.WARNING, msg, **kw)

logger = StructLogger("myapp")

# Middleware для установки контекста
async def request_middleware(request: Any, call_next: Callable) -> Any:
    _request_id.set(uuid.uuid4().hex[:12])
    if user := getattr(request, "user", None):
        _user_id.set(user.id)
    logger.info("request_start", method=request.method, path=str(request.url))
    try:
        response = await call_next(request)
        logger.info("request_end", status=response.status_code)
        return response
    except Exception:
        logger.error("request_error")
        raise
```

## 5. Background Task Manager

```python
"""Фоновые задачи с контролем жизненного цикла."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass
class TaskManager:
    """Управление фоновыми задачами."""
    
    _tasks: dict[str, asyncio.Task[Any]] = field(default_factory=dict, init=False)
    _loop: asyncio.AbstractEventLoop | None = None
    
    def __post_init__(self) -> None:
        self._loop = asyncio.get_event_loop()
    
    def create(self, name: str, coro: Awaitable[Any]) -> asyncio.Task[Any]:
        """Создать фоновую задачу."""
        task = self._loop.create_task(coro, name=name)
        task.add_done_callback(lambda t: self._on_done(name, t))
        self._tasks[name] = task
        return task
    
    def _on_done(self, name: str, task: asyncio.Task[Any]) -> None:
        self._tasks.pop(name, None)
        if exc := task.exception():
            logger.error("background_task_failed", task=name, error=str(exc))
    
    async def cancel(self, name: str) -> None:
        """Отменить задачу по имени."""
        if task := self._tasks.get(name):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def cancel_all(self) -> None:
        """Отменить все фоновые задачи."""
        for name in list(self._tasks):
            await self.cancel(name)
    
    @property
    def active_count(self) -> int:
        return len(self._tasks)

# Использование:
# tm = TaskManager()
# tm.create("polling", poll_forever())
# await tm.cancel("polling")
```

## 6. Batch Processor

```python
"""Пакетная обработка с контролем скорости."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")

@dataclass
class BatchProcessor(Generic[T, R]):
    """Обрабатывает элементы пачками с контролем скорости."""
    handler: Callable[[list[T]], Any]  # Обрабатывает пачку
    batch_size: int = 100
    max_concurrency: int = 5
    flush_interval: float = 1.0  # Максимум ждать перед принудительным flush
    
    _queue: asyncio.Queue[T] = field(default_factory=asyncio.Queue, init=False)
    _sem: asyncio.Semaphore = field(init=False)
    _results: list[R] = field(default_factory=list, init=False)
    
    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.max_concurrency)
    
    async def add(self, item: T) -> None:
        """Добавить элемент в очередь обработки."""
        await self._queue.put(item)
    
    async def stream(self) -> AsyncIterator[list[R]]:
        """Поток обработанных пачек."""
        while True:
            batch = await self._collect_batch()
            if not batch:
                break
            async with self._sem:
                results = await self.handler(batch)
                yield results
    
    async def _collect_batch(self) -> list[T]:
        """Собрать пачку элементов (ожидая до flush_interval)."""
        batch: list[T] = []
        try:
            first = await asyncio.wait_for(self._queue.get(), timeout=self.flush_interval)
            batch.append(first)
        except TimeoutError:
            return batch
        
        # Забрать остальные (без ожидания)
        while len(batch) < self.batch_size:
            try:
                item = self._queue.get_nowait()
                batch.append(item)
            except asyncio.QueueEmpty:
                break
        
        return batch

# Использование:
# processor = BatchProcessor[int, int](
#     handler=lambda batch: [x * 2 async for x in batch_processor(batch)],
#     batch_size=50,
# )
# for batch_results in processor.stream():
#     print(batch_results)
```

## 7. Event Bus (in-process)

```python
"""In-process event bus для слабой связанности."""
from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

type EventHandler = Callable[..., Any]

@dataclass
class EventBus:
    """Простая шина событий в процессе."""
    
    _handlers: dict[str, list[EventHandler]] = field(default_factory=dict, init=False)
    
    def on(self, event: str) -> Callable:
        """Декоратор для подписки на событие."""
        def decorator(handler: EventHandler) -> EventHandler:
            if event not in self._handlers:
                self._handlers[event] = []
            self._handlers[event].append(handler)
            return handler
        return decorator
    
    async def emit(self, event: str, **data: Any) -> None:
        """Отправить событие всем подписчикам."""
        if handlers := self._handlers.get(event):
            results = await asyncio.gather(
                *(h(**data) for h in handlers),
                return_exceptions=True,
            )
            for handler, result in zip(handlers, results):
                if isinstance(result, Exception):
                    logger.error("event_handler_failed", event=event, handler=handler.__name__, error=str(result))
    
    def emit_sync(self, event: str, **data: Any) -> None:
        """Синхронная отправка (для скриптов/CLI)."""
        if handlers := self._handlers.get(event):
            for handler in handlers:
                try:
                    handler(**data)
                except Exception as e:
                    logger.error("event_handler_failed", event=event, handler=handler.__name__, error=str(e))

# Использование:
# bus = EventBus()
#
# @bus.on("user.created")
# async def send_welcome_email(user_id: int, email: str) -> None:
#     await email_service.send(email, "Welcome!")
#
# @bus.on("user.created")
# async def log_new_user(user_id: int, **kw: Any) -> None:
#     logger.info("new_user", user_id=user_id)
#
# await bus.emit("user.created", user_id=42, email="user@example.com")
```

## 8. Idempotency Guard

```python
"""Защита от повторной обработки (идемпотентность)."""
from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

@dataclass
class IdempotencyGuard:
    """Гарантирует, что операция выполнится только один раз."""
    storage: Any  # Redis / dict store
    ttl: float = 86400  # 24 часа
    
    def key(self, operation: str, *args: Any, **kwargs: Any) -> str:
        """Создать ключ идемпотентности."""
        raw = json.dumps({"op": operation, "args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return f"idempotency:{hashlib.sha256(raw.encode()).hexdigest()[:16]}"
    
    async def execute(self, operation: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Выполнить с идемпотентностью."""
        id_key = self.key(operation, *args, **kwargs)
        
        # Уже было?
        if cached := await self.storage.get(id_key):
            return json.loads(cached)["result"]
        
        # Выполнить
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        # Сохранить результат
        await self.storage.setex(id_key, self.ttl, json.dumps({"result": result}, default=str))
        
        return result

# Использование:
# guard = IdempotencyGuard(storage=redis_client)
# result = await guard.execute("charge", charge_user, user_id=42, amount=100)
```

## 9. State Machine

```python
"""Finit state machine для бизнес-процессов."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Self

class OrderState(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    PROCESSING = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

@dataclass
class StateMachine:
    """Простая state machine."""
    
    transitions: dict[Enum, dict[Enum, bool]] = field(default_factory=dict)
    
    def allow(self, from_state: Enum, to_state: Enum) -> Self:
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if to_state not in self.transitions.get(from_state, {}):
            self.transitions[from_state][to_state] = True
        return self
    
    def can(self, current: Enum, target: Enum) -> bool:
        return self.transitions.get(current, {}).get(target, False)
    
    def validate(self, current: Enum, target: Enum) -> None:
        if not self.can(current, target):
            raise ValueError(f"Transition {current.name} → {target.name} not allowed")

# Определение transitions
order_sm = (StateMachine()
    .allow(OrderState.PENDING, OrderState.CONFIRMED)
    .allow(OrderState.PENDING, OrderState.CANCELLED)
    .allow(OrderState.CONFIRMED, OrderState.PROCESSING)
    .allow(OrderState.CONFIRMED, OrderState.CANCELLED)
    .allow(OrderState.PROCESSING, OrderState.SHIPPED)
    .allow(OrderState.PROCESSING, OrderState.CANCELLED)
    .allow(OrderState.SHIPPED, OrderState.DELIVERED)
)

# Использование:
# order_sm.validate(order.state, OrderState.SHIPPED)
# order.state = OrderState.SHIPPED
```

## 10. Query Object (instead of raw SQL everywhere)

```python
"""Типизированные запросы вместо raw SQL."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self

@dataclass
class Query:
    """Построитель запросов с типизацией."""
    
    filters: list[tuple[str, str, Any]] | None = None
    sort: tuple[str, bool] | None = None  # (field, asc)
    limit: int | None = None
    offset: int = 0
    
    def where(self, field: str, op: str = "=", value: Any = None) -> Self:
        if self.filters is None:
            self.filters = []
        self.filters.append((field, op, value))
        return self
    
    def order_by(self, field: str, asc: bool = True) -> Self:
        self.sort = (field, asc)
        return self
    
    def with_limit(self, limit: int) -> Self:
        self.limit = limit
        return self
    
    def with_offset(self, offset: int) -> Self:
        self.offset = offset
        return self

# Repository использует Query
class UserRepository:
    async def find(self, query: Query) -> list[User]:
        stmt = select(User)
        if query.filters:
            stmt = stmt.where(*(getattr(User, f) == v for f, op, v in query.filters if op == "="))
        if query.sort:
            col = getattr(User, query.sort[0])
            stmt = stmt.order_by(col.asc() if query.sort[1] else col.desc())
        if query.limit:
            stmt = stmt.limit(query.limit).offset(query.offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

# Использование:
# users = await repo.find(
#     Query()
#     .where("is_active", "=", True)
#     .order_by("created_at", asc=False)
#     .with_limit(20)
#     .with_offset(0)
# )
```


---

## 3. Retry with Exponential Backoff + Jitter (Production-Grade)

```python
"""Retry стратегия для продакшена — полная версия."""
from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")

@dataclass
class RetryConfig:
    """Конфигурация retry."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    jitter: bool = True
    jitter_range: tuple[float, float] = (0.0, 1.0)
    
    # Какие ошибки retry
    retryable_exceptions: tuple = (ConnectionError, TimeoutError, OSError)
    # Какие не retry
    non_retryable_exceptions: tuple = (ValueError, TypeError, KeyError, ZeroDivisionError)


async def retry_with_backoff[T](
    fn: Callable[..., Awaitable[T]],
    *args: Any,
    config: RetryConfig | None = None,
    **kwargs: Any,
) -> T:
    """Универсальный retry с exponential backoff + jitter.
    
    Battle Scar: Без jitter все ретраи приходили одновременно — 
    создавали spike нагрузки. С random jitter — равномерное распределение.
    """
    cfg = config or RetryConfig()
    last_exception: Exception | None = None
    
    for attempt in range(cfg.max_retries + 1):
        try:
            return await fn(*args, **kwargs)
        except cfg.non_retryable_exceptions:
            # Не retry — сразу raise
            raise
        except cfg.retryable_exceptions as e:
            last_exception = e
            if attempt == cfg.max_retries:
                break
            
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s...
            delay = min(cfg.base_delay * (2 ** attempt), cfg.max_delay)
            
            # Jitter: random 0-1s дополнительно
            if cfg.jitter:
                jitter_val = random.uniform(*cfg.jitter_range)
                delay += jitter_val
            
            print(f"Retry {attempt + 1}/{cfg.max_retries} after {delay:.2f}s")
            await asyncio.sleep(delay)
    
    raise RetryExhaustedError(f"All {cfg.max_retries} retries failed") from last_exception


# Использование:
async def fetch_data(url: str) -> dict:
    return await retry_with_backoff(
        http_client.get,
        url,
        config=RetryConfig(max_retries=5, base_delay=0.5, max_delay=10.0),
    )
```

## 4. Circuit Breaker (Full Implementation)

```python
"""Circuit Breaker с тремя состояниями и half-open recovery."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = auto()      # Работает нормально
    OPEN = auto()        # Сломан — отклоняем запросы
    HALF_OPEN = auto()   # Пробуем восстановиться


@dataclass
class CircuitBreakerConfig:
    """Настройки circuit breaker."""
    failure_threshold: int = 5          # Открыть после N ошибок
    recovery_timeout: float = 30.0      # Через N секунд попробовать half-open
    half_open_max_calls: int = 3        # В half-open максимум N запросов
    success_threshold: int = 2          # Закрыть после N успехов в half-open


class CircuitBreaker(Generic[T]):
    """Circuit Breaker для защиты внешних вызовов.
    
    Battle Scar: Без circuit breaker при падении БД все сервисы в каскаде
    падали за 30 секунд. С ним — грациозная деградация за 5 секунд.
    """
    
    def __init__(self, config: CircuitBreakerConfig | None = None):
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        self._mutex = asyncio.Lock()
    
    async def call(
        self,
        fn: Callable[..., Awaitable[T]],
        fallback: Callable[..., Awaitable[T]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Вызвать функцию с circuit breaker."""
        
        async with self._mutex:
            if self._state == CircuitState.OPEN:
                if time.monotonic() - self._last_failure_time >= self._config.recovery_timeout:
                    logger.info("Circuit half-open: trying recovery")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self._success_count = 0
                else:
                    logger.warning("Circuit open — using fallback")
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitOpenError("Circuit breaker is open")
            
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self._config.half_open_max_calls:
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise CircuitOpenError("Half-open: max calls reached")
                self._half_open_calls += 1
        
        try:
            result = await fn(*args, **kwargs)
            
            async with self._mutex:
                if self._state == CircuitState.HALF_OPEN:
                    self._success_count += 1
                    if self._success_count >= self._config.success_threshold:
                        logger.info("Circuit closed: recovery successful")
                        self._state = CircuitState.CLOSED
                        self._failure_count = 0
                        self._success_count = 0
                else:
                    self._failure_count = 0
            return result
            
        except Exception as e:
            async with self._mutex:
                self._failure_count += 1
                self._last_failure_time = time.monotonic()
                
                if self._failure_count >= self._config.failure_threshold:
                    logger.error(f"Circuit open: {self._failure_count} failures")
                    self._state = CircuitState.OPEN
                
                if fallback:
                    return await fallback(*args, **kwargs)
            raise
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    async def reset(self) -> None:
        async with self._mutex:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0


class CircuitOpenError(Exception):
    """Circuit breaker is open — request rejected."""
    pass


class RetryExhaustedError(Exception):
    """All retry attempts exhausted."""
    pass
```

## 5. Connection Pool with Heartbeat

```python
"""Connection Pool с health check и heartbeat."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class PoolConfig:
    min_size: int = 2
    max_size: int = 20
    max_idle_time: float = 60.0
    max_lifetime: float = 3600.0
    acquire_timeout: float = 5.0
    heartbeat_interval: float = 15.0
    retry_on_failure: bool = True


@dataclass
class PooledConnection(Generic[T]):
    conn: T
    created_at: float = field(default_factory=time.monotonic)
    last_used: float = field(default_factory=time.monotonic)
    healthy: bool = True


class ConnectionPool(Generic[T]):
    """Production-grade connection pool with heartbeat and health checks.
    
    Battle Scar: Без heartbeat при долгом простое connections 
    умирали (NAT timeout 60s). С heartbeat каждые 15s — zero stale connections.
    """
    
    def __init__(
        self,
        factory: Callable[[], Awaitable[T]],
        close_fn: Callable[[T], Awaitable[None]] | None = None,
        health_check: Callable[[T], Awaitable[bool]] | None = None,
        config: PoolConfig | None = None,
    ):
        self._factory = factory
        self._close = close_fn or (lambda c: c.close() if hasattr(c, 'close') else None)
        self._health_check = health_check
        self._config = config or PoolConfig()
        
        self._idle: list[PooledConnection[T]] = []
        self._used: set[PooledConnection[T]] = set()
        self._sem = asyncio.Semaphore(self._config.max_size)
        self._running = False
        self._heartbeat_task: asyncio.Task | None = None
    
    async def start(self) -> None:
        """Инициализация пула."""
        self._running = True
        for _ in range(self._config.min_size):
            conn = await self._create_connection()
            self._idle.append(conn)
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info(f"Pool started: {self._config.min_size} initial connections")
    
    async def stop(self) -> None:
        """Остановка пула."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        for conn in self._idle:
            await self._close(conn.conn)
        for conn in self._used:
            await self._close(conn.conn)
        
        self._idle.clear()
        self._used.clear()
        logger.info("Pool stopped")
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[T]:
        """Получить соединение из пула."""
        try:
            async with asyncio.timeout(self._config.acquire_timeout):
                async with self._sem:
                    conn = await self._get_connection()
                    try:
                        yield conn.conn
                    except Exception:
                        # Сбойное соединение — закрыть, создать новое
                        conn.healthy = False
                        await self._close(conn.conn)
                        self._used.discard(conn)
                        raise
                    finally:
                        if conn in self._used:
                            self._used.remove(conn)
                            conn.last_used = time.monotonic()
                            if conn.healthy:
                                self._idle.append(conn)
        except asyncio.TimeoutError:
            raise PoolTimeoutError(
                f"Acquire timeout after {self._config.acquire_timeout}s"
            )
    
    async def _create_connection(self) -> PooledConnection[T]:
        conn = await self._factory()
        return PooledConnection(conn=conn)
    
    async def _get_connection(self) -> PooledConnection[T]:
        # Clean stale connections
        now = time.monotonic()
        self._idle = [
            c for c in self._idle
            if (now - c.last_used < self._config.max_idle_time and
                now - c.created_at < self._config.max_lifetime)
        ]
        
        if self._idle:
            conn = self._idle.pop()
            # Health check before returning
            if self._health_check:
                if not await self._health_check(conn.conn):
                    await self._close(conn.conn)
                    conn = await self._create_connection()
        else:
            conn = await self._create_connection()
        
        self._used.add(conn)
        conn.last_used = time.monotonic()
        return conn
    
    async def _heartbeat_loop(self) -> None:
        """Периодическая проверка соединений."""
        while self._running:
            try:
                await asyncio.sleep(self._config.heartbeat_interval)
                await self._check_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    async def _check_connections(self) -> None:
        """Проверить здоровье idle соединений."""
        healthy: list[PooledConnection[T]] = []
        for conn in self._idle:
            if self._health_check:
                try:
                    ok = await self._health_check(conn.conn)
                    if ok:
                        healthy.append(conn)
                    else:
                        await self._close(conn.conn)
                except Exception:
                    await self._close(conn.conn)
            else:
                healthy.append(conn)
        
        self._idle = healthy
        
        # Maintain minimum connections
        while len(self._idle) < self._config.min_size:
            conn = await self._create_connection()
            self._idle.append(conn)
    
    @property
    def idle_count(self) -> int:
        return len(self._idle)
    
    @property
    def used_count(self) -> int:
        return len(self._used)
    
    @property
    def total_count(self) -> int:
        return self.idle_count + self.used_count


class PoolTimeoutError(asyncio.TimeoutError):
    """Timeout waiting for pool connection."""
    pass


# Использование с asyncpg:
# pool = ConnectionPool(
#     factory=lambda: asyncpg.connect(DSN),
#     health_check=lambda c: c.fetch("SELECT 1"),
#     config=PoolConfig(min_size=5, max_size=30),
# )
# await pool.start()
# async with pool.acquire() as conn:
#     await conn.fetch("SELECT * FROM users")
# await pool.stop()
```

## 6. Rate Limiter (Token Bucket + Sliding Window)

```python
"""Rate Limiter — защита от abuse и перегрузки."""
from __future__ import annotations

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


class RateLimitStrategy(Enum):
    TOKEN_BUCKET = auto()
    SLIDING_WINDOW = auto()
    FIXED_WINDOW = auto()


@dataclass
class RateLimit:
    requests: int
    window: float = 60.0  # seconds
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET


@dataclass
class TokenBucket:
    """Token Bucket алгоритм для rate limiting."""
    capacity: int
    refill_rate: float  # tokens per second
    refill_amount: int = 1
    tokens: float = field(init=False)
    last_refill: float = field(default_factory=time.monotonic)
    
    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)
    
    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimiter:
    """Rate limiter для защиты API и внешних вызовов.
    
    Battle Scar: Без rate limiter один клиент мог положить весь сервис
    100K запросами в секунду. С лимитом 1000/сек — zero impact.
    """
    
    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}
        self._windows: dict[str, list[float]] = defaultdict(list)
    
    def add_limit(self, key: str, limit: RateLimit) -> None:
        if limit.strategy == RateLimitStrategy.TOKEN_BUCKET:
            self._buckets[key] = TokenBucket(
                capacity=limit.requests,
                refill_rate=limit.requests / limit.window,
            )
    
    def check(self, key: str, cost: int = 1) -> bool:
        bucket = self._buckets.get(key)
        if bucket:
            return bucket.consume(cost)
        return True
    
    async def wait_if_needed(self, key: str, cost: int = 1) -> None:
        """Блокирующая версия — ждёт, пока можно."""
        while not self.check(key, cost):
            await asyncio.sleep(0.1)
    
    def remaining(self, key: str) -> float:
        bucket = self._buckets.get(key)
        if bucket:
            now = time.monotonic()
            elapsed = now - bucket.last_refill
            return min(bucket.capacity, bucket.tokens + elapsed * bucket.refill_rate)
        return float('inf')


# Использование:
# limiter = RateLimiter()
# limiter.add_limit("api:users", RateLimit(requests=100, window=60))
# 
# if limiter.check("api:users"):
#     await call_api()
# else:
#     raise HTTPException(status_code=429)
```

## 7. Health Check System

```python
"""Система health checks для микросервиса."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    error: str | None = None
    details: dict | None = None


@dataclass
class HealthChecker:
    """Health check aggregator для микросервиса.
    
    Используется в /health/ready и /health/live эндпоинтах.
    
    Battle Scar: k8s readiness probe без проверки зависимостей —
    сервис отвечал 200, но БД была мертва. 500 ошибок на каждый запрос.
    """
    checks: dict[str, Callable[[], Awaitable[HealthCheckResult]]] = field(default_factory=dict)
    timeout: float = 5.0
    
    def register(self, name: str, check_fn: Callable[[], Awaitable[HealthCheckResult]]) -> None:
        self.checks[name] = check_fn
    
    async def check_all(self) -> list[HealthCheckResult]:
        results: list[HealthCheckResult] = []
        for name, check_fn in self.checks.items():
            try:
                async with asyncio.timeout(self.timeout):
                    result = await check_fn()
            except asyncio.TimeoutError:
                result = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=f"timeout after {self.timeout}s",
                )
            except Exception as e:
                result = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=str(e),
                )
            results.append(result)
        return results
    
    async def is_healthy(self) -> bool:
        """True if all checks are healthy."""
        results = await self.check_all()
        return all(r.status == HealthStatus.HEALTHY for r in results)
    
    async def is_ready(self) -> bool:
        """True if ready to serve traffic (no unhealthy checks)."""
        results = await self.check_all()
        return all(r.status != HealthStatus.UNHEALTHY for r in results)


# Пример:
# checker = HealthChecker()
# checker.register("database", check_database)
# checker.register("redis", check_redis)
# checker.register("kafka", check_kafka)
# 
# async def check_database() -> HealthCheckResult:
#     start = time.monotonic()
#     try:
#         async with pool.acquire() as conn:
#             await conn.fetch("SELECT 1")
#         return HealthCheckResult("database", HealthStatus.HEALTHY,
#                                 latency_ms=(time.monotonic() - start) * 1000)
#     except Exception as e:
#         return HealthCheckResult("database", HealthStatus.UNHEALTHY, error=str(e))
```

## 8. Graceful Shutdown with Dependency Order

```python
"""Graceful shutdown с учётом зависимостей между сервисами."""
from __future__ import annotations

import asyncio
import signal
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field


@dataclass
class ShutdownHook:
    """Хук для graceful shutdown."""
    name: str
    handler: Callable[[], Awaitable[None]]
    order: int = 0  # Меньше = раньше
    timeout: float = 10.0
    critical: bool = True


class ShutdownManager:
    """Управление graceful shutdown с зависимостями.
    
    Battle Scar: Однажды закрыли DB pool до HTTP сервера —
    in-flight запросы упали с 500. Порядок shutdown критичен.
    """
    
    def __init__(self):
        self._hooks: list[ShutdownHook] = []
        self._shutdown_in_progress = False
        self._signal_handlers: list = []
    
    def register(self, hook: ShutdownHook) -> None:
        self._hooks.append(hook)
    
    def register_signal_handlers(self) -> None:
        """Register SIGTERM/SIGINT handlers."""
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            handler = loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(self.shutdown(s)),
            )
            self._signal_handlers.append((sig, handler))
    
    async def shutdown(self, sig: signal.Signals | None = None) -> None:
        """Execute shutdown hooks in order (reverse dependency order)."""
        if self._shutdown_in_progress:
            return
        self._shutdown_in_progress = True
        
        logger.info(f"Shutdown initiated (signal: {sig})")
        
        # Сортируем hooks по order (меньше = раньше)
        # Для shutdown — обратный порядок
        sorted_hooks = sorted(self._hooks, key=lambda h: h.order, reverse=True)
        
        failed = False
        for hook in sorted_hooks:
            try:
                async with asyncio.timeout(hook.timeout):
                    logger.info(f"Shutdown hook: {hook.name}")
                    await hook.handler()
            except asyncio.TimeoutError:
                logger.error(f"Shutdown hook {hook.name} timed out ({hook.timeout}s)")
                if hook.critical:
                    failed = True
            except Exception as e:
                logger.error(f"Shutdown hook {hook.name} failed: {e}")
                if hook.critical:
                    failed = True
        
        if failed:
            logger.error("Shutdown completed with errors")
        else:
            logger.info("Shutdown completed successfully")
    
    @property
    def is_shutting_down(self) -> bool:
        return self._shutdown_in_progress


# Использование:
# manager = ShutdownManager()
# manager.register(ShutdownHook("http_server", http_server.stop, order=10))
# manager.register(ShutdownHook("kafka_consumer", kafka_consumer.stop, order=20))
# manager.register(ShutdownHook("db_pool", pool.stop, order=30, critical=True))
# manager.register_signal_handlers()
```

## 9. Feature Flags

```python
"""Feature flags — безопасный rollout фич."""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from enum import Enum


class RolloutStrategy(Enum):
    PERCENTAGE = "percentage"      # X% пользователей
    USER_ID = "user_id"            # Конкретные user_id
    ENVIRONMENT = "environment"    # prod/staging/dev
    COHORT = "cohort"              # A/B тест


@dataclass
class FeatureFlag:
    name: str
    enabled: bool = False
    strategy: RolloutStrategy = RolloutStrategy.PERCENTAGE
    percentage: float = 0.0  # 0.0 - 1.0
    user_ids: set[str] = field(default_factory=set)
    environments: set[str] = field(default_factory=set)
    description: str = ""


class FeatureFlagSystem:
    """Feature flag система для постепенного rollout.
    
    Battle Scar: Новый алгоритм recommendations выкатили сразу на 100% —
    latency выросла в 10 раз. Rollback занял 15 минут.
    С feature flags — выкатка на 1%, 5%, 25%, 50%, 100% с мониторингом.
    """
    
    def __init__(self):
        self._flags: dict[str, FeatureFlag] = {}
    
    def add_flag(self, flag: FeatureFlag) -> None:
        self._flags[flag.name] = flag
    
    def is_enabled(self, flag_name: str, user_id: str | None = None) -> bool:
        flag = self._flags.get(flag_name)
        if not flag:
            return False
        if not flag.enabled:
            return False
        
        match flag.strategy:
            case RolloutStrategy.PERCENTAGE:
                if user_id:
                    # Consistent hashing для user-based rollout
                    hash_val = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
                    return (hash_val % 100) / 100 < flag.percentage
                return random.random() < flag.percentage
            
            case RolloutStrategy.USER_ID:
                return user_id in flag.user_ids if user_id else False
            
            case RolloutStrategy.ENVIRONMENT:
                import os
                return os.getenv("ENV", "dev") in flag.environments
            
            case RolloutStrategy.COHORT:
                return user_id and hash(user_id) % 2 == 0
        
        return False
    
    def enable_for_percentage(self, flag_name: str, pct: float) -> None:
        flag = self._flags.get(flag_name)
        if flag:
            flag.percentage = pct
            flag.enabled = pct > 0
    
    def get_all_flags(self) -> dict[str, bool]:
        return {name: flag.enabled for name, flag in self._flags.items()}


# Использование:
# flags = FeatureFlagSystem()
# flags.add_flag(FeatureFlag(
#     name="new_recommendations",
#     strategy=RolloutStrategy.PERCENTAGE,
#     percentage=0.01,  # 1%
#     description="Новый алгоритм рекомендаций"
# ))
# 
# if flags.is_enabled("new_recommendations", user_id=user.id):
#     return new_recommendations(user)
# else:
#     return old_recommendations(user)
```

## 10. Saga Pattern (Choreography-based)

```python
"""Saga pattern для distributed transactions."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SagaStep:
    name: str
    action: Callable[[], Awaitable[None]]
    compensate: Callable[[], Awaitable[None]] | None = None
    retry_count: int = 3
    timeout: float = 30.0


class Saga:
    """Saga orchestrator для распределённых транзакций.
    
    Battle Scar: Без Saga при ошибке в шаге 3 из 5 — 
    данные оставались в несогласованном состоянии.
    Saga гарантирует eventual consistency.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._steps: list[SagaStep] = []
        self._completed: list[SagaStep] = []
    
    def add_step(self, step: SagaStep) -> None:
        self._steps.append(step)
    
    async def execute(self) -> None:
        """Execute saga with compensation on failure."""
        for step in self._steps:
            try:
                async with asyncio.timeout(step.timeout):
                    for attempt in range(step.retry_count):
                        try:
                            await step.action()
                            self._completed.append(step)
                            break
                        except Exception as e:
                            if attempt == step.retry_count - 1:
                                raise
                            await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Saga {self.name}: step '{step.name}' failed: {e}")
                await self._compensate()
                raise SagaFailedError(f"Saga {self.name} failed at step '{step.name}'")
    
    async def _compensate(self) -> None:
        """Rollback completed steps in reverse order."""
        logger.info(f"Saga {self.name}: compensating {len(self._completed)} steps")
        for step in reversed(self._completed):
            if step.compensate:
                try:
                    await step.compensate()
                    logger.info(f"Saga {self.name}: compensated '{step.name}'")
                except Exception as e:
                    logger.error(f"Saga {self.name}: compensate '{step.name}' failed: {e}")


class SagaFailedError(Exception):
    pass


# Использование:
# saga = Saga("create_order")
# saga.add_step(SagaStep(
#     name="reserve_inventory",
#     action=lambda: inventory.reserve(order.items),
#     compensate=lambda: inventory.unreserve(order.items),
# ))
# saga.add_step(SagaStep(
#     name="charge_payment",
#     action=lambda: payment.charge(order.total),
#     compensate=lambda: payment.refund(order.total),
# ))
# saga.add_step(SagaStep(
#     name="send_notification",
#     action=lambda: notification.send(order.user_id, "Order created"),
#     compensate=None,  # No need to compensate notification
# ))
# await saga.execute()
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
