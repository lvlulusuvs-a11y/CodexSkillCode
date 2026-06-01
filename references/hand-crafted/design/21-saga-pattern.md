# Saga Pattern: Distributed Transactions

When you need a transaction that spans multiple services, you cant use
ACID. Each service has its own database. Enter the Saga pattern.

## The Problem

```python
async def create_order(user_id: str, items: list, payment_token: str):
    # Step 1: Reserve inventory
    await inventory_service.reserve(items)

    # Step 2: Process payment
    await payment_service.charge(payment_token, total)

    # Step 3: Update user loyalty
    await loyalty_service.add_points(user_id, points)

    # If step 2 fails, step 1 has already reserved inventory (leak!)
    # If step 3 fails, we charged the card but gave no loyalty points
```

## Saga: Choreography (Event-Driven)

Each service emits events and listens to events. No central coordinator.

```python
# Order Service
async def create_order(data: dict) -> None:
    order = await save_order(data)
    await event_bus.publish("order.created", {
        "order_id": order.id,
        "items": data["items"],
    })


# Inventory Service (listens to order.created)
async def on_order_created(event: dict) -> None:
    try:
        await reserve_inventory(event["items"])
        await event_bus.publish("inventory.reserved", {
            "order_id": event["order_id"],
        })
    except Exception as e:
        await event_bus.publish("inventory.reservation_failed", {
            "order_id": event["order_id"],
            "reason": str(e),
        })


# Payment Service (listens to inventory.reserved)
async def on_inventory_reserved(event: dict) -> None:
    try:
        order = await get_order(event["order_id"])
        await charge_payment(order["payment_token"], order["total"])
        await event_bus.publish("payment.processed", {
            "order_id": event["order_id"],
        })
    except Exception as e:
        # Compensating action: release inventory
        await event_bus.publish("payment.failed", {
            "order_id": event["order_id"],
            "reason": str(e),
        })


# Inventory Service (listens to payment.failed - compensating action)
async def on_payment_failed(event: dict) -> None:
    await release_inventory(event["order_id"])
```

## Saga: Orchestration (Central Coordinator)

```python
from dataclasses import dataclass, field
from typing import Callable, Awaitable


@dataclass
class SagaStep:
    name: str
    forward: Callable[[], Awaitable[None]]
    compensate: Callable[[], Awaitable[None]] | None = None


class SagaOrchestrator:
    def __init__(self, saga_name: str):
        self.name = saga_name
        self._steps: list[SagaStep] = []

    def add_step(self, step: SagaStep) -> None:
        self._steps.append(step)

    async def execute(self) -> None:
        completed: list[SagaStep] = []

        for step in self._steps:
            try:
                logger.info("Saga %s: executing %s", self.name, step.name)
                await step.forward()
                completed.append(step)
            except Exception as e:
                logger.error("Saga %s failed at %s: %s", self.name, step.name, e)
                await self._compensate(completed)
                raise SagaFailedError(self.name, step.name, str(e))

    async def _compensate(self, completed: list[SagaStep]) -> None:
        for step in reversed(completed):
            if step.compensate:
                try:
                    logger.info("Compensating %s", step.name)
                    await step.compensate()
                except Exception as e:
                    logger.critical("Compensation for %s failed: %s", step.name, e)


# Usage
async def create_order_saga(order_data: dict):
    saga = SagaOrchestrator("create_order")

    saga.add_step(SagaStep(
        name="reserve_inventory",
        forward=lambda: inventory_service.reserve(order_data["items"]),
        compensate=lambda: inventory_service.release(order_data["items"]),
    ))

    saga.add_step(SagaStep(
        name="charge_payment",
        forward=lambda: payment_service.charge(
            order_data["payment_token"], order_data["total"]
        ),
        compensate=lambda: payment_service.refund(order_data["total"]),
    ))

    saga.add_step(SagaStep(
        name="update_loyalty",
        forward=lambda: loyalty_service.add_points(
            order_data["user_id"], order_data["total"]
        ),
        # No compensation for loyalty (its already earned)
    ))

    await saga.execute()
```

## Key Concepts

### Compensating Transaction
For every action that can fail, define a compensating action that undoes it:
- Reserve -> Release
- Charge -> Refund
- Send confirmation -> Send cancellation

### Idempotency
Each step must be idempotent. If a step fails and retries, the result must
be the same as if it ran once.

### Reliability
The saga must survive service restarts. Store the saga state in a database:

```sql
CREATE TABLE saga_states (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    current_step TEXT NOT NULL,
    state JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Failure Handling

1. **Retryable failure** - retry the step with backoff
2. **Non-retryable failure** - start compensation
3. **Compensation failure** - need manual intervention (alert!)

## Choreography vs Orchestration

| Aspect | Choreography | Orchestration |
|--------|-------------|---------------|
| Coordination | Implicit (events) | Explicit (coordinator) |
| Coupling | Lower | Higher |
| Complexity | Harder to trace | Easier to trace |
| Scalability | Higher | Lower |
| Best for | Simple flows | Complex flows |

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
