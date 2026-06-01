# Data Structures & Algorithms: Production Reference

**Не для интервью — для реального кода. Когда что использовать и как не ошибиться.**

---

## 1. Production Data Structure Selection

```python
"""When to use what data structure."""
from __future__ import annotations

from typing import Any


DATA_STRUCTURE_GUIDE = {
    "array_list": {
        "use_case": "Ordered data, indexed access, iteration",
        "time_complexity": "O(1) get/set, O(n) insert/delete (except end)",
        "memory": "Contiguous, cache-friendly",
        "python": "list",
        "when_to_use": "95% of the time for collections",
        "when_to_avoid": "Frequent insert/delete at beginning",
    },
    "linked_list": {
        "use_case": "Frequent insert/delete, queue/deque",
        "time_complexity": "O(1) insert/delete (if ref held), O(n) access",
        "memory": "Non-contiguous, overhead per node",
        "python": "collections.deque (doubly-linked list)",
        "when_to_use": "Queue/FIFO operations, LRU cache",
        "when_to_avoid": "Random access patterns",
    },
    "hash_table": {
        "use_case": "Key-value lookup, unique items, counting",
        "time_complexity": "O(1) average get/set/delete",
        "memory": "Larger than array, hash overhead",
        "python": "dict, set, defaultdict, Counter",
        "when_to_use": "Lookup by key, deduplication, frequency counting",
        "when_to_avoid": "Ordered data (use OrderedDict or list)",
    },
    "binary_search_tree": {
        "use_case": "Sorted data, range queries",
        "time_complexity": "O(log n) average get/insert/delete",
        "python": "bisect module (on sorted list), sortedcontainers",
        "when_to_use": "Maintaining sorted data with dynamic inserts",
        "when_to_avoid": "When hashing suffices (hash is faster O(1))",
    },
    "heap": {
        "use_case": "Priority queue, top-K, scheduling",
        "time_complexity": "O(log n) push/pop, O(1) peek",
        "python": "heapq (min-heap), negate for max-heap",
        "when_to_use": "Priority queue, always want min/max",
        "when_to_avoid": "Need to search for arbitrary elements",
    },
    "trie": {
        "use_case": "Prefix search, autocomplete, spell check",
        "time_complexity": "O(m) search/insert (m = key length)",
        "python": "Custom implementation or pygtrie",
        "when_to_use": "String prefix matching, dictionary with prefixes",
        "when_to_avoid": "Simple string matching (use set or bloom filter)",
    },
    "bloom_filter": {
        "use_case": "Probabilistic membership test",
        "time_complexity": "O(k) for k hash functions",
        "memory": "Very memory efficient",
        "python": "pybloom_live, bloom_filter",
        "when_to_use": "Cache pre-check, spam detection, spell check",
        "when_to_avoid": "Need exact results (no false negatives allowed)",
    },
    "graph": {
        "use_case": "Relationships, paths, networks",
        "time_complexity": "Depends on algorithm",
        "python": "Adjacency list (dict of sets/list)",
        "when_to_use": "Social networks, routing, dependency resolution",
        "when_to_avoid": "Simple relationships (use DB joins)",
    },
}
```

## 2. Algorithm Selection Guide

```python
"""When to use which algorithm."""
from __future__ import annotations


# Sorting
SORTING_GUIDE = """
  JavaScript (.sort()): TimSort — hybrid stable sort, O(n log n) avg, O(n) best
  Python (.sort()): TimSort — hybrid stable sort
  Go (sort.Slice): pdqsort (pattern-defeating quicksort)
  Rust (.sort()): pdqsort
  
  When to NOT sort:
    - Need min/max → min() / max() O(n)
    - Need top-K → heap O(n log k)
    - Need unique → set O(n)
    - Need order statistics → quickselect O(n) avg
"""

# Search
SEARCH_GUIDE = """
  Unsorted data: Linear search O(n) — can't beat this
  Sorted data: Binary search O(log n) — bisect module in Python
  Special cases:
    - Lookup by key → hash table O(1)
    - Lookup by prefix → trie O(m) for m key length
    - Approximate match → bloom filter O(k)
"""

# Graph
GRAPH_ALGORITHMS = """
  BFS: Shortest path in unweighted graph, connectivity
    O(V + E)
  
  DFS: Topological sort, cycle detection, connected components
    O(V + E)
  
  Dijkstra: Shortest path in weighted graph (non-negative)
    O((V + E) log V) with heap
    Use: Navigation, routing
  
  A*: Dijkstra with heuristic (faster for single destination)
    Use: Games, map routing
  
  Bellman-Ford: Shortest path with negative weights
    O(VE)
  
  Floyd-Warshall: All pairs shortest path
    O(V³)
    Use: Small graphs, transitive closure
  
  Union-Find: Disjoint set, connected components
    O(α(n)) — inverse Ackermann (practically O(1))
    Use: Kruskal's MST, graph connectivity
"""

# String
STRING_ALGORITHMS = """
  Pattern matching:
    - Naive: O(n*m) — good for small text
    - KMP: O(n+m) — when naive is too slow
    - Boyer-Moore: O(n/m) best, O(n*m) worst — fast in practice
    - Rabin-Karp: O(n+m) avg — multiple pattern search
  
  Edit distance:
    - Levenshtein: O(n*m) — spell check, DNA alignment
    - Damerau-Levenshtein: adds transpositions
  
  Longest common subsequence: O(n*m) — diff tools
"""

# Optimizations
OPTIMIZATIONS = """
  Trading accuracy for speed:
    - Bloom filter instead of set (probabilistic)
    - HyperLogLog instead of exact count (approximate cardinality)
    - MinHash instead of exact Jaccard similarity
    - Reservoir sampling instead of exact random sample
  
  Precomputation:
    - Prefix sum for range sum queries O(1)
    - Segment tree for range queries + updates O(log n)
    - Fenwick tree (BIT) for prefix sums O(log n)
    - Sparse table for RMQ (static) O(1)
  
  Divide and conquer:
    - Merge sort: O(n log n), stable, external sort
    - Quick sort: O(n log n) avg, in-place, not stable
    - Binary search: O(log n), sorted data
"""
```

## 3. Time & Space Complexity Cheatsheet

```text
Data Structure    | Access | Search | Insert | Delete | Space
------------------|--------|--------|--------|--------|------
Array             | O(1)   | O(n)   | O(n)*  | O(n)*  | O(n)
Stack             | O(n)   | O(n)   | O(1)   | O(1)   | O(n)
Queue             | O(n)   | O(n)   | O(1)   | O(1)   | O(n)
Singly-Linked     | O(n)   | O(n)   | O(1)   | O(1)   | O(n)
Doubly-Linked     | O(n)   | O(n)   | O(1)   | O(1)   | O(n)
Hash Table        | N/A    | O(1)** | O(1)** | O(1)** | O(n)
BST               | O(log n) | O(log n) | O(log n) | O(log n) | O(n)
Red-Black Tree    | O(log n) | O(log n) | O(log n) | O(log n) | O(n)
AVL Tree          | O(log n) | O(log n) | O(log n) | O(log n) | O(n)
B-Tree            | O(log n) | O(log n) | O(log n) | O(log n) | O(n)
Heap              | O(n)   | O(n)   | O(log n) | O(log n) | O(n)
Trie              | O(m)   | O(m)   | O(m)   | O(m)   | O(m * n)
Bloom Filter      | N/A    | O(k)   | O(k)   | N/A    | O(m)

* At end: O(1). Anywhere else: O(n) shift.
** Average case. Worst: O(n).
m = key length, k = number of hash functions

Sorting Algorithms:
Algorithm        | Best    | Average | Worst   | Space  | Stable
-----------------|---------|---------|---------|--------|-------
Quick Sort       | O(n log n) | O(n log n) | O(n²) | O(log n) | No
Merge Sort       | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes
Heap Sort        | O(n log n) | O(n log n) | O(n log n) | O(1) | No
Insertion Sort   | O(n)    | O(n²)   | O(n²)   | O(1)   | Yes
Selection Sort   | O(n²)   | O(n²)   | O(n²)   | O(1)   | No
Bubble Sort      | O(n)    | O(n²)   | O(n²)   | O(1)   | Yes
TimSort (Python) | O(n)    | O(n log n) | O(n log n) | O(n) | Yes
Counting Sort    | O(n+k)  | O(n+k)  | O(n+k)  | O(k)   | Yes
Radix Sort       | O(nk)   | O(nk)   | O(nk)   | O(n+k) | Yes
```

## 4. Python-Specific Optimizations

```python
"""Python-specific algorithmic optimizations."""


# 1. Use built-in functions (C implementation)
min_value = min(data)           # O(n), C-level
max_value = max(data)           # O(n), C-level
total = sum(data)               # O(n), C-level
exists = any(x > 0 for x in data)  # Short-circuits
all_ok = all(x > 0 for x in data)  # Short-circuits
first = next(iter(data))        # O(1)


# 2. Use bisect for sorted operations
import bisect
index = bisect.bisect_left(sorted_list, value)  # O(log n)
bisect.insort(sorted_list, value)  # O(log n) insert


# 3. Use heapq for priority operations
import heapq
heapq.heapify(data)              # O(n) in-place
smallest_3 = heapq.nsmallest(3, data)  # O(n log 3)
largest_3 = heapq.nlargest(3, data)   # O(n log 3)
# nsmallest/nlargest faster than sort for small n


# 4. Use itertools for memory-efficient iteration
import itertools
# chain: combine iterators
# islice: slice iterators without list
# groupby: group consecutive elements
# zip_longest: zip with padding
# product/cartesian: nested loops
# permutations/combinations: combinatorial


# 5. Use collections for specialized data structures
from collections import Counter, defaultdict, deque, OrderedDict
Counter(data).most_common(10)    # O(n log k) for top K


# 6. Use functools for memoization
@functools.lru_cache(maxsize=None)  # Infinite cache for recursion
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)
# Without LRU: O(2^n). With LRU: O(n).


# 7. Use operator module for faster attribute access
import operator
get_names = operator.itemgetter('name')  # Faster than lambda
sorted_items.sort(key=operator.itemgetter(1))  # Sort by value
```

## 5. Common Algorithm Implementations

```python
"""Production-ready algorithm implementations."""


# Binary Search
def binary_search(arr: list[int], target: int) -> int:
    """Find target in sorted array. Returns index or -1."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
        if arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return -1


# Quickselect (find kth smallest)
import random
def quickselect(arr: list[int], k: int) -> int:
    """Find kth smallest element. O(n) average."""
    if len(arr) == 1: return arr[0]
    pivot = random.choice(arr)
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]
    
    if k < len(lows): return quickselect(lows, k)
    elif k < len(lows) + len(pivots): return pivots[0]
    else: return quickselect(highs, k - len(lows) - len(pivots))


# Union-Find (Disjoint Set)
class UnionFind:
    """Union-Find with path compression and union by rank."""
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # Path compression
            x = self.parent[x]
        return x
    
    def union(self, x: int, y: int) -> None:
        px, py = self.find(x), self.find(y)
        if px == py: return
        if self.rank[px] < self.rank[py]: self.parent[px] = py
        elif self.rank[px] > self.rank[py]: self.parent[py] = px
        else: self.parent[py] = px; self.rank[px] += 1


# Topological Sort
def topological_sort(graph: dict[int, list[int]]) -> list[int]:
    """Topological sort using Kahn's algorithm."""
    in_degree = {v: 0 for v in graph}
    for v in graph:
        for w in graph[v]:
            in_degree[w] += 1
    
    queue = [v for v, d in in_degree.items() if d == 0]
    result = []
    
    while queue:
        v = queue.pop(0)
        result.append(v)
        for w in graph[v]:
            in_degree[w] -= 1
            if in_degree[w] == 0:
                queue.append(w)
    
    return result if len(result) == len(graph) else []  # Return [] if cycle


# Dijkstra's Algorithm
import heapq
def dijkstra(graph: dict[int, list[tuple[int, int]]], start: int) -> dict[int, int]:
    """Shortest path from start to all nodes."""
    distances = {v: float('inf') for v in graph}
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances[node]: continue  # Stale entry
        for neighbor, weight in graph[node]:
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances


# Trie (Prefix Tree)
class TrieNode:
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word: str) -> bool:
        node = self.root
        for char in word:
            if char not in node.children: return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children: return False
            node = node.children[char]
        return True
    
    def autocomplete(self, prefix: str) -> list[str]:
        """Return words starting with prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children: return []
            node = node.children[char]
        
        result = []
        self._dfs(node, prefix, result)
        return result
    
    def _dfs(self, node: TrieNode, prefix: str, result: list[str]) -> None:
        if node.is_end:
            result.append(prefix)
        for char, child in node.children.items():
            self._dfs(child, prefix + char, result)


# Bloom Filter
import hashlib

class BloomFilter:
    """Space-efficient probabilistic set membership."""
    def __init__(self, size: int, num_hashes: int):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = 0  # Python int as bit array
    
    def add(self, item: str) -> None:
        for i in range(self.num_hashes):
            h = hashlib.md5(f"{item}{i}".encode()).hexdigest()
            idx = int(h[:8], 16) % self.size
            self.bit_array |= (1 << idx)
    
    def __contains__(self, item: str) -> bool:
        for i in range(self.num_hashes):
            h = hashlib.md5(f"{item}{i}".encode()).hexdigest()
            idx = int(h[:8], 16) % self.size
            if not (self.bit_array & (1 << idx)):
                return False
        return True  # May be false positive
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
