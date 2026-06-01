# Design Patterns Deep Dive

**GoF и современные паттерны в Python. Когда использовать, какие компромиссы.**

---

## 1. Factory Method

```python
from abc import ABC, abstractmethod

class Exporter(ABC):
    @abstractmethod
    def export(self, data: list[dict]) -> str: ...

class CSVExporter(Exporter):
    def export(self, data: list[dict]) -> str:
        if not data:
            return ""
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        for row in data:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)

class JSONExporter(Exporter):
    def export(self, data: list[dict]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)

class XMLExporter(Exporter):
    def export(self, data: list[dict]) -> str:
        rows = []
        for row in data:
            elements = "\n".join(f"    <{k}>{v}</{k}>" for k, v in row.items())
            rows.append(f"  <row>\n{elements}\n  </row>")
        return "<data>\n" + "\n".join(rows) + "\n</data>"

def get_exporter(format: str) -> Exporter:
    exporters = {"csv": CSVExporter(), "json": JSONExporter(), "xml": XMLExporter()}
    if format not in exporters:
        raise ValueError(f"Unsupported format: {format}")
    return exporters[format]

# Использование
exporter = get_exporter("json")
result = exporter.export([{"id": 1, "name": "Alice"}])
```

## 2. Strategy Pattern

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return 0.0

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self._percent = percent
    
    def calculate(self, total: float) -> float:
        return total * self._percent / 100

class TieredDiscount(DiscountStrategy):
    def __init__(self, tiers: list[tuple[float, float]]):
        self._tiers = sorted(tiers, key=lambda x: x[0], reverse=True)
    
    def calculate(self, total: float) -> float:
        for threshold, percent in self._tiers:
            if total >= threshold:
                return total * percent / 100
        return 0.0

class Order:
    def __init__(self, total: float, strategy: DiscountStrategy):
        self._total = total
        self._strategy = strategy
    
    def final_price(self) -> float:
        return self._total - self._strategy.calculate(self._total)

# Использование
order = Order(1000, TieredDiscount([(500, 5), (1000, 10)]))
print(order.final_price())  # 900
```

## 3. Observer Pattern

```python
from abc import ABC, abstractmethod

class EventListener(ABC):
    @abstractmethod
    def update(self, event: str, data: dict) -> None: ...

class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[EventListener]] = {}
    
    def on(self, event: str, listener: EventListener) -> None:
        self._listeners.setdefault(event, []).append(listener)
    
    def off(self, event: str, listener: EventListener) -> None:
        if listeners := self._listeners.get(event):
            listeners.remove(listener)
    
    def emit(self, event: str, data: dict) -> None:
        for listener in self._listeners.get(event, []):
            listener.update(event, data)

class EmailNotifier(EventListener):
    def update(self, event: str, data: dict) -> None:
        print(f"Email: {event} - {data}")

class Logger(EventListener):
    def update(self, event: str, data: dict) -> None:
        print(f"Log: {event} - {data}")

# Использование
emitter = EventEmitter()
emitter.on("user.created", EmailNotifier())
emitter.on("user.created", Logger())
emitter.emit("user.created", {"id": 1, "email": "test@test.com"})
```

## 4. Builder Pattern

```python
class QueryBuilder:
    def __init__(self):
        self._table = ""
        self._fields = ["*"]
        self._where: list[str] = []
        self._order: list[str] = []
        self._limit = 0
        self._offset = 0
    
    def select(self, *fields: str) -> "QueryBuilder":
        self._fields = list(fields) if fields else ["*"]
        return self
    
    def from_table(self, table: str) -> "QueryBuilder":
        self._table = table
        return self
    
    def where(self, condition: str) -> "QueryBuilder":
        self._where.append(condition)
        return self
    
    def order_by(self, field: str, asc: bool = True) -> "QueryBuilder":
        direction = "ASC" if asc else "DESC"
        self._order.append(f"{field} {direction}")
        return self
    
    def limit(self, limit: int) -> "QueryBuilder":
        self._limit = limit
        return self
    
    def offset(self, offset: int) -> "QueryBuilder":
        self._offset = offset
        return self
    
    def build(self) -> str:
        parts = [f"SELECT {', '.join(self._fields)} FROM {self._table}"]
        if self._where:
            parts.append("WHERE " + " AND ".join(self._where))
        if self._order:
            parts.append("ORDER BY " + ", ".join(self._order))
        if self._limit:
            parts.append(f"LIMIT {self._limit}")
        if self._offset:
            parts.append(f"OFFSET {self._offset}")
        return " ".join(parts)

# Использование
query = (QueryBuilder()
         .select("id", "name", "email")
         .from_table("users")
         .where("age > 18")
         .where("active = true")
         .order_by("name")
         .limit(10)
         .offset(0)
         .build())
```

## 5. Singleton Pattern

```python
class SingletonMeta(type):
    _instances: dict[type, object] = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        self.parsed = False
    
    def parse(self):
        if not self.parsed:
            # ... парсинг
            self.parsed = True

# Все инстансы Config = один объект
c1 = Config()
c2 = Config()
assert c1 is c2
```

## 6. Adapter Pattern

```python
class LegacyPaymentSystem:
    def make_payment(self, amount: float, currency: str, user_id: int) -> dict:
        return {"status": "success", "transaction_id": "legacy_123"}

class ModernPaymentGateway:
    def charge(self, amount_cents: int, currency_code: str, 
               customer_id: str) -> dict:
        return {"status": "completed", "id": "modern_456"}

# Адаптер
class PaymentAdapter:
    def __init__(self, modern: ModernPaymentGateway):
        self._modern = modern
    
    def make_payment(self, amount: float, currency: str, user_id: int) -> dict:
        result = self._modern.charge(
            amount_cents=int(amount * 100),
            currency_code=currency.upper(),
            customer_id=str(user_id),
        )
        return {
            "status": "success" if result["status"] == "completed" else "failed",
            "transaction_id": result["id"],
        }

# Использование
adapter = PaymentAdapter(ModernPaymentGateway())
result = adapter.make_payment(99.99, "usd", 42)
```

## 7. Decorator Pattern

```python
from functools import wraps

class DataSource:
    def read(self) -> str:
        return "raw data"

class CompressedDataSource(DataSource):
    def __init__(self, source: DataSource):
        self._source = source
    
    def read(self) -> str:
        data = self._source.read()
        return f"compressed({data})"

class EncryptedDataSource(DataSource):
    def __init__(self, source: DataSource):
        self._source = source
    
    def read(self) -> str:
        data = self._source.read()
        return f"encrypted({data})"

# Композиция
source = EncryptedDataSource(CompressedDataSource(DataSource()))
print(source.read())  # encrypted(compressed(raw data))
```

## 8. Chain of Responsibility

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self._next: Handler | None = None
    
    def set_next(self, handler: "Handler") -> "Handler":
        self._next = handler
        return handler
    
    @abstractmethod
    def handle(self, request: dict) -> dict | None: ...

class ValidationHandler(Handler):
    def handle(self, request: dict) -> dict | None:
        if "email" not in request:
            return {"error": "Email required"}
        if "@" not in request["email"]:
            return {"error": "Invalid email"}
        return self._next.handle(request) if self._next else request

class AuthHandler(Handler):
    def handle(self, request: dict) -> dict | None:
        if not request.get("token"):
            return {"error": "Auth required"}
        return self._next.handle(request) if self._next else request

class LoggingHandler(Handler):
    def handle(self, request: dict) -> dict | None:
        print(f"Request: {request}")
        return self._next.handle(request) if self._next else request

# Цепочка
handler = LoggingHandler()
handler.set_next(ValidationHandler()).set_next(AuthHandler())
result = handler.handle({"email": "test@test.com", "token": "abc"})
```

## 9. Composite Pattern

```python
from abc import ABC, abstractmethod

class FileSystemNode(ABC):
    @abstractmethod
    def get_size(self) -> int: ...
    
    @abstractmethod
    def display(self, indent: str = "") -> None: ...

class File(FileSystemNode):
    def __init__(self, name: str, size: int):
        self._name = name
        self._size = size
    
    def get_size(self) -> int:
        return self._size
    
    def display(self, indent: str = "") -> None:
        print(f"{indent}{self._name} ({self._size} bytes)")

class Directory(FileSystemNode):
    def __init__(self, name: str):
        self._name = name
        self._children: list[FileSystemNode] = []
    
    def add(self, child: FileSystemNode) -> None:
        self._children.append(child)
    
    def get_size(self) -> int:
        return sum(child.get_size() for child in self._children)
    
    def display(self, indent: str = "") -> None:
        print(f"{indent}{self._name}/")
        for child in self._children:
            child.display(indent + "  ")

# Использование
root = Directory("root")
root.add(File("readme.txt", 100))
subdir = Directory("src")
subdir.add(File("main.py", 500))
subdir.add(File("utils.py", 300))
root.add(subdir)
root.display()
```

## 10. Template Method

```python
from abc import ABC, abstractmethod

class DataImporter(ABC):
    def import_data(self, path: str) -> list[dict]:
        """Template method: определяет шаги импорта."""
        raw = self._read_file(path)
        parsed = self._parse(raw)
        validated = self._validate(parsed)
        return self._transform(validated)
    
    @abstractmethod
    def _read_file(self, path: str) -> str: ...
    
    @abstractmethod
    def _parse(self, data: str) -> list[dict]: ...
    
    def _validate(self, data: list[dict]) -> list[dict]:
        return [row for row in data if row.get("name") and row.get("email")]
    
    def _transform(self, data: list[dict]) -> list[dict]:
        return [{k: str(v).strip() for k, v in row.items()} for row in data]

class CSVImporter(DataImporter):
    def _read_file(self, path: str) -> str:
        import csv
        with open(path) as f:
            return f.read()
    
    def _parse(self, data: str) -> list[dict]:
        import csv, io
        reader = csv.DictReader(io.StringIO(data))
        return list(reader)

class JSONImporter(DataImporter):
    def _read_file(self, path: str) -> str:
        with open(path) as f:
            return f.read()
    
    def _parse(self, data: str) -> list[dict]:
        import json
        return json.loads(data)
```

## 11. State Pattern

```python
from abc import ABC, abstractmethod

class OrderState(ABC):
    @abstractmethod
    def confirm(self, order: "Order") -> None: ...
    @abstractmethod
    def ship(self, order: "Order") -> None: ...
    @abstractmethod
    def deliver(self, order: "Order") -> None: ...
    @abstractmethod
    def cancel(self, order: "Order") -> None: ...

class PendingState(OrderState):
    def confirm(self, order: "Order") -> None:
        print("Order confirmed")
        order.state = ConfirmedState()
    
    def ship(self, order: "Order") -> None:
        raise ValueError("Cannot ship pending order")
    
    def deliver(self, order: "Order") -> None:
        raise ValueError("Cannot deliver pending order")
    
    def cancel(self, order: "Order") -> None:
        print("Order cancelled")
        order.state = CancelledState()

class ConfirmedState(OrderState):
    def confirm(self, order: "Order") -> None:
        raise ValueError("Already confirmed")
    
    def ship(self, order: "Order") -> None:
        print("Order shipped")
        order.state = ShippedState()
    
    def deliver(self, order: "Order") -> None:
        raise ValueError("Cannot deliver before shipping")
    
    def cancel(self, order: "Order") -> None:
        print("Order cancelled")
        order.state = CancelledState()

class ShippedState(OrderState):
    def confirm(self, order: "Order") -> None:
        raise ValueError("Already confirmed")
    
    def ship(self, order: "Order") -> None:
        raise ValueError("Already shipped")
    
    def deliver(self, order: "Order") -> None:
        print("Order delivered")
        order.state = DeliveredState()
    
    def cancel(self, order: "Order") -> None:
        print("Order cancelled (shipping return)")
        order.state = CancelledState()

class DeliveredState(OrderState):
    def confirm(self, order: "Order") -> None:
        raise ValueError("Already confirmed")
    
    def deliver(self, order: "Order") -> None:
        raise ValueError("Already delivered")
    
    def cancel(self, order: "Order") -> None:
        print("Return initiated")
        order.state = CancelledState()

class CancelledState(OrderState):
    def confirm(self, order: "Order") -> None:
        raise ValueError("Cannot confirm cancelled order")
    
    def ship(self, order: "Order") -> None:
        raise ValueError("Cannot ship cancelled order")
    
    def deliver(self, order: "Order") -> None:
        raise ValueError("Cannot deliver cancelled order")
    
    def cancel(self, order: "Order") -> None:
        raise ValueError("Already cancelled")

class Order:
    def __init__(self):
        self.state: OrderState = PendingState()
    
    def confirm(self) -> None:
        self.state.confirm(self)
    
    def ship(self) -> None:
        self.state.ship(self)
    
    def deliver(self) -> None:
        self.state.deliver(self)
    
    def cancel(self) -> None:
        self.state.cancel(self)

# Использование
order = Order()
order.confirm()  # Order confirmed
order.ship()     # Order shipped
order.deliver()  # Order delivered
```

## 12. Proxy Pattern

```python
import time
from functools import wraps

class APIClient:
    def fetch(self, url: str) -> dict:
        time.sleep(1)  # симуляция запроса
        return {"url": url, "data": "response"}

class CachedAPIClient:
    def __init__(self, client: APIClient):
        self._client = client
        self._cache: dict[str, dict] = {}
    
    def fetch(self, url: str) -> dict:
        if url in self._cache:
            print("Cache hit!")
            return self._cache[url]
        
        result = self._client.fetch(url)
        self._cache[url] = result
        return result

# Использование
client = CachedAPIClient(APIClient())
client.fetch("/users")  # реальный запрос
client.fetch("/users")  # из кэша
```

## 13. Iterator Pattern

```python
class PaginatedCollection:
    def __init__(self, data: list[Any], page_size: int = 10):
        self._data = data
        self._page_size = page_size
    
    def __iter__(self) -> "PaginatedIterator":
        return PaginatedIterator(self._data, self._page_size)

class PaginatedIterator:
    def __init__(self, data: list[Any], page_size: int):
        self._data = data
        self._page_size = page_size
        self._index = 0
    
    def __next__(self) -> list[Any]:
        if self._index >= len(self._data):
            raise StopIteration
        
        page = self._data[self._index:self._index + self._page_size]
        self._index += self._page_size
        return page

# Использование
collection = PaginatedCollection(list(range(100)), page_size=20)
for page in collection:
    print(f"Page with {len(page)} items")
```

## 14. Command Pattern

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...
    @abstractmethod
    def undo(self) -> None: ...

class CreateUserCommand(Command):
    def __init__(self, repo: UserRepository, data: dict):
        self._repo = repo
        self._data = data
        self._created_user = None
    
    def execute(self) -> None:
        self._created_user = self._repo.create(self._data)
    
    def undo(self) -> None:
        if self._created_user:
            self._repo.delete(self._created_user.id)

class CommandHistory:
    def __init__(self):
        self._history: list[Command] = []
    
    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)
    
    def undo(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()
```

## 15. Which Pattern When

```
┌────────────────────┬────────────────────────────────┬──────────────────────┐
│ Проблема           │ Паттерн                        │ Когда НЕ использовать│
├────────────────────┼────────────────────────────────┼──────────────────────┤
│ Создание объектов  │ Factory, Builder, Singleton    │ Если просто new() ok │
│ Поведение          │ Strategy, State, Command       │ Если if/else хватает │
│ Структура          │ Adapter, Composite, Proxy      │ Если не нужно сейчас │
│ Коммуникация       │ Observer, Chain, Mediator      │ Если связи простые   │
│ Алгоритм           │ Template, Iterator, Visitor    │ Если алгоритм простой│
└────────────────────┴────────────────────────────────┴──────────────────────┘
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

## Architectural Patterns in Production

### Repository Pattern (Full Implementation)

```python
"""Complete Repository pattern with caching and retry."""
from __future__ import annotations

from typing import Any, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

EntityT = TypeVar("EntityT")
ID = TypeVar("ID")


class Repository(ABC, Generic[EntityT, ID]):
    """Abstract repository with caching layer."""
    
    @abstractmethod
    async def get(self, id: ID) -> EntityT | None:
        ...
    
    @abstractmethod
    async def save(self, entity: EntityT) -> EntityT:
        ...
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        ...


@dataclass
class CachedRepository(Repository[EntityT, ID]):
    """Repository with Redis caching layer."""
    
    db_repo: Repository[EntityT, ID]
    cache: Any  # Redis client
    ttl: int = 300
    prefix: str = "repo:"
    
    async def get(self, id: ID) -> EntityT | None:
        cache_key = f"{self.prefix}{id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return self._deserialize(cached)
        
        # Cache miss — get from DB
        entity = await self.db_repo.get(id)
        if entity:
            await self.cache.setex(cache_key, self.ttl, self._serialize(entity))
        
        return entity
    
    async def save(self, entity: EntityT) -> EntityT:
        result = await self.db_repo.save(entity)
        # Invalidate cache
        await self.cache.delete(f"{self.prefix}{entity.id}")
        return result
    
    async def delete(self, id: ID) -> bool:
        result = await self.db_repo.delete(id)
        await self.cache.delete(f"{self.prefix}{id}")
        return result


### Strategy Pattern with Factory

from typing import Protocol


class PaymentProvider(Protocol):
    async def charge(self, amount: int, currency: str) -> dict: ...
    async def refund(self, payment_id: str) -> dict: ...


class StripeProvider:
    async def charge(self, amount: int, currency: str) -> dict:
        # Stripe API integration
        return {"id": "ch_xxx", "status": "succeeded"}
    
    async def refund(self, payment_id: str) -> dict:
        return {"id": "re_xxx", "status": "succeeded"}


class PayPalProvider:
    async def charge(self, amount: int, currency: str) -> dict:
        # PayPal API integration
        return {"id": "PAY-XXX", "status": "completed"}
    
    async def refund(self, payment_id: str) -> dict:
        return {"id": "REF-XXX", "status": "completed"}


class PaymentFactory:
    providers = {
        "stripe": StripeProvider,
        "paypal": PayPalProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str) -> PaymentProvider:
        provider_cls = cls.providers.get(provider_name)
        if not provider_cls:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_cls()
