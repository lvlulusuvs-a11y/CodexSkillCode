# Performance Optimization: Complete Reference

**Как оптимизировать Python приложения от миллисекунд до дата-центров.**

---

## 1. Profiling Stack

```python
"""Complete profiling toolkit."""
from __future__ import annotations

import cProfile
import pstats
import io
import time
import functools
from typing import Any, Callable


# Level 1: Quick timing
def timing_decorator(func: Callable) -> Callable:
    """Simple timing decorator."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  {func.__name__}: {elapsed*1000:.1f}ms")
        return result
    return wrapper


# Level 2: cProfile for function-level profiling
def profile_func(output: str = "profile.prof") -> Callable:
    """Profiling decorator with cProfile."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            try:
                result = profiler.runcall(func, *args, **kwargs)
                return result
            finally:
                profiler.dump_stats(output)
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
                ps.print_stats(30)
                print(s.getvalue())
        return wrapper
    return decorator


# Level 3: py-spy (sampling profiler, no code changes)
PY_SPY_USAGE = """
  # Profile running process (no code change)
  py-spy record -o profile.svg --pid 12345
  
  # Profile Python script from start
  py-spy record -o profile.svg -- python myapp.py
  
  # Top-like live view
  py-spy top --pid 12345
  
  # Save as flamegraph
  py-spy record -o flamegraph.svg --duration 30 -- python myapp.py
"""


# Level 4: Memory profiling
def memory_profile(func: Callable) -> Callable:
    """Track memory usage of a function."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from memory_profiler import memory_usage
        mem_usage, result = memory_usage(
            (func, args, kwargs),
            retval=True,
            interval=0.1,
            timestamps=True,
        )
        print(f"  Memory: min={min(mem_usage):.1f}MB "
              f"max={max(mem_usage):.1f}MB "
              f"delta={max(mem_usage)-min(mem_usage):.1f}MB")
        return result
    return wrapper


# Level 5: Line profiler (line-by-line)
LINE_PROFILER_USAGE = """
  @profile  # Not a decorator — line_profiler injects this
  def my_func():
      ...
  
  kernprof -l -v my_script.py
  # Output shows time per line
"""
```

## 2. Optimization Techniques by Category

### 2.1 Data Structures

```python
"""Choosing the right data structure."""

# Lists → Arrays
import array
# arr = array.array('i', [1, 2, 3])  # C array, 4 bytes per element vs 28 for list of ints

# Sets for membership testing (O(1) vs O(n))
membership_test = """
  items_list = [1, 2, 3, ..., 10000]
  items_set = {1, 2, 3, ..., 10000}
  
  if 9999 in items_list:  # O(n) — 10,000 checks
  if 9999 in items_set:   # O(1) — hash lookup
"""

# deque for queue operations
from collections import deque
queue = deque(maxlen=1000)
# queue.append() / queue.popleft() = O(1)
# list.append(0) / list.pop(0) = O(n)

# defaultdict for counting
from collections import defaultdict
counter = defaultdict(int)
counter['key'] += 1  # No need for if key in counter:

# OrderedDict for LRU
from collections import OrderedDict
lru = OrderedDict()
lru['key'] = 'value'
lru.move_to_end('key')  # Recently used
lru.popitem(last=False)  # Remove oldest

# heapq for priority queues
import heapq
heap = []
heapq.heappush(heap, (priority, item))
heapq.heappop(heap)  # Returns lowest priority first
```

### 2.2 String Operations

```python
"""String optimization patterns."""

# ❌ Slow: String concatenation in loop
def slow_concat(items: list[str]) -> str:
    result = ""
    for item in items:
        result += item  # O(n²) — creates new string each time
    return result

# ✅ Fast: join
def fast_concat(items: list[str]) -> str:
    return "".join(items)  # O(n) — single allocation


# ❌ Slow: f-strings in loop
def slow_format(items: list[dict]) -> list[str]:
    return [f"Name: {item['name']}, Age: {item['age']}" for item in items]

# ✅ Fast: template + % (2x faster)
def fast_format(items: list[dict]) -> list[str]:
    template = "Name: %(name)s, Age: %(age)s"
    return [template % item for item in items]


# String to bytes / bytes to string
# str.encode() / bytes.decode() faster than bytes() / str()

# Regular expressions — compile once
import re
PATTERN = re.compile(r"\d{3}-\d{2}-\d{4}")  # Compile once
matches = [m for line in data if PATTERN.search(line)]
```

### 2.3 Loop Optimization

```python
"""Loop optimization patterns."""

# 1. Local variable binding
# ❌ Slow (global lookups)
def slow_sum(items: list[int]) -> int:
    s = 0
    for i in items:
        s += i * 2  # Each iteration looks up 'items', 's', 'i'
    return s

# ✅ Fast (locals)
def fast_sum(items: list[int]) -> int:
    s = 0
    it = items
    for i in it:
        s += i * 2
    return s
# or even faster:
def fastest_sum(items: list[int]) -> int:
    return sum(i * 2 for i in items)


# 2. List comprehensions vs for loops
# List comprehensions 1.5-2x faster (C-level execution)
def comp():
    return [x * 2 for x in range(1000)]

def loop():
    result = []
    for x in range(1000):
        result.append(x * 2)
    return result


# 3. map() vs comprehension (comprehension slightly faster)
list(map(str.upper, items))  # Function call overhead
[s.upper() for s in items]  # Inline, no function call


# 4. any()/all() with generator (short-circuit)
has_positive = any(x > 0 for x in large_list)  # Stops at first positive
```

### 2.4 Function Call Optimization

```python
"""Function call overhead reduction."""

# 1. Inline simple operations
# ❌ Function call overhead for simple operations
def double(x): return x * 2
# ✅ Inline: result = x * 2

# 2. Use local functions for inner loops
@functools.lru_cache(maxsize=128)
def expensive(x): ...

# 3. Default arguments cache
def process(data, config=load_config()):  # load_config called once at definition
    ...

# 4. @staticmethod vs @classmethod vs module-level functions
# Module-level functions are fastest (no instance/class lookup overhead)

# 5. __slots__ reduces attribute lookup overhead and memory
class FastPoint:
    __slots__ = ("x", "y")
    # No __dict__ — saves memory, faster attribute access
```

### 2.5 I/O Optimization

```python
"""I/O optimization patterns."""

# 1. Buffer reads/writes
# ❌ Read byte by byte
with open("file", "rb") as f:
    while byte := f.read(1):
        process(byte)

# ✅ Read in chunks
with open("file", "rb") as f:
    while chunk := f.read(65536):  # 64KB buffer
        process(chunk)


# 2. Memory-mapped files for random access
import mmap
with open("large_file.bin", "rb") as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        # Access like bytearray — no seek/read overhead
        value = mm[1000:2000]


# 3. Async I/O for concurrent operations
import aiofiles
async def read_many(files: list[str]) -> list[str]:
    tasks = [aiofiles.open(f) as f: await f.read() for f in files]
    return await asyncio.gather(*tasks)


# 4. Batch database operations
# ❌ Single inserts
for item in items:
    await db.execute("INSERT INTO t VALUES (?)", [item])

# ✅ Batch insert
await db.executemany("INSERT INTO t VALUES (?)", [(i,) for i in items])
```

### 2.6 Caching Strategies

```python
"""Caching for performance."""

# 1. LRU Cache
@functools.lru_cache(maxsize=1000)
def expensive_function(arg: int) -> int:
    """Cache results in memory."""
    return compute(arg)


# 2. TTL Cache
from functools import lru_cache
import time

def ttl_cache(seconds: int = 60):
    """Cache with TTL."""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache:
                value, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return value
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator


# 3. Redis Cache (for distributed caching)
async def get_or_compute(key: str, compute_func, ttl: int = 300):
    result = await redis.get(key)
    if result:
        return json.loads(result)
    
    value = await compute_func()
    await redis.set(key, json.dumps(value), expire=ttl)
    return value


# 4. Cache stampede protection (doomlock pattern)
# Use SET NX to ensure only one process computes
```

### 2.7 Database Query Optimization

```python
"""Database query optimization."""

# 1. N+1 Query Detection
# ❌ N+1
users = await db.fetch_all("SELECT * FROM users")
for user in users:  # N queries
    orders = await db.fetch_all(f"SELECT * FROM orders WHERE user_id = {user.id}")

# ✅ Single query
users = await db.fetch_all("""
    SELECT u.*, json_agg(o.*) as orders
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
""")


# 2. Indexes for common queries
INDEXES = """
  CREATE INDEX idx_orders_user_id ON orders(user_id);
  CREATE INDEX idx_orders_created ON orders(created_at DESC);
  CREATE INDEX idx_users_email ON users(email);
  
  Composite indexes:
  CREATE INDEX idx_orders_user_status ON orders(user_id, status);
  
  Partial indexes:
  CREATE INDEX idx_active_orders ON orders(user_id) WHERE status = 'active';
"""


# 3. Query optimization tips
QUERY_TIPS = """
  - SELECT specific columns, not *
  - Use LIMIT/OFFSET for pagination (or cursor)
  - Avoid ORDER BY on unindexed columns
  - Use EXISTS instead of COUNT for existence checks
  - Use JOINs instead of subqueries when possible
  - Batch INSERT/UPDATE (batches of 100-1000)
  - Use connection pooling (20-50 connections optimal)
"""
```

## 3. Async Performance

```python
"""Async performance optimization."""

# Event loop overhead:
# ~10µs per task switch
# ~1µs per await
# ~50µs per create_task

# Optimal concurrency:
# I/O-bound: asyncio.Semaphore to limit to 100-1000 concurrent tasks
# CPU-bound: ProcessPoolExecutor (cpu_count * 2)
# Mixed: asyncio + ThreadPoolExecutor

# Avoiding event loop blocking:
EVENT_LOOP_TIPS = """
  - Never call time.sleep() — use asyncio.sleep()
  - Never do CPU-bound work in async functions — offload to executor
  - Never use blocking I/O (requests, file reads) — use aiohttp, aiofiles
  - Monitor event loop delay (> 100ms = problem)
  - Use uvloop for 2x faster event loop
"""

# uvloop setup:
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
```

## 4. PyPy (Drop-in 4x Speedup)

```python
"""PyPy compatibility and optimization."""

# PyPy is ~4x faster for pure Python code
# But: C extensions (numpy, pandas) don't work or are slower
# Use: pure Python code, CPU-bound logic, string processing

# PyPy optimized patterns:
PYPY_TIPS = """
  PyPy loves:
    - Loops (JIT-compiled)
    - Object-oriented code (better optimization)
    - String operations
    - Dynamic dispatch (JIT inlines and optimizes)
  
  PyPy doesn't love:
    - C extensions (CPython API)
    - Very large arrays of simple types (use __slots__)
    - Single-threaded CPU-bound with GIL (PyPy has no GIL but STM is experimental)
"""
```

## 5. Performance Benchmarking Framework

```python
"""Simple benchmarking framework."""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    total_time: float
    times: list[float] = field(default_factory=list)
    
    @property
    def avg_ms(self) -> float:
        return (self.total_time / self.iterations) * 1000
    
    @property
    def min_ms(self) -> float:
        return min(self.times) * 1000 if self.times else 0
    
    @property
    def max_ms(self) -> float:
        return max(self.times) * 1000 if self.times else 0
    
    @property
    def median_ms(self) -> float:
        return statistics.median(self.times) * 1000 if self.times else 0


class Benchmark:
    """Benchmark functions and compare."""
    
    def run(self, fn: Callable, name: str = "", iterations: int = 1000) -> BenchmarkResult:
        """Run benchmark."""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            fn()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        total = sum(times)
        return BenchmarkResult(
            name=name or fn.__name__,
            iterations=iterations,
            total_time=total,
            times=times,
        )
    
    def compare(self, *funcs: Callable, iterations: int = 10000) -> None:
        """Compare multiple implementations."""
        results = []
        for fn in funcs:
            result = self.run(fn, iterations=iterations)
            results.append(result)
            print(f"  {result.name}: avg={result.avg_ms:.2f}ms "
                  f"min={result.min_ms:.2f}ms max={result.max_ms:.2f}ms")
        
        # Show speedup relative to slowest
        results.sort(key=lambda r: r.avg_ms)
        fastest = results[0].avg_ms
        print(f"\n  Fastest: {results[0].name} ({results[0].avg_ms:.2f}ms)")
        for r in results[1:]:
            ratio = r.avg_ms / fastest
            print(f"  {r.name} is {ratio:.1f}x slower")
```


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
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
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.
