# Algorithms & Data Structures Reference

**Быстрый справочник алгоритмов для Python-разработчика.**

---

## 1. Sorting Algorithms

### Quick Sort
```python
def quicksort(arr):
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
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
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

### Heap Sort
```python
import heapq

def heapsort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

## 2. Search Algorithms

### Binary Search
```python
def binary_search(arr, target):
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

# Built-in
import bisect
idx = bisect.bisect_left(sorted_arr, target)
if idx < len(sorted_arr) and sorted_arr[idx] == target:
    print(f"Found at {idx}")
```

### Binary Search Tree
```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
            return
        curr = self.root
        while True:
            if val < curr.val:
                if curr.left:
                    curr = curr.left
                else:
                    curr.left = TreeNode(val)
                    break
            else:
                if curr.right:
                    curr = curr.right
                else:
                    curr.right = TreeNode(val)
                    break
    
    def search(self, val):
        curr = self.root
        while curr:
            if val == curr.val:
                return True
            elif val < curr.val:
                curr = curr.left
            else:
                curr = curr.right
        return False
    
    def inorder(self):
        result = []
        def dfs(node):
            if node:
                dfs(node.left)
                result.append(node.val)
                dfs(node.right)
        dfs(self.root)
        return result
```

## 3. Graph Algorithms

### BFS
```python
from collections import deque

def bfs(graph: dict[int, list[int]], start: int) -> list[int]:
    visited = set()
    queue = deque([start])
    result = []
    
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            result.append(node)
            queue.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
    
    return result
```

### DFS
```python
def dfs(graph: dict[int, list[int]], start: int) -> list[int]:
    visited = set()
    result = []
    
    def _dfs(node):
        if node in visited:
            return
        visited.add(node)
        result.append(node)
        for neighbor in graph[node]:
            _dfs(neighbor)
    
    _dfs(start)
    return result
```

### Dijkstra
```python
import heapq

def dijkstra(graph: dict[int, dict[int, int]], start: int) -> dict[int, float]:
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances[node]:
            continue
        for neighbor, weight in graph[node].items():
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances
```

### Floyd-Warshall (all pairs)
```python
def floyd_warshall(graph):
    n = len(graph)
    dist = [[float('inf')] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        for j, w in graph[i].items():
            dist[i][j] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist
```

## 4. Dynamic Programming

### Fibonacci
```python
# Memoization
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]

# Tabulation
def fib_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### Longest Common Subsequence
```python
def lcs(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

### 0/1 Knapsack
```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]
```

## 5. String Algorithms

### String Matching (KMP)
```python
def kmp_search(text: str, pattern: str) -> list[int]:
    """Find all occurrences of pattern in text."""
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        j = 0
        for i in range(1, len(pattern)):
            while j > 0 and pattern[i] != pattern[j]:
                j = lps[j-1]
            if pattern[i] == pattern[j]:
                j += 1
                lps[i] = j
        return lps
    
    lps = compute_lps(pattern)
    matches = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j-1]
        if text[i] == pattern[j]:
            j += 1
        if j == len(pattern):
            matches.append(i - j + 1)
            j = lps[j-1]
    return matches
```

### Palindrome Check
```python
def is_palindrome(s: str) -> bool:
    s = s.lower().replace(" ", "").translate(str.maketrans("", "", string.punctuation))
    return s == s[::-1]

def longest_palindrome(s: str) -> str:
    """Manacher's algorithm O(n)."""
    if not s:
        return ""
    processed = "#" + "#".join(s) + "#"
    n = len(processed)
    p = [0] * n
    center = right = 0
    for i in range(n):
        if i < right:
            p[i] = min(p[2*center - i], right - i)
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and processed[i-p[i]-1] == processed[i+p[i]+1]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]
    max_len = max(p)
    center_idx = p.index(max_len)
    start = (center_idx - max_len) // 2
    return s[start:start + max_len]
```

## 6. Tree Algorithms

### Tree Traversals
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(node):
    return inorder(node.left) + [node.val] + inorder(node.right) if node else []

def preorder(node):
    return [node.val] + preorder(node.left) + preorder(node.right) if node else []

def postorder(node):
    return postorder(node.left) + postorder(node.right) + [node.val] if node else []

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

# Max depth
def max_depth(root):
    return 1 + max(max_depth(root.left), max_depth(root.right)) if root else 0

# Validate BST
def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    if not (min_val < root.val < max_val):
        return False
    return is_valid_bst(root.left, min_val, root.val) and is_valid_bst(root.right, root.val, max_val)
```

## 7. System Design Algorithms

### Consistent Hashing
```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes: list[str], replicas: int = 3):
        self._replicas = replicas
        self._ring: dict[int, str] = {}
        self._sorted_keys: list[int] = []
        
        for node in nodes:
            self.add_node(node)
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node: str) -> None:
        for i in range(self._replicas):
            key = self._hash(f"{node}:{i}")
            self._ring[key] = node
            bisect.insort(self._sorted_keys, key)
    
    def remove_node(self, node: str) -> None:
        for i in range(self._replicas):
            key = self._hash(f"{node}:{i}")
            del self._ring[key]
            self._sorted_keys.remove(key)
    
    def get_node(self, key: str) -> str:
        if not self._ring:
            return ""
        hash_key = self._hash(key)
        idx = bisect.bisect(self._sorted_keys, hash_key)
        if idx == len(self._sorted_keys):
            idx = 0
        return self._ring[self._sorted_keys[idx]]
```

### Rate Limiter (Token Bucket)
```python
import time
import asyncio

class TokenBucket:
    def __init__(self, rate: float, burst: int):
        self._rate = rate
        self._burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
    
    async def acquire(self) -> bool:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last_refill = now
        
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False
```

## 8. Time Complexity Reference

```
Data Structures:
├── Array:         Access O(1), Search O(n), Insert O(n), Delete O(n)
├── Stack:         Push O(1), Pop O(1), Peek O(1)
├── Queue:         Enqueue O(1), Dequeue O(1), Peek O(1)
├── Linked List:   Access O(n), Search O(n), Insert O(1), Delete O(1)
├── Hash Table:    Access N/A, Search O(1), Insert O(1), Delete O(1)
├── BST:           Access O(log n), Search O(log n), Insert O(log n), Delete O(log n)
├── Heap:          Access O(1), Search O(n), Insert O(log n), Delete O(log n)
└── Trie:          Search O(k), Insert O(k) where k = key length

Sorting:
├── Quick Sort:    O(n log n) avg, O(n²) worst
├── Merge Sort:    O(n log n) all
├── Heap Sort:     O(n log n) all
├── Bubble Sort:   O(n²) all
└── Counting Sort: O(n + k) where k = range

Graph:
├── BFS/DFS:       O(V + E)
├── Dijkstra:      O((V+E) log V)
├── Floyd-Warshall: O(V³)
└── Kruskal/MST:   O(E log V)
```


---

## Enterprise Implementation Patterns

### Production-Grade Code

```python
"""Enterprise-grade implementation with full resilience."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools
import random

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class EnterpriseService:
    """Production service with all resilience patterns."""
    
    max_retries: int = 3
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    
    def __post_init__(self):
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time = 0.0
    
    async def call_with_resilience(
        self,
        fn: Callable[..., Awaitable[T]],
        fallback: Callable[..., Awaitable[T]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute with circuit breaker + retry + timeout."""
        if self._circuit_open:
            if time.monotonic() - self._last_failure_time < 30.0:
                if fallback:
                    return await fallback(*args, **kwargs)
                raise RuntimeError("Circuit breaker is open")
            self._circuit_open = False
            logger.info("Circuit breaker half-open, testing...")
        
        for attempt in range(self.max_retries + 1):
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    result = await fn(*args, **kwargs)
                    self._failure_count = 0
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout (attempt {attempt+1})")
                if attempt == self.max_retries:
                    self._record_failure()
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt) + random.uniform(0, 0.5))
            except Exception as e:
                logger.warning(f"Error (attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    self._record_failure()
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        
        raise RuntimeError("Unreachable")
    
    def _record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.circuit_breaker_threshold:
            self._circuit_open = True
            logger.error(f"Circuit breaker opened after {self._failure_count} failures")


### Configuration Management

@dataclass
class ServiceSettings:
    """Type-safe configuration from environment variables."""
    service_name: str = "my-service"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = ""
    db_pool_min: int = 5
    db_pool_max: int = 20
    db_timeout: int = 5
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_default_ttl: int = 300
    
    # API
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = None
    
    # External services
    external_api_timeout: int = 10
    external_api_retries: int = 3
    
    # Feature flags
    enable_new_feature: bool = False
    
    def validate(self) -> None:
        """Validate configuration on startup."""
        errors = []
        if self.environment == "production":
            if not self.database_url:
                errors.append("DATABASE_URL is required")
            if self.debug:
                errors.append("Debug mode must be disabled in production")
            if "localhost" in (self.database_url or ""):
                errors.append("Cannot use localhost in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @classmethod
    def from_env(cls) -> "ServiceSettings":
        """Load configuration from environment variables."""
        import os
        return cls(
            service_name=os.getenv("SERVICE_NAME", "my-service"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            debug=os.getenv("DEBUG", "0") == "1",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv("DATABASE_URL", ""),
            db_pool_min=int(os.getenv("DB_POOL_MIN", "5")),
            db_pool_max=int(os.getenv("DB_POOL_MAX", "20")),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            port=int(os.getenv("PORT", "8000")),
            external_api_timeout=int(os.getenv("EXTERNAL_API_TIMEOUT", "10")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        )


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
