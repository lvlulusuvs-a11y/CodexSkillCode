# 🏭 Production-паттерны, которые я таскаю с собой в каждый проект

Это не теория из книг. Это код, который я реально таскаю из проекта в проект вот уже много лет. Паттерны, которые спасали мне задницу в production.

## 1. Result Type — явные ошибки вместо исключений

Исключения — это goto. Они разрывают поток выполнения и ты никогда не знаешь, кто их поймает.

Я использую Result type для ожидаемых ошибок.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Callable
from enum import Enum

T = TypeVar('T')
E = TypeVar('E')


class ErrorLevel(Enum):
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Error(Generic[E]):
    """Типизированная ошибка с контекстом."""
    code: str
    message: str
    level: ErrorLevel = ErrorLevel.ERROR
    details: dict | None = None
    
    @classmethod
    def not_found(cls, entity: str, id: str) -> Error:
        return cls(
            code="NOT_FOUND",
            message=f"{entity} with id {id} not found",
            level=ErrorLevel.WARN,
        )
    
    @classmethod
    def validation(cls, field: str, reason: str) -> Error:
        return cls(
            code="VALIDATION_ERROR",
            message=f"Validation failed for {field}: {reason}",
        )
    
    @classmethod
    def unavailable(cls, service: str) -> Error:
        return cls(
            code="SERVICE_UNAVAILABLE",
            message=f"{service} is not available",
            level=ErrorLevel.CRITICAL,
        )


Result = T | Error  # Простая union type, без классов-обёрток


def match(result: Result[T, E], on_ok: Callable[[T], None], on_err: Callable[[Error], None]):
    """Pattern matching для Result."""
    if isinstance(result, Error):
        on_err(result)
    else:
        on_ok(result)


# Использование
def get_user(db, user_id: str) -> Result[User, Error]:
    user = db.query(User).get(user_id)
    if user is None:
        return Error.not_found("User", user_id)
    if not user.is_active:
        return Error.validation("is_active", "User is deactivated")
    return user


def process_order(order_id: str) -> Result[Order, Error]:
    user = get_user(db, user_id)
    if isinstance(user, Error):
        return user  # Пробрасываем наверх
    
    # user — точно User, type-safe
    order = create_order(user, ...)
    return order


# На уровне API Handler
def handler(request):
    result = process_order(request.order_id)
    if isinstance(result, Error):
        if result.level == ErrorLevel.WARN:
            return HTTPResponse(404, {"error": result.message})
        return HTTPResponse(500, {"error": result.message})
    return HTTPResponse(200, result.to_dict())
```

**Почему это лучше исключений:**
- Типизировано — я знаю, какие ошибки могут быть
- Явно — я вижу, где ошибка обрабатывается
- Композируемо — можно пробрасывать наверх без try/except

## 2. Retry с exponential backoff и jitter

Базовый паттерн для всех внешних вызовов.

```python
import asyncio
import random
from functools import wraps
from typing import Type, Callable


class RetryableError(Exception):
    """Ошибка, которую можно ретраить."""
    pass


class NonRetryableError(Exception):
    """Ошибка, которую ретраить бесполезно."""
    pass


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    jitter: float = 0.1,
    retryable_exceptions: tuple[Type[Exception], ...] = (RetryableError, TimeoutError, ConnectionError),
):
    """Декоратор для retry с exponential backoff и jitter.
    
    Args:
        max_attempts: Максимум попыток (включая первую)
        base_delay: Базовая задержка между ретраями (секунды)
        max_delay: Максимальная задержка
        jitter: Случайная вариация задержки (0.1 = ±10%)
        retryable_exceptions: Какие исключения ретраить
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except NonRetryableError:
                    raise  # Не ретраим
                except retryable_exceptions as e:
                    last_error = e
                    
                    if attempt == max_attempts - 1:
                        raise  # Это последняя попытка
                    
                    # Exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    # Jitter
                    if jitter > 0:
                        delay += random.uniform(-delay * jitter, delay * jitter)
                    
                    logger.warning(
                        "Attempt %d/%d failed: %s. Retrying in %.2fs",
                        attempt + 1, max_attempts, e, delay,
                    )
                    await asyncio.sleep(delay)
            
            raise last_error  # type: ignore
        
        return wrapper
    
    return decorator


# Использование
@retry(max_attempts=3, base_delay=1.0, max_delay=10.0)
async def call_payment_api(order_id: str, amount: Money) -> PaymentResult:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://payment.example.com/charge",
            json={"order_id": order_id, "amount": str(amount)},
            timeout=5.0,
        )
        if response.status_code == 400:
            raise NonRetryableError(f"Invalid payment request: {response.text}")
        if response.status_code >= 500:
            raise RetryableError(f"Payment service error: {response.status_code}")
        return PaymentResult.from_json(response.json())
```

## 3. Bulkhead — изоляция ресурсов

Когда один сбойный компонент валит весь сервис.

```python
import asyncio
from dataclasses import dataclass, field


@dataclass
class Bulkhead:
    """Изолятор ресурсов. Ограничивает конкурентные вызовы к внешнему сервису.
    
    Представь, что у тебя 3 внешних сервиса: Payments, Inventory, Notifications.
    Если Payments начал тормозить — он не должен забрать все потоки и 
    положить Inventory и Notifications.
    """
    name: str
    max_concurrent: int = 10
    queue_size: int = 20
    
    _semaphore: asyncio.Semaphore = field(init=False)
    _queue_dropped: int = 0
    
    def __post_init__(self):
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
    
    async def execute(self, func, *args, **kwargs):
        """Выполняет функцию с ограничением по конкурентности."""
        if self._semaphore.locked() and self._queue_dropped > self.queue_size:
            self._queue_dropped += 1
            raise BulkheadRejectedError(f"{self.name}: queue full")
        
        async with self._semaphore:
            self._queue_dropped = max(0, self._queue_dropped - 1)
            return await func(*args, **kwargs)


# Использование
class Service:
    def __init__(self):
        self._payment_bulkhead = Bulkhead("payment", max_concurrent=5)
        self._inventory_bulkhead = Bulkhead("inventory", max_concurrent=10)
        self._notification_bulkhead = Bulkhead("notification", max_concurrent=3)
    
    async def create_order(self, request):
        # Каждый внешний вызов идёт через свой bulkhead
        payment = await self._payment_bulkhead.execute(
            self._payment_client.charge, request.payment
        )
        inventory = await self._inventory_bulkhead.execute(
            self._inventory_client.reserve, request.items
        )
        # ...
```

## 4. Saga — распределённые транзакции

Когда одна операция затрагивает несколько сервисов, и нужно уметь откатываться.

```python
from dataclasses import dataclass, field
from typing import Callable, Awaitable
import asyncio


@dataclass
class SagaStep:
    name: str
    forward: Callable[[], Awaitable[None]]
    compensate: Callable[[], Awaitable[None]] | None = None


class SagaError(Exception):
    def __init__(self, message: str, failed_step: str):
        self.failed_step = failed_step
        super().__init__(f"Saga failed at '{failed_step}': {message}")


class Saga:
    """Saga паттерн для распределённых транзакций.
    
    Пример: создание заказа требует:
    1. Зарезервировать товар (Inventory Service)
    2. Списать деньги (Payment Service) 
    3. Отправить уведомление (Notification Service)
    
    Если шаг 2 упал — выполняем компенсацию для шага 1.
    """
    
    def __init__(self, name: str):
        self.name = name
        self._steps: list[SagaStep] = []
    
    def add_step(self, step: SagaStep):
        self._steps.append(step)
    
    async def execute(self):
        """Выполняет сагу с компенсациями при ошибках."""
        completed: list[SagaStep] = []
        
        for step in self._steps:
            try:
                logger.info("Saga %s: executing step '%s'", self.name, step.name)
                await step.forward()
                completed.append(step)
            except Exception as e:
                logger.error(
                    "Saga %s: step '%s' failed: %s. Starting compensation...",
                    self.name, step.name, e,
                )
                # Компенсация в обратном порядке
                for completed_step in reversed(completed):
                    if completed_step.compensate:
                        try:
                            logger.info(
                                "Saga %s: compensating step '%s'",
                                self.name, completed_step.name,
                            )
                            await completed_step.compensate()
                        except Exception as comp_error:
                            logger.critical(
                                "Saga %s: compensation for step '%s' also failed: %s",
                                self.name, completed_step.name, comp_error,
                            )
                raise SagaError(str(e), step.name)
        
        logger.info("Saga %s: completed successfully", self.name)


# Использование
async def create_order_saga(order_data: dict):
    saga = Saga("create_order")
    
    saga.add_step(SagaStep(
        name="reserve_inventory",
        forward=lambda: inventory_client.reserve(order_data["items"]),
        compensate=lambda: inventory_client.release(order_data["items"]),
    ))
    
    saga.add_step(SagaStep(
        name="charge_payment",
        forward=lambda: payment_client.charge(order_data["total"]),
        compensate=lambda: payment_client.refund(order_data["total"]),
    ))
    
    saga.add_step(SagaStep(
        name="send_notification",
        forward=lambda: notification_client.send_order_confirmation(order_data["user_id"]),
        compensate=None,  # Отправку уведомления не откатываем
    ))
    
    await saga.execute()
```

## 5. Feature Flags — убийца кода навсегда

```python
from dataclasses import dataclass
from enum import Enum
import json


class FeatureStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ROLLOUT = "rollout"  # Постепенный rollout


@dataclass
class FeatureFlag:
    """Фича-флаг с поддержкой rollout."""
    name: str
    status: FeatureStatus
    rollout_percentage: int = 0  # 0-100
    
    def is_enabled(self, user_id: str | None = None) -> bool:
        if self.status == FeatureStatus.DISABLED:
            return False
        if self.status == FeatureStatus.ENABLED:
            return True
        if self.status == FeatureStatus.ROLLOUT and user_id:
            # Детерминированный rollout на основе user_id
            return hash(f"{self.name}:{user_id}") % 100 < self.rollout_percentage
        return False


class FeatureFlags:
    """Централизованное управление фичами."""
    
    def __init__(self, flags_file: str = "feature_flags.json"):
        self._flags: dict[str, FeatureFlag] = {}
        self._load(flags_file)
    
    def _load(self, path: str):
        with open(path) as f:
            data = json.load(f)
        for name, config in data.items():
            self._flags[name] = FeatureFlag(
                name=name,
                status=FeatureStatus(config["status"]),
                rollout_percentage=config.get("rollout_percentage", 0),
            )
    
    def is_enabled(self, flag_name: str, user_id: str | None = None) -> bool:
        flag = self._flags.get(flag_name)
        if not flag:
            return False  # Неизвестный флаг = выключено
        return flag.is_enabled(user_id)


# Использование
flags = FeatureFlags()

async def get_dashboard_data(user_id: str):
    # Новая версия дашборда — только для 10% пользователей
    if flags.is_enabled("new_dashboard", user_id):
        return await new_dashboard(user_id)
    return await old_dashboard(user_id)
```

## 6. Circuit Breaker с половиным состоянием

```python
from dataclasses import dataclass
from enum import Enum
import asyncio
import time


class CircuitState(Enum):
    CLOSED = "closed"       # Работает нормально
    OPEN = "open"           # Отказ, запросы блокируются
    HALF_OPEN = "half_open" # Пробуем восстановиться


class CircuitBreakerError(Exception):
    """Сервис недоступен (circuit breaker open)."""
    pass


@dataclass
class CircuitBreaker:
    """Circuit breaker с автоматическим восстановлением."""
    name: str
    threshold: int = 5           # Сколько ошибок до открытия
    recovery_timeout: float = 30.0  # Через сколько пробовать восстановиться
    half_open_max_requests: int = 3  # Сколько запросов пустить в half-open
    
    _state: CircuitState = CircuitState.CLOSED
    _failure_count: int = 0
    _last_failure_time: float = 0.0
    _half_open_requests: int = 0
    
    async def call(self, func, *args, **kwargs):
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                logger.info("Circuit %s: OPEN -> HALF_OPEN", self.name)
                self._state = CircuitState.HALF_OPEN
                self._half_open_requests = 0
            else:
                raise CircuitBreakerError(f"Circuit {self.name} is OPEN")
        
        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_requests >= self.half_open_max_requests:
                raise CircuitBreakerError(
                    f"Circuit {self.name} is HALF_OPEN (max probe requests reached)"
                )
            self._half_open_requests += 1
        
        try:
            result = await func(*args, **kwargs)
            
            if self._state == CircuitState.HALF_OPEN:
                logger.info("Circuit %s: HALF_OPEN -> CLOSED (success)", self.name)
                self._state = CircuitState.CLOSED
                self._failure_count = 0
            
            return result
            
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            
            if self._failure_count >= self.threshold:
                logger.warning(
                    "Circuit %s: %s -> OPEN (%d failures)", 
                    self.name, self._state.value, self._failure_count,
                )
                self._state = CircuitState.OPEN
            
            raise


# Использование
payment_circuit = CircuitBreaker("payment", threshold=3, recovery_timeout=30.0)

async def process_payment(order_id: str, amount: Money) -> PaymentResult:
    try:
        return await payment_circuit.call(
            payment_client.charge, order_id=order_id, amount=amount
        )
    except CircuitBreakerError:
        logger.error("Payment circuit is open, falling back to async processing")
        # Fallback: кладём в очередь, обработаем позже
        await payment_queue.enqueue(order_id, amount)
        return PaymentResult(status="queued")
```

---

**Это база.** Не «ещё один туториал по паттернам». Это то, что я реально копирую из проекта в проект, адаптируя под конкретные нужды.

Я не использую все паттерны сразу. Я использую те, которые **нужны прямо сейчас**, и добавляю новые, когда возникает боль.
