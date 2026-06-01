# Background Tasks: Choose Your Weapon

Background tasks are a permanent headache. Here is how I choose between the options.

## When You Need Background Tasks

1. **Sending emails** after user registration (dont block the response)
2. **Processing files** (images, CSVs, documents)
3. **Scheduled jobs** (reports, cleanup, sync)
4. **External API calls** (slow, unreliable third parties)
5. **Retry queues** (operations that may fail temporarily)

## Option 1: asyncio.create_task

```python
@app.post("/register")
async def register(request: RegisterRequest):
    user = await user_service.create(request)

    # Fire and forget
    asyncio.create_task(send_welcome_email(user.email))

    return {"user_id": user.id}
```

**Pros**: Simple, no infrastructure, zero latency.
**Cons**: Lost on restart, no retry, no monitoring, no backpressure.

**Use when**: Task is truly fire-and-forget and data loss is acceptable.

### Better Version with Tracking

```python
background_tasks: set[asyncio.Task] = set()

@app.post("/register")
async def register(request: RegisterRequest):
    user = await user_service.create(request)
    task = asyncio.create_task(send_welcome_email(user.email))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    return {"user_id": user.id}
```

## Option 2: ARQ (Async Redis Queue)

Lightweight, async-native task queue.

```python
from arq import create_pool, Worker
from arq.connections import RedisSettings


# Task function
async def send_welcome_email(ctx, user_email: str):
    await email_service.send_welcome(user_email)
    return {"email": user_email, "status": "sent"}


# Producer (your app)
async def enqueue_welcome_email(email: str):
    redis = await create_pool(RedisSettings())
    job = await redis.enqueue_job("send_welcome_email", email)
    return job.id


# Worker (separate process)
async def run_worker():
    redis = await create_pool(RedisSettings())
    worker = Worker(
        functions=[send_welcome_email],
        redis_pool=redis,
        poll_delay=0.1,
        max_jobs=10,
    )
    await worker.main()
```

**Pros**: Async-native, lightweight, built-in retry, healthchecks.
**Cons**: Needs Redis, no built-in scheduling.

## Option 3: Celery (Full Featured)

```python
from celery import Celery

app = Celery("tasks", broker="redis://redis:6379")

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_payment(self, order_id: str):
    try:
        return payment_service.charge(order_id)
    except RetryableError as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)

@app.task
def send_notification(user_id: str, message: str) -> None:
    notification_service.send(user_id, message)
```

**Pros**: Everything included - retry, schedule, rate limiting, monitoring.
**Cons**: Heavy, needs broker (Redis/RabbitMQ), complex to configure.

## Retry Policy Design

```python
from dataclasses import dataclass
from enum import Enum


class RetryableError(Exception):
    """Error that can be retried."""
    pass

class NonRetryableError(Exception):
    """Error that should NOT be retried."""
    pass


@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 3600.0
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)

    def should_retry(self, error: Exception) -> bool:
        return not isinstance(error, NonRetryableError)
```

## My Recommendation

| Scenario | Solution |
|----------|----------|
| Simple, non-critical | asyncio.create_task |
| Need persistence | ARQ |
| Heavy enterprise | Celery |
| Already have RabbitMQ | Celery |
| Scheduling needed | Celery beat or APScheduler |
| Lambda environment | SQS + Lambda |

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written
