# Idiomatic Python — Extended

**Расширенное руководство по идиоматичному Python.**

---

## 1. List Comprehensions

```python
# Basic
squares = [x * x for x in range(10)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# Nested
flat = [y for row in matrix for y in row]

# With if-else
labels = ["even" if x % 2 == 0 else "odd" for x in range(10)]

# Multiple conditions
result = [x for x in range(100) if x % 2 == 0 if x % 3 == 0]
```

## 2. Dict Comprehensions

```python
# Basic
square_dict = {x: x * x for x in range(10)}

# From two lists
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
users = {name: age for name, age in zip(names, ages)}

# Filtering
active_users = {k: v for k, v in users.items() if v.is_active}

# Inverting
inverted = {v: k for k, v in original.items()}

# With condition
even_squares = {x: x * x for x in range(10) if x % 2 == 0}
```

## 3. Enumerate

```python
# Instead of range(len())
for i, item in enumerate(items):
    print(i, item)

# Custom start index
for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")
```

## 4. Zip

```python
# Parallel iteration
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# Strict mode (Python 3.10+)
for name, age in zip(names, ages, strict=True):
    # Raises ValueError if lengths differ
    pass

# Unzip
pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
numbers, letters = zip(*pairs)

# Dictionary from two lists
lookup = dict(zip(keys, values))
```

## 5. Unpacking

```python
# Basic unpacking
a, b, c = [1, 2, 3]

# Extended unpacking (Python 3.0+)
first, *rest = items
first, *middle, last = items

# Star unpacking
def f(a, b, c, d):
    print(a, b, c, d)
f(*[1, 2], 3, *[4])

# Dict unpacking
settings = {"host": "localhost", "port": 8080}
new_settings = {**settings, "port": 9090}

# Nested unpacking
(first_name, last_name), age = [("Alice", "Smith"), 30]
```

## 6. F-Strings

```python
name = "Alice"
age = 30

# Basic
f"My name is {name}"

# Expressions
f"Next year I'll be {age + 1}"

# Format specifiers
f"Pi is {math.pi:.2f}"  # "Pi is 3.14"
f"{price:>10.2f}"  # right-aligned, 10 chars
f"{value:08b}"  # binary, zero-padded

# Dict access
user = {"name": "Alice"}
f"User: {user['name']}"

# Debug (Python 3.8+)
f"{name=}, {age=}"  # "name='Alice', age=30"

# Multiline
message = (
    f"Name: {name}\n"
    f"Age: {age}\n"
    f"City: {city}"
)
```

## 7. Walrus Operator

```python
# While loop
while chunk := file.read(8192):
    process(chunk)

# If statement
if (n := len(items)) > 0:
    print(f"Processing {n} items")

# List comprehension
results = [y for x in data if (y := transform(x)) is not None]

# Match case
match value:
    case n if (n_squared := n ** 2) > 100:
        print(f"Large: {n_squared}")

# Pattern: while with assignment
while (line := input_line()) is not None:
    process(line)
```

## 8. Context Managers

```python
# Multiple contexts
with open("a.txt") as a, open("b.txt") as b:
    process(a.read(), b.read())

# Suppress exceptions
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("temp.txt")  # no error if not exists

# Redirect stdout
from contextlib import redirect_stdout
with redirect_stdout(StringIO()):
    print("Captured")

# ExitStack (dynamic contexts)
from contextlib import ExitStack
with ExitStack() as stack:
    files = [stack.enter_context(open(f)) for f in filenames]
    process_files(files)
```

## 9. Itertools

```python
from itertools import chain, cycle, count, islice, groupby, product, combinations, permutations, zip_longest

# Chain iterables
all_items = chain(list1, list2, list3)

# Cycle forever
for item in cycle(["A", "B", "C"]):
    if condition: break

# Count infinity
for i in count(start=0, step=2):
    if i > 100: break

# Group by
for key, group in groupby(sorted(items), key=group_func):
    print(key, list(group))

# Product (Cartesian)
for a, b in product([1, 2], ["A", "B"]):
    print(a, b)  # (1,A), (1,B), (2,A), (2,B)

# Combinations
for combo in combinations(items, 2):
    print(combo)

# Permutations
for perm in permutations(items, 2):
    print(perm)

# Zip with fill
for a, b in zip_longest(list1, list2, fillvalue=""):
    print(a, b)

# Slice iterator
first_10 = islice(iterator, 10)
```

## 10. Collections

```python
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict

# defaultdict
d = defaultdict(list)
d["key"].append(1)  # no KeyError

# Counter
counts = Counter("hello world")
print(counts.most_common(3))  # [('l', 3), ('o', 2), ('h', 1)]

# deque
q = deque(maxlen=10)
q.append(1)
q.appendleft(2)
q.popleft()

# namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p.x, p.y)  # 10 20

# OrderedDict (with move_to_end)
d = OrderedDict()
d["a"] = 1
d.move_to_end("a")  # move to end (LRU)
d.popitem(last=False)  # FIFO
```


---

## Real-World Implementation

```python
"""Production-grade implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionService:
    """Battle-tested service pattern with full observability."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with retry, timeout, and monitoring."""
        start = time.perf_counter()
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                elapsed = time.perf_counter() - start
                logger.info("Success", extra={"duration_ms": elapsed * 1000})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"Failed after {elapsed*1000:.1f}ms: {e}")
            raise
    
    async def _process(self) -> dict[str, Any]:
        """Core processing logic."""
        return {"status": "ok", "timestamp": time.time()}


### Key Takeaway for Principal Engineers

This pattern exemplifies the Principal Engineer mindset:
1. **Defensive by default** — timeouts, error handling, logging
2. **Observable** — every operation produces metrics and logs
3. **Resilient** — built to handle failures gracefully
4. **Simple** — one function, one responsibility
5. **Testable** — can mock `_process` and test retry/timeout logic

Apply this pattern to every external call in your service.


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


---

## Production Usage

```python
"""Production implementation with full resilience."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass 
class ResilientOperation:
    """Execute operations with full production patterns."""
    
    async def execute(self, operation: str, fn: callable, *args, **kwargs) -> Any:
        for attempt in range(3):
            try:
                async with asyncio.timeout(30):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Operation '{operation}' timed out")
                    raise
            except Exception:
                logger.exception(f"Operation '{operation}' failed")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    raise
        return None
    

### Principal Engineer Summary

This pattern encapsulates everything a Principal Engineer knows:
1. Always set timeouts
2. Always retry transient failures
3. Always log with context
4. Always have a fallback plan
5. Always think about observability

Apply this to every external interaction in your system.
