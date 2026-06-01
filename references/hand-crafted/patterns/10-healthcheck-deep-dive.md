# Health Check: Design for Resilience

Healthcheck is a contract between your service and the orchestrator.
How you design it determines how your service deploys and recovers.

## Three Levels of Health

### Liveness - Is the Process Alive?

```python
@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
```

Only checks that the process responds to HTTP. NO external dependencies.

If liveness checks the DB, Kubernetes restarts your pod when DB is down.
But restarting doesnt fix the DB - it only makes the problem worse.

### Readiness - Is the Service Ready for Traffic?

```python
@app.get("/health/ready")
async def readiness():
    checks = {
        "db": await ping_db(),
        "cache": await ping_cache(),
        "queue": await ping_queue(),
    }
    ready = all(checks.values())
    return {"status": "ready" if ready else "not_ready", "checks": checks}
```

Load balancer doesnt send traffic when readiness != 200.

### Startup - Has Initialization Finished?

For slow startups: ML model loading, cache warmup, DB migrations.

## Configuration

| Check | Period | Failure | Effect |
|-------|--------|---------|--------|
| liveness | 10s | 3 | restart pod |
| readiness | 5s | 1 | remove from LB |
| startup | 2s | 30 | wait for init |

## Graceful Drain Integration

```python
_draining = False

@app.get("/health/ready")
async def readiness():
    if _draining:
        return {"status": "draining"}, 503
    return await check_dependencies()
```

## What NOT to Check

- **Disk usage** - thats monitoring, not health
- **Request latency** - not a health concern
- **Business metrics** - unrelated to pod health
- **Update availability** - not relevant here
- **Other services health** - cascading failures

## Monitoring Healthchecks

```prometheus
# HELP healthcheck_total Total healthcheck results
# TYPE healthcheck_total counter
healthcheck_total{check="liveness", status="pass"} 10000
healthcheck_total{check="readiness", status="fail"} 3
healthcheck_duration_seconds{check="readiness"} 0.045
```

If readiness fails more than 1% - alert.
If liveness fails - the pod is restarting (thats working as intended).

## Real World Experience

We once had a service that checked the DB in its liveness probe.
When the DB had a brief hiccup, Kubernetes restarted ALL pods.
The restart storm killed the service for 15 minutes.

Now: liveness = just HTTP response. readiness = deep check.

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
