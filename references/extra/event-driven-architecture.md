# Event-Driven Architecture: Complete Guide

**Event-driven systems в Big Tech. Kafka, RabbitMQ, event sourcing, CQRS на практике.**

---

## 1. Event Types

```python
"""Event classification for event-driven systems."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


# Domain Events — что произошло в системе
@dataclass
class OrderCreated:
    order_id: str
    user_id: str
    items: list[dict]
    total: float
    timestamp: datetime

@dataclass
class PaymentProcessed:
    order_id: str
    payment_id: str
    amount: float
    status: str

# Integration Events — коммуникация между сервисами
@dataclass
class UserRegistered:
    user_id: str
    email: str
    name: str
    registered_at: datetime

@dataclass
class InventoryUpdated:
    product_id: str
    quantity_change: int
    new_quantity: int

# System Events — инфраструктурные
@dataclass
class ServiceHealthChanged:
    service_name: str
    old_status: str
    new_status: str
    timestamp: datetime
```

## 2. Event Bus Implementation

```python
"""Event bus with guaranteed delivery."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class InMemoryEventBus:
    """In-memory event bus with retry and DLQ.
    
    For production: Use Kafka/RabbitMQ instead.
    This is for testing and simple in-process events.
    """
    
    handlers: dict[str, list[Callable]] = field(default_factory=lambda: defaultdict(list))
    retry_count: int = 3
    dlq_handler: Callable | None = None
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        self.handlers[event_type].append(handler)
    
    async def publish(self, event_type: str, event: Any) -> None:
        """Publish event with retry and DLQ."""
        for handler in self.handlers.get(event_type, []):
            for attempt in range(self.retry_count):
                try:
                    await handler(event)
                    break
                except Exception as e:
                    if attempt == self.retry_count - 1:
                        if self.dlq_handler:
                            await self.dlq_handler(event_type, event, e)
                        logger.error(f"Handler failed after {self.retry_count} retries: {e}")
                    else:
                        await asyncio.sleep(2 ** attempt)
```

## 3. Outbox Pattern

```python
"""Outbox pattern for reliable event publishing.

Battle Scar: Публикация события до commit транзакции → 
событие опубликовано, но транзакция откатилась. Консистентность нарушена.
Outbox: событие пишется в той же транзакции → гарантия доставки.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
import json


@dataclass
class OutboxMessage:
    """Message in outbox table."""
    id: int
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict
    created_at: datetime
    published_at: datetime | None = None


class OutboxPublisher:
    """Reliable event publisher using outbox table.
    
    1. Write event to outbox table (same transaction as business data)
    2. Background worker reads unpublished events
    3. Publishes to message broker
    4. Marks as published
    """
    
    async def publish_pending(self, batch_size: int = 100) -> int:
        """Publish all pending outbox messages."""
        messages = await self._get_unpublished(batch_size)
        published = 0
        
        for msg in messages:
            try:
                await self._send_to_broker(msg)
                await self._mark_published(msg.id)
                published += 1
            except Exception as e:
                logger.error(f"Failed to publish outbox msg {msg.id}: {e}")
        
        return published
    
    async def _send_to_broker(self, msg: OutboxMessage) -> None:
        """Send to Kafka/RabbitMQ."""
        await self.producer.send(
            msg.event_type,
            key=msg.aggregate_id.encode(),
            value=json.dumps(msg.payload).encode(),
        )
```

## 4. Event Sourcing

```python
"""Event sourcing implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventSourcedAggregate:
    """Base class for event-sourced aggregates."""
    id: str
    version: int = 0
    _changes: list = field(default_factory=list)
    
    def apply(self, event: Any) -> None:
        """Apply event to aggregate state."""
        handler_name = f"apply_{type(event).__name__}"
        handler = getattr(self, handler_name, None)
        if handler:
            handler(event)
        self.version += 1
    
    def add_event(self, event: Any) -> None:
        """Register event (not yet persisted)."""
        self.apply(event)
        self._changes.append(event)


class OrderAggregate(EventSourcedAggregate):
    """Order aggregate with event sourcing."""
    
    def __init__(self, id: str):
        super().__init__(id)
        self.status = "pending"
        self.items = []
        self.total = 0
    
    def apply_OrderCreated(self, event: "OrderCreated") -> None:
        self.status = "created"
        self.items = event.items
        self.total = event.total
    
    def apply_OrderConfirmed(self, event: "OrderConfirmed") -> None:
        self.status = "confirmed"
    
    def apply_OrderShipped(self, event: "OrderShipped") -> None:
        self.status = "shipped"
    
    def create_order(self, items: list, total: float) -> None:
        self.add_event(OrderCreated(
            order_id=self.id,
            user_id="user_123",
            items=items,
            total=total,
            timestamp=datetime.utcnow(),
        ))


class EventStore:
    """Event store for persistence."""
    
    async def save_events(self, aggregate_id: str, events: list, expected_version: int) -> None:
        """Save events atomically with optimistic concurrency."""
        async with db.transaction():
            # Check version (optimistic lock)
            current = await self._get_version(aggregate_id)
            if current != expected_version:
                raise ConcurrencyError(f"Version mismatch: {current} != {expected_version}")
            
            for event in events:
                await self._insert_event(aggregate_id, event)
    
    async def get_events(self, aggregate_id: str) -> list:
        """Get all events for aggregate (for rebuild)."""
        return await self._select_events(aggregate_id)
    
    async def rebuild_aggregate(self, aggregate_id: str, cls: type) -> EventSourcedAggregate:
        """Rebuild aggregate from events."""
        events = await self.get_events(aggregate_id)
        aggregate = cls(aggregate_id)
        for event in sorted(events, key=lambda e: e.timestamp):
            aggregate.apply(event)
        return aggregate
```

## 5. CQRS (Command Query Responsibility Segregation)

```python
"""CQRS implementation with separate read/write models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# ── COMMAND SIDE (Write) ────────────────────────

@dataclass
class CreateOrderCommand:
    user_id: str
    items: list[dict]
    payment_method: str


class OrderCommandHandler:
    """Handle commands that mutate state."""
    
    async def handle(self, command: CreateOrderCommand) -> str:
        order_id = str(uuid.uuid4())
        
        # 1. Create order (domain logic)
        order = OrderAggregate(order_id)
        order.create_order(command.items, calculate_total(command.items))
        
        # 2. Save events
        await event_store.save_events(
            order_id, 
            order._changes, 
            expected_version=0,
        )
        
        # 3. Publish event (for read model update)
        await event_bus.publish("order.created", {
            "order_id": order_id,
            "user_id": command.user_id,
            "items": command.items,
            "total": order.total,
        })
        
        return order_id


# ── QUERY SIDE (Read) ──────────────────────────

@dataclass
class OrderSummary:
    """Read model — denormalized for fast queries."""
    id: str
    user_id: str
    user_name: str
    items_count: int
    total: float
    status: str
    created_at: datetime


class OrderQueryService:
    """Handle queries (reads from read-optimized store)."""
    
    async def get_order_summary(self, order_id: str) -> OrderSummary | None:
        """Read from denormalized table."""
        return await self.read_db.fetch_one(
            "SELECT * FROM order_summaries WHERE id = ?",
            [order_id],
        )
    
    async def get_user_orders(self, user_id: str, limit: int = 20) -> list[OrderSummary]:
        return await self.read_db.fetch_all(
            "SELECT * FROM order_summaries WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            [user_id, limit],
        )
```

## 6. Event Versioning

```python
"""Event schema evolution strategies."""
from __future__ import annotations


EVENT_VERSIONING = """
  Backward Compatible (recommended):
    - Add optional fields only
    - Set sensible defaults for new fields
    - Consumer reads what it needs
  
  Forward Compatible:
    - Ignore unknown fields
    - Can add new event types
    - Consumer tolerates missing fields
  
  Schema Registry (Avro/Protobuf):
    - Enforce compatibility rules
    - Auto-evolution with validation
    - Global schema IDs
  
  Breaking Changes:
    - Create new event version: OrderCreatedV2
    - Both versions published simultaneously
    - Consumers migrate independently
    - Deprecate old version after migration
"""
```


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
