# Graceful Shutdown: How to End Well

A service must not only start but also shut down gracefully. Half of the services
in production just drop connections on restart. This causes data loss, corrupted
state, and angry users.

## What Is Graceful Shutdown

When Kubernetes decides to restart your pod (new deploy, OOM, node draining),
it sends SIGTERM. You have 30 seconds to:

1. Stop accepting new requests
2. Finish in-flight requests
3. Close database connections, cache, queues
4. Return 503 on healthcheck (drain)
5. Save in-memory state if needed

After 30 seconds comes SIGKILL. If you haven't finished - connections leak,
data corrupts, users see errors.

## Python Implementation

```python
import asyncio
import signal
from contextlib import asynccontextmanager


class GracefulShutdown:
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._shutdown = asyncio.Event()
        self._active: set[asyncio.Task] = set()

    def register(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._shutdown.set)

    async def wait(self) -> None:
        await self._shutdown.wait()

    async def shutdown(self) -> None:
        print("Shutting down gracefully...")
        if self._active:
            done, pending = await asyncio.wait(
                self._active, timeout=self.timeout
            )
            for t in pending:
                t.cancel()

    @asynccontextmanager
    async def track(self):
        t = asyncio.current_task()
        self._active.add(t)
        try:
            yield
        finally:
            self._active.discard(t)


# Usage
shutdown = GracefulShutdown()
shutdown.register()

async def handle_request(request):
    async with shutdown.track():
        await process(request)

await shutdown.wait()
await shutdown.shutdown()
```

## FastAPI Integration

```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()
_draining = False

@app.get("/health")
async def health():
    if _draining:
        return {"status": "draining"}, 503
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(
        signal.SIGTERM,
        lambda: asyncio.create_task(handle_sigterm())
    )

async def handle_sigterm():
    global _draining
    _draining = True
    await asyncio.sleep(2)  # Let LB notice
    await db_pool.close()
    await redis.close()
    print("Shutdown complete")
```

## Kubernetes Integration

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]
terminationGracePeriodSeconds: 35
```

The preStop hook gives 5 seconds for the load balancer to notice before SIGTERM.
Then you have 30 more seconds for actual shutdown.

## Common Mistakes

1. **Ignoring signals** - process is killed, data is lost
2. **Infinite wait** - shutdown must have a timeout
3. **Not draining healthcheck** - traffic keeps coming until SIGKILL
4. **Killing children first** - children must be notified after parent stops accepting

## Checklist

- [ ] SIGTERM stops accepting new requests
- [ ] In-flight requests finish within timeout
- [ ] Pools close (connection, thread, goroutine)
- [ ] Queues ACK or NACK properly
- [ ] Healthcheck returns 503 during drain
- [ ] Logs write until the last moment
- [ ] preStop hook configured in K8s

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
