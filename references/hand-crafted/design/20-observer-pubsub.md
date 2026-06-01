# Observer and Pub-Sub: Event Communication

The Observer pattern is fundamental to event-driven architecture.
It lets one object notify many others about state changes without coupling them.

## The Problem: Tight Coupling

```python
class OrderService:
    def __init__(self):
        self.email = EmailService()
        self.inventory = InventoryService()
        self.analytics = AnalyticsService()
        self.payment = PaymentService()

    async def confirm_order(self, order: Order) -> None:
        # Every confirmation touches EVERY service
        await self.email.send_confirmation(order.user_id)
        await self.inventory.reduce_stock(order.items)
        await self.analytics.track_order(order)
        await self.payment.process(order)

        # Adding a new service requires changing this method!
        # What if loyalty service needs to be notified?
```

## Simple Observer (In-Process)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class Observer(ABC):
    @abstractmethod
    async def update(self, event: str, data: dict) -> None: ...


class Observable:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    async def notify(self, event: str, data: dict) -> None:
        for observer in self._observers:
            try:
                await observer.update(event, data)
            except Exception as e:
                logger.error("Observer failed: %s", e)


# Concrete Observers
class EmailNotifier(Observer):
    async def update(self, event: str, data: dict) -> None:
        if event == "order.confirmed":
            await email_service.send_confirmation(data["user_id"])

class InventoryUpdater(Observer):
    async def update(self, event: str, data: dict) -> None:
        if event == "order.confirmed":
            await inventory_service.reduce_stock(data["items"])

class AnalyticsTracker(Observer):
    async def update(self, event: str, data: dict) -> None:
        if event == "order.confirmed":
            await analytics_service.track_order(data["order"])


# Usage
@dataclass
class OrderService(Observable):
    async def confirm_order(self, order: Order) -> None:
        # Process the order
        await self._process_payment(order)

        # Notify all observers
        await self.notify("order.confirmed", {
            "order": order,
            "user_id": order.user_id,
            "items": order.items,
        })


# Wiring
order_service = OrderService()
order_service.attach(EmailNotifier())
order_service.attach(InventoryUpdater())
order_service.attach(AnalyticsTracker())
```

## Event Bus (More Flexible)

```python
import asyncio
from collections import defaultdict


class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: callable) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: callable) -> None:
        self._handlers[event].remove(handler)

    async def publish(self, event: str, data: dict) -> None:
        tasks = []
        for handler in self._handlers[event]:
            tasks.append(asyncio.create_task(self._safe_call(handler, data)))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_call(self, handler: callable, data: dict):
        try:
            await handler(data)
        except Exception as e:
            logger.error("Handler for event failed: %s", e)


# Usage
bus = EventBus()

async def on_order_confirmed(data: dict):
    await email_service.send_confirmation(data["user_id"])

async def on_order_cancelled(data: dict):
    await inventory_service.restore_stock(data["items"])

bus.subscribe("order.confirmed", on_order_confirmed)
bus.subscribe("order.cancelled", on_order_cancelled)

await bus.publish("order.confirmed", {"order_id": "123", "user_id": "456"})
```

## Distributed Pub-Sub (via Message Queue)

```python
# Producer
class OrderEventPublisher:
    def __init__(self, queue):
        self.queue = queue

    async def order_confirmed(self, order: Order) -> None:
        await self.queue.publish(
            "order.confirmed",
            {"order_id": order.id, "user_id": order.user_id},
        )

# Consumer
class InventoryConsumer:
    def __init__(self, inventory_service):
        self.service = inventory_service

    async def handle_order_confirmed(self, event: dict) -> None:
        order_id = event["order_id"]
        await self.service.reduce_stock(order_id)
```

## Pattern Comparison

| Aspect | Observer | Event Bus | Pub-Sub |
|--------|----------|-----------|---------|
| Scope | In-process | In-process | Distributed |
| Coupling | Direct | Indirect | Indirect |
| Reliability | Memory | Memory | At-least-once |
| Throughput | High | High | Medium |
| Complexity | Low | Medium | High |

## When to Use

- **Observer**: Simple in-process notification, one app
- **Event Bus**: Multiple handlers for same event, decoupled components
- **Pub-Sub**: Multiple services, need reliability, different stacks

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?
