# Memory Management: Leaks, GC, and Optimization

Memory leaks in Python happen differently than in C/C++. You cannot leak
memory in CPython, but you can hold references to objects that should be freed.

## Common Memory Issues

### 1. Circular References with __del__

```python
class Resource:
    def __del__(self):
        print(f"Cleaning up {self.id}")

class Container:
    def __init__(self):
        self.resource = Resource()

    def __del__(self):
        print(f"Container {self.id} gone")

# Circular reference
def create_leak():
    container = Container()
    container.resource.container_ref = container  # circular!
    # Neither Container nor Resource will be garbage collected
```

### 2. Caching Without Bounds

```python
class UserService:
    def __init__(self):
        self._cache = {}  # Unlimited growth!

    async def get_user(self, user_id: str):
        if user_id not in self._cache:
            self._cache[user_id] = await db.get_user(user_id)
        return self._cache[user_id]
    # Every user ever requested stays in memory forever
```

### 3. Closure Variables

```python
def create_callbacks():
    callbacks = []
    for i in range(1000):
        # Each callback captures the entire locals()!
        callbacks.append(lambda: process(i))
    # Each lambda keeps a reference to the closure environment
    return callbacks
```

## Detection Tools

### 1. objgraph for Object Graphs

```python
import objgraph

# Show most common objects
objgraph.show_most_common_types(limit=20)

# Show growth between snapshots
objgraph.show_growth(limit=10)

# Show what keeps a specific object alive
obj = some_object
objgraph.show_backrefs([obj], max_depth=5, filename="backrefs.png")
```

### 2. gc Module

```python
import gc

# Enable debugging
gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)

# Force garbage collection
collected = gc.collect()
print(f"Collected {collected} objects")

# Find unreachable objects with __del__
for obj in gc.garbage:
    print(f"Unreachable: {obj}")
```

## Prevention Strategies

### 1. Use Weak References for Caches

```python
import weakref

class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        self._cache[key] = value
```

### 2. Use LRU Cache

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user(user_id: str) -> User:
    return db.get_user(user_id)

# Cache stats
print(get_user.cache_info())
# CacheInfo(hits=500, misses=100, maxsize=1000, currsize=100)
```

### 3. Context Managers for Resources

```python
class DatabaseConnection:
    async def __aenter__(self):
        self.conn = await create_connection()
        return self.conn

    async def __aexit__(self, *args):
        await self.conn.close()


# Always use context manager
async with DatabaseConnection() as conn:
    await conn.execute("SELECT * FROM users")
# Connection is closed even if an exception occurs
```

### 4. Limit Queue/Buffer Sizes

```python
from collections import deque

# Bounded queue prevents unbounded memory growth
queue = deque(maxlen=1000)
queue.append(item)  # If full, removes oldest item
```

## Memory Profiling in Production

```python
import tracemalloc
import psutil

# System-level memory
process = psutil.Process()
print(f"RSS: {process.memory_info().rss / 1024 / 1024:.1f} MB")

# Python-level memory
tracemalloc.start()
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

for stat in top_stats[:10]:
    print(f"{stat.count:>5} blocks, {stat.size / 1024:.1f} KB: {stat.traceback.format()[0]}")
```

## Best Practices

1. **No unbounded caches** - always set maxsize or TTL
2. **No __del__** - use weakref or context managers instead
3. **No circular references** - use weakref for parent references
4. **Use __slots__** for classes with many instances
5. **Use generators** instead of lists for large datasets
6. **Batch processing** - dont load everything into memory
7. **Monitor** RSS memory in production
8. **Set limits** on queue sizes, cache sizes, connection pools

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
