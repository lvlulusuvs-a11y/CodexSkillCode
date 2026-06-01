# Distributed Systems Patterns

**Паттерны распределённых систем для Principal Engineer. Не теория — боевой опыт.**

---

## 1. Distributed Locking (Redis Redlock)

```python
"""Distributed lock with Redlock algorithm."""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DistributedLock:
    """Distributed lock using Redis.
    
    Battle Scar: Без distributed lock два экземпляра воркера
    обрабатывали одно сообщение — дубликаты заказов.
    """
    
    redis: Any
    lock_key: str
    ttl: int = 30  # seconds
    retry_delay: float = 0.1
    _token: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    
    async def acquire(self, blocking: bool = True, timeout: float = 10.0) -> bool:
        """Acquire distributed lock with optional blocking."""
        start = time.monotonic()
        while True:
            acquired = await self.redis.setnx(
                self.lock_key, self._token, expire=self.ttl
            )
            if acquired:
                return True
            
            if not blocking or time.monotonic() - start > timeout:
                return False
            
            await asyncio.sleep(self.retry_delay)
    
    async def release(self) -> None:
        """Release lock only if we own it (Lua script for atomicity)."""
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(lua, [self.lock_key], [self._token])
    
    async def __aenter__(self) -> "DistributedLock":
        await self.acquire()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.release()
```

## 2. Consistent Hashing

```python
"""Consistent hashing for distributed caching."""
from __future__ import annotations

import hashlib
from bisect import bisect
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConsistentHashRing:
    """Consistent hash ring with virtual nodes.
    
    Battle Scar: При добавлении ноды в Redis cluster без
    consistent hashing — 80% cache miss. С ним — 1/N miss.
    """
    
    nodes: list[str] = field(default_factory=list)
    virtual_nodes: int = 100
    _ring: dict[int, str] = field(default_factory=dict, init=False)
    _sorted_keys: list[int] = field(default_factory=list, init=False)
    
    def __post_init__(self) -> None:
        self._build_ring()
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    
    def _build_ring(self) -> None:
        self._ring.clear()
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                hash_key = self._hash(f"{node}:{i}")
                self._ring[hash_key] = node
        self._sorted_keys = sorted(self._ring.keys())
    
    def get_node(self, key: str) -> str:
        """Get node for key."""
        if not self._sorted_keys:
            raise ValueError("No nodes in ring")
        hash_key = self._hash(key)
        idx = bisect(self._sorted_keys, hash_key)
        if idx == len(self._sorted_keys):
            idx = 0
        return self._ring[self._sorted_keys[idx]]
    
    def add_node(self, node: str) -> None:
        self.nodes.append(node)
        self._build_ring()
    
    def remove_node(self, node: str) -> None:
        self.nodes.remove(node)
        self._build_ring()
```

## 3. Gossip Protocol (Membership)

```python
"""Gossip-based cluster membership."""
from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class NodeStatus(Enum):
    ALIVE = auto()
    SUSPECT = auto()
    DEAD = auto()


@dataclass
class ClusterMember:
    id: str
    host: str
    port: int
    status: NodeStatus = NodeStatus.ALIVE
    incarnation: int = 0
    last_seen: float = field(default_factory=time.monotonic)
    metadata: dict = field(default_factory=dict)


class GossipProtocol:
    """Gossip-based cluster membership.
    
    Used in: Cassandra, Consul, Serf
    """
    
    def __init__(self, node_id: str, seed_nodes: list[str]):
        self._local = node_id
        self._members: dict[str, ClusterMember] = {}
        self._seed_nodes = seed_nodes
        self._running = False
    
    async def start(self) -> None:
        """Start gossip protocol."""
        self._running = True
        # Contact seed nodes
        for seed in self._seed_nodes:
            await self._contact(seed)
        # Start periodic gossip
        asyncio.create_task(self._gossip_loop())
    
    async def _gossip_loop(self) -> None:
        """Periodically exchange membership info."""
        while self._running:
            await asyncio.sleep(1)  # Gossip interval
            # Pick random member to gossip with
            if len(self._members) > 1:
                target = random.choice(
                    [m for m in self._members if m != self._local]
                )
                await self._exchange(target)
    
    async def _exchange(self, target: str) -> None:
        """Exchange membership info with target node."""
        # Send our membership list, receive theirs
        # Update local state based on higher incarnation numbers
        pass
    
    def suspect(self, node_id: str) -> None:
        """Mark node as suspect."""
        if node_id in self._members:
            self._members[node_id].status = NodeStatus.SUSPECT
            self._members[node_id].incarnation += 1
    
    def alive(self, node_id: str) -> None:
        """Confirm node is alive."""
        if node_id in self._members:
            self._members[node_id].status = NodeStatus.ALIVE
            self._members[node_id].last_seen = time.monotonic()
    
    @property
    def live_nodes(self) -> list[str]:
        return [
            m.id for m in self._members.values()
            if m.status == NodeStatus.ALIVE
        ]
```

## 4. Bulkhead Pattern

```python
"""Bulkhead pattern for resource isolation.

Battle Scar: Один медленный клиент (латентность 30s) исчерпал 
все connections в пуле — все клиенты пострадали.
С bulkhead — изолированные пулы для разных клиентов.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Bulkhead:
    """Isolate resources by partition (e.g., client tier)."""
    
    max_concurrent: int = 10
    max_queue: int = 100
    _sem: asyncio.Semaphore = field(init=False)
    _queue: int = 0
    
    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.max_concurrent)
    
    async def execute(self, coro) -> Any:
        """Execute with bulkhead isolation."""
        if self._queue >= self.max_queue:
            raise BulkheadFullError("Queue full, rejecting request")
        
        self._queue += 1
        try:
            async with self._sem:
                return await coro
        finally:
            self._queue -= 1


class BulkheadRegistry:
    """Collection of bulkheads for different dependencies."""
    
    def __init__(self):
        self._bulkheads: dict[str, Bulkhead] = {}
    
    def register(self, name: str, max_concurrent: int = 10, max_queue: int = 100) -> None:
        self._bulkheads[name] = Bulkhead(max_concurrent, max_queue)
    
    async def execute(self, name: str, coro) -> Any:
        bh = self._bulkheads.get(name)
        if not bh:
            return await coro
        return await bh.execute(coro)


class BulkheadFullError(Exception):
    pass
```

## 5. Timeout and Deadline Propagation

```python
"""Timeout propagation across service boundaries.

Battle Scar: Service A calls B calls C (30s timeout each).
C hangs → A waits 90s before giving up. 
With deadline propagation: C gets (deadline - elapsed) timeout.
"""

from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class Deadline:
    """Propagate deadlines across service calls."""
    deadline: float  # Unix timestamp
    
    @classmethod
    def from_timeout(cls, timeout_s: float) -> "Deadline":
        return cls(deadline=time.monotonic() + timeout_s)
    
    @property
    def remaining(self) -> float:
        return max(0, self.deadline - time.monotonic())
    
    @property
    def expired(self) -> bool:
        return self.remaining <= 0
    
    def with_timeout(self, timeout_s: float) -> float:
        """Get effective timeout, capped by deadline."""
        return min(self.remaining, timeout_s)


# In HTTP headers:
# X-Deadline: 1710800000 (Unix timestamp)
# X-Request-Timeout: 5s

# Downstream service reads headers:
def get_effective_timeout(request) -> float:
    deadline = request.headers.get("X-Deadline")
    if deadline:
        remaining = float(deadline) - time.time()
        return max(0.1, remaining)
    return 30.0  # Default timeout
```

## 6. Two-Phase Commit (2PC) Simulation

```python
"""Two-phase commit for distributed transactions.

When you actually need 2PC (rare):
- Cross-database transactions
- Exactly-once semantics across systems

When you DON'T need 2PC (most cases):
- Saga pattern works better
- Eventual consistency is acceptable
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class Vote(Enum):
    YES = auto()
    NO = auto()


@dataclass
class TwoPhaseCommit:
    """Two-phase commit coordinator."""
    
    participants: list[str] = field(default_factory=list)
    
    async def execute(self, transaction_id: str) -> bool:
        # Phase 1: Prepare (CanCommit)
        votes = {}
        for participant in self.participants:
            vote = await self._prepare(participant, transaction_id)
            votes[participant] = vote
            if vote == Vote.NO:
                break
        
        # Phase 2: Commit or Abort
        if all(v == Vote.YES for v in votes.values()):
            for participant in self.participants:
                await self._commit(participant, transaction_id)
            return True
        else:
            for participant in votes:
                await self._abort(participant, transaction_id)
            return False
```

## 7. CAP Theorem Decision Matrix

```text
CAP Decision Matrix:

| Use Case                     | Choice | Database           |
|------------------------------|--------|--------------------|
| Financial transactions       | CP     | PostgreSQL         |
| Social media feed            | AP     | Cassandra          |
| User sessions                | CP     | Redis              |
| Analytics                    | AP     | ClickHouse         |
| Shopping cart                | CP     | PostgreSQL         |
| Real-time leaderboard        | CP     | Redis              |
| Content delivery             | AP     | CDN + S3           |
| Search                       | AP     | Elasticsearch      |
| Payment processing           | CP     | PostgreSQL         |
| Event log                    | AP     | Kafka              |

Trade-offs:
  CP: Consistency over Availability (partition → downtime)
  AP: Availability over Consistency (partition → stale reads)
  CA: Neither (partition = system failure)
```

## 8. Consensus Algorithms

```text
Raft vs Paxos vs Zab:

| Algorithm | Used By        | Simplicity | Understandability |
|-----------|----------------|------------|-------------------|
| Raft      | etcd, Consul   | Medium     | High (understandable) |
| Paxos     | Google Spanner | Low        | Low               |
| Zab       | ZooKeeper      | Medium     | Medium            |
| EPaxos    | Amazon         | Low        | Low               |

Raft is recommended for most systems:
  - Leader election
  - Log replication
  - Safety guarantees
  - Understandable (taught in universities)
```

## 9. Distributed Tracing

```python
"""OpenTelemetry-style distributed tracing."""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any
import time
import uuid


@dataclass
class Span:
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: str | None = None
    name: str = ""
    start_time: float = field(default_factory=time.monotonic)
    end_time: float = 0.0
    tags: dict[str, Any] = field(default_factory=dict)
    
    def finish(self) -> None:
        self.end_time = time.monotonic()
    
    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


_current_span: ContextVar[Span | None] = ContextVar("current_span", default=None)


class Tracer:
    """Simple distributed tracer."""
    
    def __init__(self, service_name: str):
        self._service = service_name
        self._spans: list[Span] = []
    
    def start_span(self, name: str, tags: dict | None = None) -> Span:
        parent = _current_span.get()
        span = Span(
            trace_id=parent.trace_id if parent else str(uuid.uuid4()),
            parent_id=parent.span_id if parent else None,
            name=name,
            tags=tags or {},
        )
        self._spans.append(span)
        _current_span.set(span)
        return span
    
    def end_span(self, span: Span, tags: dict | None = None) -> None:
        span.finish()
        if tags:
            span.tags.update(tags)
        _current_span.set(
            next((s for s in reversed(self._spans) if s.span_id != span.span_id), None)
        )
    
    def export(self) -> list[dict]:
        return [
            {
                "trace_id": s.trace_id,
                "name": s.name,
                "duration_ms": s.duration_ms,
                "tags": s.tags,
            }
            for s in self._spans
        ]
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
