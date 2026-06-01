# Microservices Patterns: Complete Reference

**Все паттерны микросервисной архитектуры для Principal Engineer. От decomposition до observability.**

---

## 1. Service Decomposition Patterns

### Decompose by Business Capability

```python
"""Domain-driven decomposition patterns."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DECOMPOSITION_PATTERNS = {
    "business_capability": {
        "description": "Разделение по бизнес-возможностям",
        "example": "Order Service, Payment Service, Inventory Service",
        "pros": "Соответствует бизнес-структуре, естественные границы",
        "cons": "Может быть слишком крупным или мелким",
        "when_to_use": "Когда бизнес-процессы чётко разделены",
    },
    "subdomain": {
        "description": "Разделение по DDD поддоменам",
        "example": "Core domain (orders), Supporting (notifications), Generic (auth)",
        "pros": "Чёткие границы bounded context",
        "cons": "Требует глубокого понимания домена",
        "when_to_use": "Сложные домены с разными темпами изменений",
    },
    "entity": {
        "description": "Разделение по сущностям",
        "example": "User Service, Product Service, Order Service",
        "pros": "Просто, понятно, соответствует CRUD",
        "cons": "Низкая связность, много cross-service коммуникации",
        "when_to_use": "Простые CRUD системы",
    },
    "transactional_boundary": {
        "description": "Разделение по транзакционным границам",
        "example": "Сервисы, которые не требуют distributed transactions вместе",
        "pros": "Минимизация distributed transactions",
        "cons": "Может быть неочевидно",
        "when_to_use": "Системы с строгими требованиями к консистентности",
    },
}
```

### Strangler Fig Pattern

```python
"""Strangler Fig migration pattern implementation."""
from __future__ import annotations

import hashlib
import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass
class StranglerFigRouter:
    """Route traffic between old and new service during migration.
    
    Battle Scar: Миграция монолита на микросервисы.
    Strangler Fig позволил мигрировать endpoint за endpoint'ом
    без downtime и rollback рисков.
    """
    
    old_service: Any
    new_service: Any
    migration_percentage: float = 0.0  # 0.0 to 1.0
    
    def should_route_to_new(self, request: dict) -> bool:
        """Consistent routing based on request properties."""
        user_id = request.get("user_id", "")
        hash_val = int(hashlib.md5(user_id.encode()).hexdigest()[:4], 16) % 100
        return hash_val < (self.migration_percentage * 100)
    
    async def route(self, request: dict) -> Any:
        """Route request to appropriate service."""
        if self.should_route_to_new(request):
            try:
                result = await self.new_service.handle(request)
                # Monitor for errors
                return result
            except Exception as e:
                # Fallback to old service
                logger.warning(f"New service failed, falling back: {e}")
                return await self.old_service.handle(request)
        else:
            return await self.old_service.handle(request)
    
    def increase_migration(self, percentage: float) -> None:
        """Safely increase migration percentage."""
        if percentage > self.migration_percentage:
            self.migration_percentage = min(percentage, 1.0)
            logger.info(f"Migration increased to {percentage:.0%}")
}
```

## 2. Inter-Service Communication

### Synchronous (gRPC)

```python
"""gRPC service definition and patterns."""
from __future__ import annotations


GRPC_SERVICE_DEF = """
  syntax = "proto3";
  
  package orders;
  
  service OrderService {
    rpc GetOrder (GetOrderRequest) returns (Order);
    rpc CreateOrder (CreateOrderRequest) returns (Order);
    rpc ListOrders (ListOrdersRequest) returns (ListOrdersResponse);
    rpc StreamOrders (StreamOrdersRequest) returns (stream Order);
  }
  
  message Order {
    string id = 1;
    string user_id = 2;
    double total = 3;
    string status = 4;
    repeated OrderItem items = 5;
    google.protobuf.Timestamp created_at = 6;
  }
  
  message GetOrderRequest {
    string id = 1;
  }
"""


@gRPC_SERVICE_PATTERNS = """
  gRPC patterns for production:
  
  1. Deadlines (timeout) on every call
     grpc.Deadline(timeout=5.0)
  
  2. Retry with exponential backoff
     grpc.RetryPolicy(maxAttempts=3, initialBackoff=1.0)
  
  3. Health checking
     grpc.health.v1.Health/Check
  
  4. Load balancing
     round_robin, pick_first, weighted_target
  
  5. Interceptors for observability
     - Logging interceptor
     - Metrics interceptor
     - Auth interceptor
  
  6. Error handling
     - Use gRPC status codes
     - Include error details
     - Client handles UNAVAILABLE with retry
"""
```

### Asynchronous (Events)

```python
"""Event-driven inter-service communication."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


EVENT_PATTERNS = {
    "event_notification": {
        "description": "Сервис публикует событие, другие подписываются",
        "example": "OrderCreated → Notification Service sends email",
        "pros": "Слабая связанность, масштабирование",
        "cons": "Eventual consistency",
    },
    "event_carried_state_transfer": {
        "description": "Событие содержит все необходимые данные",
        "example": "UserUpdated включает name, email, address",
        "pros": "Подписчики не делают доп запросов",
        "cons": "Дублирование данных, размер событий",
    },
    "saga": {
        "description": "Цепочка событий с компенсацией",
        "example": "OrderCreated → PaymentProcessed → InventoryReserved",
        "pros": "Консистентность без distributed transactions",
        "cons": "Сложность, нет изоляции",
    },
    "outbox": {
        "description": "Гарантированная отправка через БД",
        "example": "Событие пишется в ту же транзакцию что и бизнес-данные",
        "pros": "Exactly-once delivery",
        "cons": "Дополнительная таблица, нагрузка на БД",
    },
}
```

## 3. Data Management

### Database per Service

```python
"""Database per service pattern with shared data access."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DatabasePerService:
    """Each service owns its database.
    
    No other service can access another service's database directly.
    All access through the service's API.
    """
    
    PRINCIPLES = """
    1. Each service has its own database
    2. Only that service can access its database
    3. Other services access data through API
    4. Private data is truly private
    
    Exceptions:
    - Reporting/analytics → read replicas
    - Saga/event sourcing → events are shared
    - CQRS → query side can be shared
    """
    
    IMPLEMENTATIONS = {
        "orders_service": {
            "database": "PostgreSQL (orders_db)",
            "tables": ["orders", "order_items"],
            "api": "GET /orders, POST /orders, PATCH /orders/:id",
        },
        "payments_service": {
            "database": "PostgreSQL (payments_db)",
            "tables": ["payments", "refunds", "transactions"],
            "api": "POST /charges, POST /refunds",
        },
        "users_service": {
            "database": "PostgreSQL (users_db)",
            "tables": ["users", "addresses", "payment_methods"],
            "api": "GET /users/:id, PATCH /users/:id",
        },
    }
```

### Saga Pattern Implementation

```python
"""Saga pattern for distributed transactions."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class SagaStep:
    name: str
    execute: Callable[[], Any]
    compensate: Callable[[], Any] | None = None
    timeout: float = 30.0


@dataclass
class SagaOrchestrator:
    """Orchestrate saga execution with compensation.
    
    Battle Scar: Без saga, при ошибке в шаге 3 из 5,
    данные оставались в несогласованном состоянии.
    Saga гарантирует eventual consistency.
    """
    
    name: str
    steps: list[SagaStep] = field(default_factory=list)
    _completed: list[SagaStep] = field(default_factory=list)
    
    def add_step(self, step: SagaStep) -> None:
        self.steps.append(step)
    
    async def execute(self) -> None:
        """Execute saga steps in order, compensating on failure."""
        logger.info(f"Saga '{self.name}' started ({len(self.steps)} steps)")
        
        for step in self.steps:
            try:
                async with asyncio.timeout(step.timeout):
                    for attempt in range(3):  # Retry up to 3 times
                        try:
                            result = await step.execute()
                            self._completed.append(step)
                            logger.info(f"Step '{step.name}' completed")
                            break
                        except Exception as e:
                            if attempt == 2:
                                raise
                            await asyncio.sleep(2 ** attempt)
                except asyncio.TimeoutError:
                    raise Exception(f"Step '{step.name}' timed out")
            except Exception as e:
                logger.error(f"Saga failed at step '{step.name}': {e}")
                await self._compensate()
                raise SagaException(f"Saga '{self.name}' failed: {e}")
        
        logger.info(f"Saga '{self.name}' completed successfully")
    
    async def _compensate(self) -> None:
        """Compensate all completed steps in reverse order."""
        logger.info(f"Saga '{self.name}': compensating {len(self._completed)} steps")
        
        for step in reversed(self._completed):
            if step.compensate:
                try:
                    await step.compensate()
                    logger.info(f"Compensated step '{step.name}'")
                except Exception as e:
                    logger.error(f"Compensation for step '{step.name}' failed: {e}")


class SagaException(Exception):
    pass
```

## 4. Observability Patterns

### Distributed Tracing

```python
"""Distributed tracing across microservices."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from contextvars import ContextVar
import uuid
import time


_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_span_id: ContextVar[str] = ContextVar("span_id", default="")


@dataclass
class TraceContext:
    """Propagate trace context across service boundaries."""
    trace_id: str
    parent_span_id: str
    service_name: str
    
    @classmethod
    def from_headers(cls, headers: dict) -> "TraceContext":
        return cls(
            trace_id=headers.get("X-Trace-Id", str(uuid.uuid4())),
            parent_span_id=headers.get("X-Span-Id", ""),
            service_name=headers.get("X-Service-Name", "unknown"),
        )
    
    def to_headers(self) -> dict:
        return {
            "X-Trace-Id": self.trace_id,
            "X-Span-Id": _span_id.get(),
            "X-Service-Name": "my-service",
        }


class DistributedTracer:
    """Trace requests across microservice boundaries."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.spans: list[dict] = []
    
    @asynccontextmanager
    async def span(self, name: str, tags: dict | None = None):
        """Create child span."""
        span_id = str(uuid.uuid4())[:8]
        parent_id = _span_id.get()
        trace_id = _trace_id.get() or str(uuid.uuid4())
        
        token_trace = _trace_id.set(trace_id)
        token_span = _span_id.set(span_id)
        
        span = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_id,
            "service": self.service_name,
            "name": name,
            "start_time": time.monotonic(),
            "tags": tags or {},
        }
        
        try:
            yield
        except Exception as e:
            span["tags"]["error"] = True
            span["tags"]["error_message"] = str(e)
            raise
        finally:
            span["duration_ms"] = (time.monotonic() - span["start_time"]) * 1000
            self.spans.append(span)
            _trace_id.reset(token_trace)
            _span_id.reset(token_span)
    
    def export(self) -> list[dict]:
        """Export spans for reporting."""
        return self.spans
```

## 5. Resilience Patterns

### Bulkhead Pattern

```python
"""Bulkhead isolation for critical resources."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BulkheadIsolation:
    """Isolate resources to prevent cascading failures.
    
    Each external dependency gets its own thread pool / connection pool.
    If one dependency fails, others remain unaffected.
    """
    
    pools: dict[str, asyncio.Semaphore] = field(default_factory=dict)
    
    def register(self, name: str, max_concurrent: int) -> None:
        self.pools[name] = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, pool_name: str, coro: Any, fallback: Any = None) -> Any:
        """Execute with bulkhead isolation."""
        sem = self.pools.get(pool_name)
        if not sem:
            return await coro
        
        try:
            async with sem:
                return await coro
        except Exception as e:
            if fallback:
                return fallback
            raise


# Usage:
# bulkhead = BulkheadIsolation()
# bulkhead.register("database", max_concurrent=20)
# bulkhead.register("redis", max_concurrent=50)
# bulkhead.register("external_api", max_concurrent=5)
#
# result = await bulkhead.execute("database", fetch_user(id))
```

### Timeout & Deadline Propagation

```python
"""Deadline propagation across service calls."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass
class Deadline:
    """Propagate deadlines across service boundaries."""
    deadline: float  # Unix timestamp
    
    @classmethod
    def from_timeout(cls, timeout: float) -> "Deadline":
        return cls(deadline=time.monotonic() + timeout)
    
    @property
    def remaining(self) -> float:
        return max(0.0, self.deadline - time.monotonic())
    
    @property
    def expired(self) -> bool:
        return self.remaining <= 0
    
    def to_header(self) -> str:
        return str(self.deadline)
    
    @classmethod
    def from_header(cls, header: str) -> "Deadline":
        return cls(deadline=float(header))
    
    async def wait_for(self, coro: Any, max_timeout: float = 30.0) -> Any:
        """Execute coroutine with deadline."""
        effective_timeout = min(self.remaining, max_timeout)
        if effective_timeout <= 0:
            raise asyncio.TimeoutError("Deadline exceeded")
        try:
            return await asyncio.wait_for(coro, timeout=effective_timeout)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Deadline exceeded ({effective_timeout}s)")
```

## 6. API Gateway Patterns

```python
"""API Gateway patterns for microservices."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class APIGatewayPatterns:
    """API Gateway responsibilities and patterns."""
    
    PATTERNS = {
        "gateway_routing": {
            "description": "Route requests to appropriate services",
            "example": "/users/* → User Service, /orders/* → Order Service",
        },
        "aggregation": {
            "description": "Aggregate responses from multiple services",
            "example": "Product detail page calls Product + Inventory + Review",
        },
        "authentication": {
            "description": "Centralize auth check at gateway level",
            "example": "JWT validation before routing to services",
        },
        "rate_limiting": {
            "description": "Apply rate limits at entry point",
            "example": "100 req/s per user, 1000 req/s total",
        },
        "circuit_breaker": {
            "description": "Protect downstream services",
            "example": "If Order Service is slow, fail fast at gateway",
        },
        "transformation": {
            "description": "Transform requests/responses",
            "example": "Convert XML to JSON, v1 to v2 API format",
        },
    }
    
    # Backend for Frontend (BFF) — отдельный gateway для каждого клиента
    BFF = """
    BFF Pattern:
      Web App → Web BFF → Microservices
      Mobile App → Mobile BFF → Microservices
      Third Party → Public API Gateway → Microservices
    
    Pros:
    - Оптимизирован под конкретный клиент
    - Клиент не знает о микросервисах
    - Можно менять бэкенд без изменения клиента
    
    Cons:
    - Дополнительный сервис для поддержки
    - Дублирование логики между BFF
    """
```

## 7. Deployment & Testing Patterns

### Testing Microservices

```python
"""Testing strategies for microservices."""
from __future__ import annotations


TESTING_PYRAMID_MICROSERVICES = """
  Level 1: Unit Tests (70%)
    - Test individual functions and classes
    - Mock external dependencies
    - Fast execution (< 1ms each)
  
  Level 2: Contract Tests (20%)
    - Verify API contracts between services
    - Pact / Spring Cloud Contract
    - Ensure compatibility without deploying
  
  Level 3: Integration Tests (7%)
    - Test service with real dependencies
    - Testcontainers for databases
    - Docker Compose for full stack
  
  Level 4: E2E Tests (3%)
    - Test critical user journeys
    - Deployed environment
    - Small number, high value
  
  Level 5: Performance Tests (automated)
    - Load, stress, soak tests
    - Identify bottlenecks
    - In CI on critical path
"""
```
