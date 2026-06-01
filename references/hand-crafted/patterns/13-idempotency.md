# Idempotency: Reliability in Distributed Systems

Idempotency means calling an operation multiple times produces the same result
as calling it once. Without it, distributed systems fail in subtle ways.

## The Problem

HTTP has "at-least-once" delivery semantics. A client sends POST, server
processes it, response is lost. Client retries. Now you have duplicates.

```python
# First request
POST /orders {"user_id": "123", "product_id": "456"}
-> 201 Created (order_1)

# Client didnt get response, retries
POST /orders {"user_id": "123", "product_id": "456"}
-> 201 Created (order_2)  # DUPLICATE!
```

This happens more often than you think. Network is unreliable.

## Solution: Idempotency-Key Header

```python
import uuid
from fastapi import Header


class IdempotentHandler:
    def __init__(self, redis, ttl: int = 86400):
        self.redis = redis
        self.ttl = ttl

    async def handle(self, key: str, handler, *args, **kwargs):
        # Check if we already processed this key
        existing = await self.redis.get(f"idemp:{key}")
        if existing:
            return existing  # Return cached response

        # Execute the operation
        response = await handler(*args, **kwargs)

        # Cache the response
        await self.redis.set(f"idemp:{key}", response, ex=self.ttl)
        return response


handler = IdempotentHandler(redis)

@app.post("/orders")
async def create_order(
    request: CreateOrder,
    idempotency_key: str = Header(alias="Idempotency-Key"),
):
    return await handler.handle(
        idempotency_key, _create_order, request
    )
```

The client generates a UUID and sends it as a header.
The server deduplicates based on this key.

## Database-Level Idempotency

Use UNIQUE constraints as the last line of defense:

```sql
-- Prevent duplicate payments
ALTER TABLE payments ADD CONSTRAINT uq_payment_idemp
    UNIQUE (idempotency_key);

-- Safe insert with ON CONFLICT
INSERT INTO payments (user_id, amount, idempotency_key)
VALUES ($1, $2, $3)
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING *;
```

## Idempotency at Different Levels

### Level 1: HTTP Layer
- Client sends Idempotency-Key
- Server caches responses
- Simple, but cache can be lost

### Level 2: Database Layer  
- UNIQUE constraint on business key
- Atomic INSERT with ON CONFLICT
- Survives server restarts

### Level 3: Business Logic Layer
- Distributed lock + DB constraint
- Handles race conditions
- The most robust approach

```python
async def process_payment(user_id: str, amount: Money) -> PaymentResult:
    idemp_key = f"payment:{user_id}:{amount}:{datetime.utcnow().date()}"

    # Distributed lock prevents race conditions
    async with redis.lock(f"lock:{idemp_key}", ttl=30):
        # Double-check
        existing = await db.fetchrow(
            "SELECT * FROM payments WHERE idempotency_key = $1",
            idemp_key
        )
        if existing:
            return PaymentResult.from_row(existing)

        # Process payment
        result = await charge_payment(user_id, amount)

        # Store with idempotency key
        await db.execute("""
            INSERT INTO payments (user_id, amount, idempotency_key)
            VALUES ($1, $2, $3)
        """, user_id, amount, idemp_key)

        return result
```

## What Response to Return for Duplicate

Return 200 OK (not 409 Conflict), because from the clients perspective
the operation was successful:

```json
{
    "status": "completed",
    "previous_response": true,
    "data": {
        "order_id": "ord_123",
        "created_at": "2026-05-31T12:00:00Z"
    }
}
```

## Key Management

- Keys live 24 hours (configurable)
- Never store idempotency keys forever (memory leak)
- Client can generate new keys per request
- Server must not crash if it receives the same key twice

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |
