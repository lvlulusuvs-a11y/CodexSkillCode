# Python Developer Reference

**Полный справочник Python-разработчика. От синтаксиса до продвинутых приёмов.**

---

## 1. Core Syntax Reference

### 1.1 Type Annotations

```python
from __future__ import annotations

# Basic types
name: str = "Alice"
age: int = 30
height: float = 1.75
active: bool = True

# Collections
from collections.abc import Sequence, Mapping, Iterable, Callable
names: Sequence[str] = ["Alice", "Bob"]
lookup: Mapping[str, int] = {"a": 1, "b": 2}

# Optional / Union
from typing import Optional, Union
maybe_name: Optional[str] = None  # str | None
result: Union[int, str] = 42     # int | str (Python 3.10+: int | str)

# Aliases
type UserID = int
type JSON = dict[str, Any]

# Callable
Handler = Callable[[int, str], bool]
AsyncHandler = Callable[[int], Awaitable[bool]]
```

### 1.2 Comprehensions

```python
# List
squares = [x * x for x in range(10)]
evens = [x for x in range(10) if x % 2 == 0]

# Dict
square_dict = {x: x * x for x in range(10)}
filtered = {k: v for k, v in items.items() if v > 0}

# Set
unique = {x % 3 for x in range(100)}

# Generator (lazy)
total = sum(x * x for x in range(1000000))

# Nested
matrix = [[i * j for j in range(5)] for i in range(5)]
flat = [x for row in matrix for x in row]
```

### 1.3 Context Managers

```python
# Built-in
with open("file.txt") as f:
    data = f.read()

with lock:
    critical_section()

# Multiple
with open("a.txt") as a, open("b.txt") as b:
    ...

# Async
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()
```

### 1.4 Pattern Matching (Python 3.10+)

```python
# match/case
def process(value: Any) -> str:
    match value:
        case 0:
            return "zero"
        case 1 | 2 | 3:
            return "small"
        case int(n) if n > 100:
            return "large"
        case str(s):
            return f"string: {s}"
        case [a, b, *rest]:
            return f"list: {a}, {b}"
        case {"name": name, "age": age}:
            return f"dict: {name}, {age}"
        case _:
            return "unknown"
```

### 1.5 Walrus Operator (:=)

```python
# Assignment expression
if (n := len(items)) > 0:
    print(f"Found {n} items")

# In comprehension
results = [y for x in data if (y := process(x)) is not None]

# In while
while (line := file.readline()) != "":
    process(line)
```

## 2. Standard Library Reference

### 2.1 collections

```python
from collections import (
    defaultdict, Counter, deque, 
    OrderedDict, ChainMap, namedtuple,
)

# defaultdict — auto-initialize
groups = defaultdict(list)
groups["a"].append(1)  # doesn't need to check existence

# Counter — count elements
freq = Counter("hello world")
most_common = freq.most_common(3)

# deque — double-ended queue
queue = deque(maxlen=100)
queue.append(1)
queue.appendleft(2)
first = queue.popleft()

# ChainMap — merge without copy
defaults = {"host": "localhost", "port": 8080}
overrides = {"port": 9000}
config = ChainMap(overrides, defaults)

# namedtuple — lightweight immutable
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
```

### 2.2 functools

```python
from functools import (
    lru_cache, cached_property, 
    partial, wraps, singledispatch,
)

# Caching
@lru_cache(maxsize=128)
def expensive(n: int) -> int:
    return n * n

@cached_property
def computed(self) -> float:
    return self.a + self.b

# Partial application
base_two = partial(int, base=2)
result = base_two("1000")  # 8

# Single dispatch (overload by type)
@singledispatch
def serialize(obj): raise NotImplementedError

@serialize.register
def _(obj: User) -> str: return f"User({obj.id})"

@serialize.register
def _(obj: Order) -> str: return f"Order({obj.id})"
```

### 2.3 itertools

```python
from itertools import (
    chain, cycle, count, repeat,
    groupby, islice, product, 
    permutations, combinations, zip_longest,
)

# Infinite iterators
for i in count(0):  # 0, 1, 2, ...
    if i > 10: break

for item in cycle(["a", "b"]):  # a, b, a, b, ...
    ...

# Combinations
list(combinations([1, 2, 3], 2))  # (1,2), (1,3), (2,3)
list(permutations([1, 2, 3], 2))  # (1,2), (1,3), (2,1), (2,3), (3,1), (3,2)

# Group
for key, group in groupby(sorted(data), key=lambda x: x["type"]):
    print(key, list(group))

# Chunking
def chunks(iterable, size):
    iterator = iter(iterable)
    return iter(lambda: list(islice(iterator, size)), [])
```

### 2.4 pathlib

```python
from pathlib import Path

# Path operations
path = Path("src") / "main.py"
path = Path.home() / "project" / "data.json"
path = Path.cwd() / "config.yaml"

# Common operations
path.exists()
path.is_file()
path.is_dir()
path.name         # "main.py"
path.stem         # "main"
path.suffix       # ".py"
path.parent       # Path("src")
path.resolve()    # absolute path

# Reading/writing
path.read_text()
path.write_text("content")
path.read_bytes()
path.write_bytes(b"content")

# Directory operations
for py_file in Path.cwd().rglob("*.py"):
    ...

# Create directories
path.mkdir(parents=True, exist_ok=True)
```

### 2.5 typing

```python
from typing import (
    TypeVar, Generic, Protocol,
    Literal, Final, TypedDict,
    ParamSpec, Self, overload,
)

# TypeVar
T = TypeVar("T")
K = TypeVar("K", int, str)

# Generic
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Protocol (structural typing)
class Drawable(Protocol):
    def draw(self) -> None: ...

# Literal
def set_mode(mode: Literal["read", "write"]) -> None: ...

# TypedDict
class Movie(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]

# Self (Python 3.11+)
class Builder:
    def set_name(self, name: str) -> Self: ...
```

### 2.6 dataclasses

```python
from dataclasses import dataclass, field, asdict, astuple

@dataclass(frozen=True, order=True, slots=True)
class User:
    id: int
    name: str = field(compare=False)
    email: str = field(repr=False)
    tags: list[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Name required")

# Operations
user = User(1, "Alice", "alice@test.com")
data = asdict(user)  # dict
tup = astuple(user)  # tuple
```

### 2.7 asyncio

```python
import asyncio

# Create task
task = asyncio.create_task(coro())

# Gather
results = await asyncio.gather(coro1(), coro2(), return_exceptions=True)

# TaskGroup (3.11+)
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(coro1())
    t2 = tg.create_task(coro2())

# Timeout
async with asyncio.timeout(5.0):
    result = await slow_operation()

# Queue
queue = asyncio.Queue(maxsize=100)
await queue.put(item)
item = await queue.get()

# Synchronization
lock = asyncio.Lock()
event = asyncio.Event()
sem = asyncio.Semaphore(10)
```

## 3. String Methods

```python
# Basic
s = "hello world"
s.upper()        # "HELLO WORLD"
s.lower()        # "hello world"
s.title()        # "Hello World"
s.capitalize()   # "Hello world"
s.strip()        # remove whitespace
s.lstrip()       # left strip
s.rstrip()       # right strip

# Search
s.startswith("hello")
s.endswith("world")
s.find("world")    # index or -1
s.index("world")   # index or ValueError
s.count("o")       # 2
"hello" in s       # True

# Split/Join
s.split()          # ["hello", "world"]
s.split(",")       # by separator
", ".join(["a", "b"])  # "a, b"
s.partition(" ")   # ("hello", " ", "world")

# Replace
s.replace("world", "Python")
s.translate(str.maketrans({"o": "0", "l": "1"}))

# Check
s.isalpha()   # all letters
s.isdigit()   # all digits
s.isalnum()   # letters + digits
s.isspace()   # whitespace

# Format
f"Hello {name}"
"Hello {}".format(name)
"%(name)s" % {"name": "Alice"}
```

## 4. File I/O

```python
# Text
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()           # whole file
    line = f.readline()          # one line
    lines = f.readlines()        # list of lines
    for line in f:               # iterator
        process(line)

# Binary
with open("file.bin", "rb") as f:
    data = f.read(1024)  # read 1KB

# Write
with open("file.txt", "w") as f:
    f.write("content")
    f.writelines(["line1\n", "line2\n"])

# JSON
import json
with open("data.json") as f:
    data = json.load(f)
with open("data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# CSV
import csv
with open("data.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"])
```

## 5. Exception Handling

```python
# Basic
try:
    result = risky_operation()
except ValueError as e:
    logger.error("Value error: %s", e)
except (IOError, OSError) as e:
    logger.error("IO error: %s", e)
except Exception:
    logger.exception("Unexpected error")
    raise
else:
    print("No error occurred")
finally:
    cleanup()

# Custom exceptions
class AppError(Exception):
    def __init__(self, message: str, code: str = "ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

# Raising with cause
try:
    external_call()
except ConnectionError as e:
    raise ServiceError("External service unavailable") from e

# Suppress
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("temp.txt")
```

## 6. Regular Expressions

```python
import re

# Matching
pattern = r"\d{3}-\d{2}-\d{4}"
match = re.search(pattern, text)
match = re.match(pattern, text)  # from start
matches = re.findall(pattern, text)  # all matches
matches = re.finditer(pattern, text)  # iterator of matches

# Groups
pattern = r"(\d{3})-(\d{2})-(\d{4})"
match = re.search(pattern, text)
if match:
    area = match.group(1)
    prefix = match.group(2)
    number = match.group(3)

# Named groups
pattern = r"(?P<area>\d{3})-(?P<num>\d{7})"
match = re.search(pattern, text)
area = match.group("area")

# Replace
result = re.sub(r"\s+", " ", text)  # normalize whitespace
result = re.sub(r"\d{3}-\d{4}", "XXX-XXXX", text)  # mask

# Compile (for reuse)
phone_pattern = re.compile(r"\d{3}-\d{2}-\d{4}")
matches = phone_pattern.findall(large_text)

# Common patterns
email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
url = r"https?://[^\s/$.?#].[^\s]*"
ipv4 = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
date = r"\d{4}-\d{2}-\d{2}"
phone = r"\+?1?\d{10,11}"
```

## 7. Common Algorithms

### Binary Search
```python
def binary_search(arr: list[int], target: int) -> int:
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Quick Sort
```python
def quicksort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### Merge Sort
```python
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left: list[int], right: list[int]) -> list[int]:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### Dijkstra (Shortest Path)
```python
import heapq

def dijkstra(graph: dict[int, dict[int, int]], start: int) -> dict[int, float]:
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        if current_dist > distances[current]:
            continue
        for neighbor, weight in graph[current].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

### LRU Cache
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self._cache = OrderedDict()
        self._capacity = capacity
    
    def get(self, key: str) -> Any:
        if key not in self._cache:
            return -1
        self._cache.move_to_end(key)
        return self._cache[key]
    
    def put(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)
```

## 8. OS and System

```python
import os, sys, platform

# Environment
os.environ.get("DATABASE_URL", "default")
os.environ["PATH"] = "/usr/local/bin:" + os.environ["PATH"]

# Filesystem
os.listdir(".")
os.makedirs("path/to/dir", exist_ok=True)
os.remove("file.txt")
os.rename("old.txt", "new.txt")

# Process
os.getpid()
os.getcwd()
os.chdir("/tmp")
sys.argv  # command line args
sys.exit(0)  # exit code

# Platform
platform.system()     # Linux, Darwin, Windows
platform.release()    # kernel version
sys.platform          # linux, darwin, win32
```

## 9. JSON and Serialization

```python
import json, pickle, msgpack

# JSON
data = json.dumps(obj, indent=2, ensure_ascii=False, default=str)
obj = json.loads(data)

# Custom encoder
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

data = json.dumps(obj, cls=DateTimeEncoder)

# Pickle (Python only, faster)
data = pickle.dumps(obj, protocol=5)
obj = pickle.loads(data)

# msgpack (compact binary)
import msgpack
data = msgpack.packb(obj)
obj = msgpack.unpackb(data)
```

## 10. Networking

```python
import socket, urllib.request

# TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("example.com", 80))
sock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
response = sock.recv(4096)
sock.close()

# urllib (simple HTTP)
with urllib.request.urlopen("https://api.example.com") as resp:
    data = resp.read()
    headers = resp.headers

# IP address
import ipaddress
net = ipaddress.IPv4Network("192.168.1.0/24")
for ip in net.hosts():
    ...
```

## 11. Date and Time

```python
from datetime import datetime, date, time, timedelta, timezone

# Current time
now = datetime.now(timezone.utc)
today = date.today()

# Formatting
now.isoformat()  # 2024-01-15T10:30:00+00:00
now.strftime("%Y-%m-%d %H:%M:%S")

# Parsing
dt = datetime.fromisoformat("2024-01-15T10:30:00+00:00")
dt = datetime.strptime("2024-01-15", "%Y-%m-%d")

# Arithmetic
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)
next_week = today + timedelta(weeks=1)

# Timezone
from zoneinfo import ZoneInfo  # Python 3.9+
moscow = now.astimezone(ZoneInfo("Europe/Moscow"))
ny = now.astimezone(ZoneInfo("America/New_York"))

# Timestamps
ts = now.timestamp()
dt = datetime.fromtimestamp(ts, tz=timezone.utc)
```

## 12. Hashing and Encryption

```python
import hashlib, hmac, secrets

# Hashing
hashlib.md5(b"data").hexdigest()
hashlib.sha256(b"data").hexdigest()
hashlib.sha512(b"data").hexdigest()

# HMAC (signed hash)
h = hmac.new(b"key", b"message", hashlib.sha256)
signature = h.hexdigest()

# Secure random
token = secrets.token_hex(32)  # 64 character hex string
secret = secrets.token_urlsafe(32)  # URL-safe string
password = secrets.token_bytes(32)  # raw bytes

# Password hashing
import bcrypt
hashed = bcrypt.hashpw(b"password", bcrypt.gensalt())
bcrypt.checkpw(b"password", hashed)

# UUID
import uuid
uuid.uuid4()  # random UUID
uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")  # deterministic
```


---

## Part 5: Advanced Python Patterns

### 5.1 Descriptors (Controlling Attribute Access)

```python
from __future__ import annotations
from typing import Any, TypeVar

T = TypeVar("T")

class ValidatedAttribute:
    """Descriptor with validation.
    
    Использование: @dataclass не хватает — нужен контроль на уровне класса.
    """
    def __init__(self, validator: Callable[[Any], bool], error_msg: str = ""):
        self._validator = validator
        self._error_msg = error_msg
        self._name = ""
    
    def __set_name__(self, owner: type, name: str) -> None:
        self._name = name
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self._name)
    
    def __set__(self, obj: Any, value: Any) -> None:
        if not self._validator(value):
            raise ValueError(self._error_msg or f"Invalid value for {self._name}: {value}")
        obj.__dict__[self._name] = value

# Использование:
class Product:
    price = ValidatedAttribute(lambda p: p > 0, "Price must be positive")
    name = ValidatedAttribute(lambda n: len(n) >= 2, "Name too short")
    
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price
```

### 5.2 Metaclasses (Class Factories)

```python
"""Metaclass для автоматической регистрации подклассов."""
from __future__ import annotations
from typing import Any

class RegisteredMeta(type):
    """Automatically register all subclasses."""
    registry: dict[str, type] = {}
    
    def __new__(mcs, name: str, bases: tuple, namespace: dict[str, Any]) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "BasePlugin":
            mcs.registry[name.lower()] = cls
        return cls

class BasePlugin(metaclass=RegisteredMeta):
    """Base for all plugins. Subclasses auto-register."""
    def execute(self) -> str:
        raise NotImplementedError

class EmailPlugin(BasePlugin):
    def execute(self) -> str:
        return "Sending email..."

class SmsPlugin(BasePlugin):
    def execute(self) -> str:
        return "Sending SMS..."

# Auto-discovered:
assert "emailplugin" in RegisteredMeta.registry
assert "smsplugin" in RegisteredMeta.registry
```

### 5.3 Context Managers (Advanced)

```python
"""Context manager patterns for resource management."""
from __future__ import annotations
from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncIterator, Iterator


@contextmanager
def managed_file(path: str, mode: str = "r") -> Iterator[list[str]]:
    """Context manager with error handling and rollback."""
    file = None
    try:
        file = open(path, mode)
        yield file.readlines() if mode == "r" else file
    except Exception as e:
        # Rollback if needed
        print(f"Error: {e}")
        raise
    finally:
        if file:
            file.close()


@asynccontextmanager
async def db_transaction(pool) -> AsyncIterator[Any]:
    """Async context manager for DB transactions."""
    conn = await pool.acquire()
    try:
        await conn.execute("BEGIN")
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await pool.release(conn)


class TimerContext:
    """Context manager for timing code blocks."""
    def __enter__(self) -> "TimerContext":
        import time
        self.start = time.perf_counter()
        return self
    
    def __exit__(self, *args: Any) -> None:
        import time
        self.elapsed = time.perf_counter() - self.start
        print(f"⏱  Took {self.elapsed*1000:.1f}ms")

# Usage:
# with TimerContext():
#     expensive_operation()
```

### 5.4 Abstract Base Classes (Protocols)

```python
"""Structural subtyping with Protocols."""
from __future__ import annotations
from typing import Protocol, runtime_checkable


@runtime_checkable
class Drawable(Protocol):
    """Anything with a draw() method."""
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    """Works with anything that has draw()."""
    shape.draw()

# Both work without inheritance:
render(Circle())
render(Square())
assert isinstance(Circle(), Drawable)  # True (runtime_checkable)
```

### 5.5 Concurrency Patterns

```python
"""Thread-safe singleton with double-checked locking."""
from __future__ import annotations
import threading
from typing import Any, ClassVar


class ThreadSafeSingleton:
    _instance: ClassVar[ThreadSafeSingleton | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()
    
    def __new__(cls) -> "ThreadSafeSingleton":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 5.6 Generic Repository with TypeVar

```python
"""Generic repository pattern with full type safety."""
from __future__ import annotations
from typing import Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")
ID = TypeVar("ID")

@dataclass
class Entity(Generic[ID]):
    id: ID

class Repository(Generic[T, ID]):
    """Abstract generic repository."""
    
    async def get(self, id: ID) -> T | None:
        ...
    
    async def save(self, entity: T) -> T:
        ...
    
    async def delete(self, id: ID) -> bool:
        ...

class UserRepository(Repository["User", int]):
    """Type-safe: knows id is int, entity is User."""
    
    async def get(self, id: int) -> User | None:
        return await db.fetch_one("SELECT * FROM users WHERE id = ?", [id])
```

### 5.7 Advanced Enum Patterns

```python
"""Enums with behavior, not just constants."""
from __future__ import annotations
from enum import Enum, auto
from typing import Any


class OrderStatus(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()
    
    def can_transition_to(self, target: "OrderStatus") -> bool:
        transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],
            OrderStatus.CANCELLED: [],
        }
        return target in transitions.get(self, [])
    
    @property
    def is_active(self) -> bool:
        return self in (OrderStatus.CONFIRMED, OrderStatus.SHIPPED)
    
    @property
    def is_terminal(self) -> bool:
        return self in (OrderStatus.DELIVERED, OrderStatus.CANCELLED)


class HttpStatus(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    
    @property
    def is_error(self) -> bool:
        return self.value >= 400
    
    @property
    def is_success(self) -> bool:
        return 200 <= self.value < 300
    
    @classmethod
    def from_code(cls, code: int) -> "HttpStatus":
        for status in cls:
            if status.value == code:
                return status
        raise ValueError(f"Unknown status code: {code}")
```

### 5.8 TypedDict for Structured Data

```python
"""TypedDict — type-safe dicts with runtime checking."""
from __future__ import annotations
from typing import TypedDict, NotRequired, Unpack


class UserDict(TypedDict):
    id: int
    name: str
    email: str
    is_active: NotRequired[bool]  # Optional field


def create_user(**kwargs: Unpack[UserDict]) -> UserDict:
    """Type-checked at call site."""
    return {"id": kwargs["id"], "name": kwargs["name"], "email": kwargs["email"]}

# Static type check:
user = create_user(id=1, name="Alice", email="alice@example.com")
```

### 5.9 Match Statement Patterns (Python 3.10+)

```python
"""Advanced pattern matching patterns."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Success:
    value: Any

@dataclass
class Failure:
    error: str

@dataclass
class Loading:
    pass

type State = Success | Failure | Loading

def handle_state(state: State) -> str:
    match state:
        case Success(value=int(v)) if v < 0:
            return f"Negative: {v}"
        case Success(value=str(v)):
            return f"String: {v}"
        case Success():
            return f"Value: {state.value}"
        case Failure(error="not_found"):
            return "Not found!"
        case Failure(error=e):
            return f"Error: {e}"
        case Loading():
            return "Loading..."
        case _:
            return "Unknown state"


def parse_json(data: str) -> dict | None:
    """Match on JSON structure."""
    import json
    match json.loads(data):
        case {"type": "user", "id": int(id_), "name": str(name)}:
            return {"id": id_, "name": name}
        case {"type": "order", "items": [*_]}:  # Non-empty list
            return {"type": "order"}
        case _:
            return None
```

### 5.10 Positional-Only and Keyword-Only Parameters

```python
"""Modern parameter patterns (Python 3.8+)."""
from __future__ import annotations


def create_user(
    name: str,                  # Positional or keyword
    email: str,                 
    /,                          # Positional-ONLY separator
    age: int,                   
    *,                          # Keyword-ONLY separator
    is_admin: bool = False,
    department: str | None = None,
) -> dict:
    """Clear API design with explicit parameter modes.
    
    / before: must be positional (breaking change safe)
    * after: must be keyword (self-documenting at call site)
    """
    return {
        "name": name,
        "email": email,
        "age": age,
        "is_admin": is_admin,
        "department": department,
    }

# Usage:
create_user("Alice", "alice@example.com", 30, is_admin=True)
# create_user(name="Alice", ...) — ошибка: name positional-only
```

### 5.11 Performance Optimizations

```python
"""Micro-optimizations that matter in hot paths."""
from __future__ import annotations
import sys
from typing import Any


# 1. Local variable binding (avoid global lookups)
def slow(items: list[int]) -> int:
    return sum([x * 2 for x in items])  # List comprehension builds full list

def fast(items: list[int]) -> int:
    return sum(x * 2 for x in items)  # Generator — no intermediate list

# 2. __slots__ (reduces memory ~40%)
class SlotsPoint:
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# 3. String concatenation
def slow_str(items: list[str]) -> str:
    result = ""
    for item in items:
        result += item  # O(n²) — creates new string each time
    return result

def fast_str(items: list[str]) -> str:
    return "".join(items)  # O(n) — single allocation

# 4. Membership testing
# Set: O(1) average
# List: O(n)
# Tuple: O(n)
def filter_unique(items: list[int]) -> list[int]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:  # O(1) with set
            seen.add(item)
            result.append(item)
    return result

# 5. Map vs list comprehension (both fast, comprehension preferred)
def transform(items: list[int]) -> list[int]:
    return [x * 2 for x in items]  # Slightly faster than list(map(...))
```

### 5.12 Profiling and Optimization

```python
"""Profiling tools and techniques."""
from __future__ import annotations
import cProfile
import pstats
import io
import functools
from typing import Any, Callable


def profile(output_file: str = "profile.prof") -> Callable:
    """Decorator to profile a function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                profiler.dump_stats(output_file)
                s = io.StringIO()
                ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
                ps.print_stats(20)
                print(s.getvalue())
        return wrapper
    return decorator


class MemoryProfiler:
    """Simple memory usage tracking."""
    
    def __init__(self):
        self._snapshots: list[dict] = []
    
    def snapshot(self, label: str = "") -> None:
        import tracemalloc
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")
        total = sum(stat.size for stat in stats)
        self._snapshots.append({"label": label, "total": total, "time": time.time()})
    
    def report(self) -> str:
        lines = ["Memory Profile:"]
        for snap in self._snapshots:
            lines.append(f"  {snap['label']}: {snap['total'] / 1024:.1f} KB")
        if len(self._snapshots) > 1:
            delta = self._snapshots[-1]["total"] - self._snapshots[0]["total"]
            lines.append(f"  Delta: {delta / 1024:+.1f} KB")
        return "\n".join(lines)


# Usage:
# @profile("my_func.prof")
# def my_func():
#     ...
```

### 5.13 Python Version-Specific Features

```python
"""Features by Python version."""

# Python 3.8:
# - Walrus operator :=
if (n := len(items)) > 10:
    print(f"Large list: {n}")

# - Positional-only parameters /
def func(a, b, /, c, d, *, e, f): ...

# Python 3.9:
# - dict | (union operator)
d1 = {"a": 1}
d2 = {"b": 2}
d3 = d1 | d2  # {"a": 1, "b": 2}

# Python 3.10:
# - match statement
match value:
    case 1: ...
    case str(): ...

# - Type union operator |
x: int | str = 42

# Python 3.11:
# - Self type
from typing import Self

# - Variadic generics
from typing import TypeVarTuple

# Python 3.12:
# - Type parameter syntax (PEP 695)
def max[T](a: T, b: T) -> T: ...

# - override decorator
from typing import override

# Python 3.13:
# - JIT compiler (experimental)
# - Improved error messages
# - REPL improvements
```

## Part 6: Async/Await Deep Dive (Production)

### 6.1 Event Loop Internals

```python
"""Understanding the event loop."""
from __future__ import annotations
import asyncio
import time


# What happens during await:
async def example():
    # 1. Function executes until first await
    # 2. Suspends coroutine, yields control to event loop
    # 3. Event loop runs other tasks
    # 4. When result is ready, resumes coroutine
    await asyncio.sleep(1)

# Event loop does NOT:
# - Run CPU-bound code in parallel (GIL + single thread)
# - Automatically make I/O faster
# - Prevent blocking

# Event loop DOES:
# - Multiplex I/O operations
# - Schedule coroutines cooperatively
# - Handle many concurrent connections with few threads


# Measuring event loop health:
class LoopMonitor:
    """Monitor event loop delay (blocking detection)."""
    
    def __init__(self, threshold_ms: float = 100):
        self.threshold = threshold_ms / 1000
        self._task: asyncio.Task | None = None
    
    async def start(self) -> None:
        async def monitor():
            while True:
                start = time.monotonic()
                await asyncio.sleep(0.01)  # 10ms tick
                elapsed = time.monotonic() - start
                delay = max(0, elapsed - 0.01)
                
                if delay > self.threshold:
                    logger.warning(
                        f"⚠️ Event loop blocked for {delay*1000:.0f}ms! "
                        f"(threshold: {self.threshold*1000:.0f}ms)"
                    )
        self._task = asyncio.create_task(monitor())
    
    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
```

### 6.2 Task Group Patterns (Python 3.11+)

```python
"""TaskGroup — structured concurrency."""
from __future__ import annotations
import asyncio
from typing import Any


async def process_many(items: list[Any]) -> list[Any]:
    """Process items concurrently with structured error handling."""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_item(item)) for item in items]
    
    # All tasks done here (or exception raised for first failure)
    return [t.result() for t in tasks]


async def mixed_concurrency() -> None:
    """Multiple concurrent operations."""
    async with asyncio.TaskGroup() as tg:
        tg.create_task(fetch_users())
        tg.create_task(fetch_orders())
        tg.create_task(process_events())
    
    # If any task fails, all are cancelled
    # Clean separation of concerns


async def timeout_with_taskgroup(timeout: float = 5.0) -> None:
    """TaskGroup with overall timeout."""
    try:
        async with asyncio.timeout(timeout):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(work1())
                tg.create_task(work2())
    except asyncio.TimeoutError:
        print("All tasks cancelled due to timeout")
```

### 6.3 Async Queues for Backpressure

```python
"""Async queue patterns for flow control."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BackpressureWorker:
    """Worker with backpressure handling.
    
    Battle Scar: Без backpressure producer заваливал consumer'а 
    — память росла до OOM. С bounded queue — producer ждёт.
    """
    
    max_queue: int = 1000
    workers: int = 5
    queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=1000))
    
    async def produce(self, item: Any) -> None:
        """Produce item (blocks if queue full — backpressure)."""
        await self.queue.put(item)
    
    async def consume(self, handler: Callable[[Any], Awaitable[None]]) -> None:
        """Consume items with concurrency."""
        async def worker():
            while True:
                item = await self.queue.get()
                try:
                    await handler(item)
                except Exception as e:
                    logger.error(f"Handler failed: {e}")
                finally:
                    self.queue.task_done()
        
        workers = [asyncio.create_task(worker()) for _ in range(self.workers)]
        await asyncio.gather(*workers)
```

### 6.4 Async Context Propagation

```python
"""Propagate context through async calls."""
from __future__ import annotations
import asyncio
from contextvars import ContextVar


request_id: ContextVar[str] = ContextVar("request_id", default="")
user_id: ContextVar[str] = ContextVar("user_id", default="")
trace_id: ContextVar[str] = ContextVar("trace_id", default="")


def setup_context(req_id: str, u_id: str = "", t_id: str = "") -> None:
    """Setup context at request boundary."""
    request_id.set(req_id)
    if u_id:
        user_id.set(u_id)
    if t_id:
        trace_id.set(t_id)


async def business_logic() -> None:
    """Context automatically propagates through all awaits."""
    # Access context anywhere in the call chain:
    logger.info(
        "Processing request",
        extra={
            "request_id": request_id.get(),
            "user_id": user_id.get(),
            "trace_id": trace_id.get(),
        }
    )

# With contextlib:
from contextlib import asynccontextmanager
from typing import AsyncIterator


@asynccontextmanager
async def request_context(req_id: str, u_id: str = "") -> AsyncIterator[None]:
    """Ensure context is properly set up and cleaned up."""
    ctx_token_req = request_id.set(req_id)
    ctx_token_user = user_id.set(u_id) if u_id else None
    
    try:
        yield
    finally:
        request_id.reset(ctx_token_req)
        if ctx_token_user:
            user_id.reset(ctx_token_user)
```

### 6.5 Async Testing Patterns

```python
"""Testing async code properly."""
from __future__ import annotations
import asyncio
import pytest
from unittest.mock import AsyncMock, patch


# Async test with pytest
@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data()
    assert result is not None


# Mocking async functions
async def test_with_async_mock():
    with patch("myapp.service.fetch_data", new_callable=AsyncMock) as mock:
        mock.return_value = {"id": 1, "name": "Test"}
        result = await process_user(1)
        assert result.name == "Test"


# Test timeouts
@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await asyncio.sleep(10)
```

## Part 7: Production Python Optimization

### 7.1 GIL and Multiprocessing

```python
"""When and how to bypass the GIL."""
from __future__ import annotations
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any


# CPU-bound → ProcessPoolExecutor
def cpu_intensive(data: list[float]) -> float:
    return sum(x ** 2 for x in data)

def parallel_map_cpu(items: list[Any], worker: Callable) -> list[Any]:
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        return list(pool.map(worker, items))

# I/O-bound → asyncio or ThreadPoolExecutor
def parallel_map_io(items: list[Any], worker: Callable) -> list[Any]:
    with ThreadPoolExecutor(max_workers=20) as pool:
        return list(pool.map(worker, items))

# Mixed → custom strategy
def mixed_strategy():
    """CPU for computation, async for I/O."""
    # Use ProcessPoolExecutor for heavy computation
    # Use asyncio + aiohttp for network calls
    pass
```

### 7.2 C Extensions and Cython

```python
"""When Python is not fast enough."""
# Options (in order of complexity):
# 1. PyPy — drop-in replacement, ~4x faster for pure Python
# 2. Cython — static types, compile to C
# 3. Numba — JIT for numerical code
# 4. C extensions — manual C code
# 5. Rust (PyO3) — safe, fast, modern


# Numba example:
from numba import jit

@jit(nopython=True)
def monte_carlo_pi(n: int) -> float:
    """~100x faster than pure Python."""
    import random
    inside = 0
    for _ in range(n):
        x = random.random()
        y = random.random()
        if x*x + y*y <= 1:
            inside += 1
    return 4.0 * inside / n


# Cython (.pyx):
# def fib(int n):
#     cdef int a = 0, b = 1, i
#     for i in range(n):
#         a, b = b, a + b
#     return a
```

### 7.3 Async Performance Checklist

```text
□ Используешь asyncio для I/O-bound, не CPU-bound
□ Нет блокирующих вызовов в async функциях
□ Timeout на всех внешних вызовах
□ Connection pool настроен (NOT default pool_size=5)
□ Semaphore/circuit breaker на внешние сервисы
□ Rate limiter на клиентские запросы
□ Graceful shutdown с правильным порядком
□ Structured logging с correlation IDs
□ Event loop monitor (обнаружение block)
□ Profiling перед оптимизацией
```

### 7.4 Docker Optimization for Python

```dockerfile
# Multi-stage build for Python
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim
RUN adduser --disabled-password appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.5 Environment-Specific Configuration

```python
"""12-factor app configuration."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Settings:
    """Application settings from environment.
    
    All config via env vars (12-factor app).
    """
    # Core
    env: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "0") == "1")
    
    # Database
    db_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # Redis
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    
    # Kafka
    kafka_bootstrap: str = field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP", "localhost:9092"))
    kafka_group_id: str = field(default_factory=lambda: os.getenv("KAFKA_GROUP_ID", "my-service"))
    
    # API
    api_port: int = int(os.getenv("PORT", "8000"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    cors_origins: list[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    
    # Auth
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    jwt_algorithm: str = "HS256"
    
    # Feature flags
    enable_new_pipeline: bool = field(
        default_factory=lambda: os.getenv("FEATURE_NEW_PIPELINE", "0") == "1"
    )
    
    @property
    def is_production(self) -> bool:
        return self.env == "prod"
    
    def validate(self) -> None:
        """Validate critical settings at startup."""
        if self.is_production:
            assert self.db_url, "DATABASE_URL required in production"
            assert self.jwt_secret, "JWT_SECRET required in production"
            if "localhost" in self.db_url:
                raise ValueError("Database cannot be localhost in production")
```

## Part 8: Debugging & Troubleshooting

### 8.1 Common Production Issues

```python
"""Diagnosing common production issues."""

# 1. "Too many open files"
#   check: ulimit -n
#   fix:   Increase file descriptor limit
#          Close connections properly
#          Use context managers

# 2. "Connection refused" or "Connection reset"
#   check: Is the service running? (kubectl get pods)
#          Network policies? (kubectl describe networkpolicy)
#          Resource limits? (kubectl describe pod)

# 3. "Killed" (OOM)
#   check: dmesg | tail -20
#          Memory limits in k8s
#   fix:   Add memory limits
#          Profile memory usage
#          LRU cache with size limit

# 4. High CPU but low throughput
#   check: Profiling (py-spy, cProfile)
#          GIL contention
#          Busy loops
#   fix:   asyncio.sleep(0) in loops
#          ThreadPoolExecutor for CPU work
#          PyPy or Cython

# 5. Slow queries after migration
#   check: EXPLAIN ANALYZE
#          Missing indexes
#          N+1 queries
#   fix:   Add indexes
#          SELECT only needed columns
#          Use eager loading (joined/in subquery)

# 6. Memory leak
#   check: tracemalloc
#          objgraph (reference cycles)
#          Growth over time
#   fix:   WeakValueDictionary for caches
#          Clear caches periodically
#          __del__ for cleanup
```

### 8.2 Debugging Tools Checklist

```text
Performance:
  □ py-spy — sampling profiler (no code change)
  □ cProfile — deterministic profiler
  □ pyperformance — benchmarking suite
  □ memory_profiler — line-by-line memory
  □ tracemalloc — memory allocation tracking

Debugging:
  □ pdb / ipdb — interactive debugger
  □ breakpoint() — Python 3.7+ built-in
  □ icecream — better print debugging
  □ rich.inspect — detailed object inspection

Production:
  □ sentry-sdk — error tracking
  □ opentelemetry — distributed tracing
  □ prometheus_client — metrics
  □ structlog — structured logging
  □ healthcheck — service health
```

## Part 9: Python in Big Tech — What Actually Works

### Production Stats (from real services)

```text
Python in Big Tech:
  - Backend API services (FastAPI/Django)
  - Data pipelines (Airflow, Spark)
  - ML inference (MLflow, BentoML)
  - Infrastructure tools (AWS CDK, Kubernetes clients)
  - Developer tooling

Performance Reality:
  - Typical throughput: 5K-20K req/s per instance (FastAPI)
  - Typical latency: 20-100ms (API), 100ms-5s (data)
  - Memory: 128MB-2GB per instance
  - Python is NOT the bottleneck 90% of the time

When NOT to use Python:
  - High-frequency trading (< 1ms latency)
  - System programming (OS, drivers, embedded)
  - Mobile apps (frontend)
  - Extremely CPU-intensive (ML training — use C++/CUDA)

When Python WINS:
  - API development (fastest time-to-market)
  - Data processing (rich ecosystem)
  - ML/AI (PyTorch, TensorFlow)
  - Infrastructure automation
  - Prototyping and MVPs
```

## Part 10: Python 3.13+ Patterns

### Async Improvements (3.13+)

```python
"""Python 3.13+ async features."""

# JIT compiler (experimental — compile .pyc with JIT)
# No code changes needed — automatic speedup

# Improved task and exception handling
async def improved_async() -> None:
    """Better error messages and tracebacks."""
    async with asyncio.TaskGroup() as tg:
        tg.create_task(might_fail())
    # Exception group with clear traceback


# No-GIL mode (free-threaded Python)
# Experimental in 3.13 — truly parallel threads
# To enable: PYTHON_GIL=0 python app.py
```

### Type System Evolution

```python
"""Python 3.12-3.13 type features."""

# PEP 695: Type parameter syntax (3.12+)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

# Type alias with | (3.10+)
JSON = str | int | float | bool | None | dict[str, "JSON"] | list["JSON"]

# Override decorator (3.12+)
from typing import override

class Base:
    def method(self) -> str: ...

class Derived(Base):
    @override  # Type-checker ensures it overrides Base.method
    def method(self) -> str: ...

# ReadOnly (3.13+)
from typing import ReadOnly

class Config:
    name: ReadOnly[str]  # Cannot be set after init
```

### Pattern Matching Evolution

```python
"""Advanced match patterns (3.10+)"""

# Nested patterns
match data:
    case {"user": {"id": int(id_), "name": str(name)}, "action": "login"}:
        print(f"User {name} logged in")

# Guard conditions
match value:
    case int(x) if x < 0:
        print("Negative")
    case int(x) if x == 0:
        print("Zero")
    case int(x):
        print(f"Positive: {x}")

# Class patterns
match event:
    case ClickEvent(x=x, y=y) if 0 <= x <= 100 and 0 <= y <= 100:
        print("Clicked in bounding box")
    case KeyEvent(key="Enter"):
        print("Enter pressed")
    case _:
        print("Unknown event")
```

## Part 11: Python Package Structure

### Modern Python Project Layout

```text
my_project/
├── pyproject.toml          # Modern packaging (PEP 621)
├── src/                    # src-layout (prevents import confusion)
│   └── my_project/
│       ├── __init__.py
│       ├── __main__.py     # python -m my_project
│       ├── app/            # Application logic
│       ├── domain/         # Domain models
│       ├── infrastructure/ # External integrations
│       └── api/            # API endpoints
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── scripts/                # Dev/CI scripts
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── README.md
```

### pyproject.toml (Modern Standard)

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "my_project"
version = "0.1.0"
description = "Production Python service"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "alembic>=1.13.0",
    "pydantic>=2.5.0",
    "redis>=5.0.0",
    "aiokafka>=0.10.0",
    "opentelemetry-api>=1.22.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "A", "C4", "SIM"]

[tool.mypy]
strict = true
python_version = "3.11"
warn_unused_ignores = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: detect-private-key
```

---

*С любовью — команда @intarktelegram*


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
