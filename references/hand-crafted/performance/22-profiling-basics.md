# Profiling: Finding Bottlenecks

You cannot optimize what you do not measure. Profiling tells you where the
time is actually spent, not where you think it is spent.

## The Number One Rule

Do not optimize without profiling. The bottleneck is never where you expect it.

## CPU Profiling with cProfile

```python
import cProfile
import pstats
from io import StringIO


def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(20)  # Top 20 functions by cumulative time
    print(stream.getvalue())
    return result


# Usage
profile_function(process_orders, order_data)
```

### Interpreting Results

Look for:
1. Functions that take the most cumulative time
2. Functions called many times (even if fast individually)
3. Surprising entries (things you didnt expect to be slow)

## Async Profiling with py-spy

```bash
# Profile a running process
py-spy record -o profile.svg --pid 12345

# Profile a Python script
py-spy record -o profile.svg -- python my_script.py

# Top-like live view
py-spy top --pid 12345
```

py-spy is a sampling profiler. It does not modify the running code.
Works with async Python.

## Memory Profiling

```python
from memory_profiler import profile


@profile
def process_large_dataset():
    data = load_all_data()     # Line 1: see memory usage
    transformed = transform(data)  # Line 2: see memory usage
    result = aggregate(transformed)  # Line 3: see memory usage
    return result
```

### Tracking Memory Leaks

```python
import tracemalloc

tracemalloc.start()

# Take a snapshot
snapshot1 = tracemalloc.take_snapshot()

# Run the suspect code
process_orders()

# Take another snapshot
snapshot2 = tracemalloc.take_snapshot()

# Compare
stats = snapshot2.compare_to(snapshot1, "lineno")
for stat in stats[:10]:
    print(stat)
```

## Tracing and Observability-based Profiling

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp import OTLPSpanExporter
import time


tracer = trace.get_tracer(__name__)

@contextlib.contextmanager
def profile_span(name: str, attributes: dict = None):
    start = time.monotonic()
    try:
        with tracer.start_as_current_span(name) as span:
            if attributes:
                span.set_attributes(attributes)
            yield
    finally:
        duration = (time.monotonic() - start) * 1000
        metrics.duration_ms.labels(operation=name).observe(duration)
```

## Common Bottlenecks

### 1. N+1 Database Queries

```python
# Bad: 1 query for users + N queries for orders
users = await db.fetch("SELECT * FROM users")
for user in users:
    orders = await db.fetch("SELECT * FROM orders WHERE user_id = $1", user["id"])

# Good: 2 queries total
users = await db.fetch("SELECT * FROM users")
order_map = await group_orders_by_user(users)
```

### 2. Serial JSON Serialization

```python
# Bad: 1000 small serializations
for item in items:
    json.dumps(item.to_dict())

# Good: batch serialization
json.dumps([item.to_dict() for item in items])
```

### 3. Unbounded List Growth

```python
# Bad: process creates list, never trims
results = []
for item in items:
    results.append(process(item))
return results

# Good: generator/streaming
for item in items:
    yield process(item)
```

### 4. Synchronous Calls in Async Code

```python
# Bad: blocks event loop
async def handle(request):
    data = requests.get("http://api.example.com")
    return process(data)

# Good: async call
async def handle(request):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://api.example.com")
    return process(response.json())
```

## What to Measure

1. **Throughput** - requests per second
2. **Latency** - p50, p95, p99 response times
3. **Error rate** - percentage of failed requests
4. **CPU usage** - percentage, per core
5. **Memory** - total, heap, GC pressure
6. **I/O** - database queries, external API calls
7. **Lock contention** - time waiting for locks
8. **Context switches** - overhead of switching between tasks

## When to Stop Optimizing

When the performance is good enough for your use case.

| Use Case | Target p99 Latency | Target Throughput |
|----------|-------------------|------------------|
| API response | < 200ms | 1000 rps per instance |
| Database query | < 100ms | 100 qps per connection |
| Background job | < 5 min | depends on batch size |
| File processing | < 10 min | > 100 MB/s |

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```

## Practice

Apply this concept to your codebase today. Find one place where it fits.

### Exercise

1. Read the pattern
2. Find a real use case in your project
3. Implement it
4. Write a test
5. Reflect on whether it improved the code

### Code

```python
def practice():
    """Implement what you learned."""
    return "done"
```
