# GraphQL API Patterns

**GraphQL в Big Tech: когда использовать, как не облажаться, production-паттерны.**

---

## 1. GraphQL vs REST: Decision Framework

```python
"""When to choose GraphQL over REST."""
from __future__ import annotations

DECISION_MATRIX = """
  Choose GraphQL when:
    ✅ Multiple clients need different data shapes
    ✅ Frontend controls data requirements
    ✅ Rapid iteration of client requirements
    ✅ Dashboard/complex UIs with many data sources
  
  Choose REST when:
    ✅ Simple CRUD APIs
    ✅ Public APIs with many consumers
    ✅ Strong caching requirements
    ✅ File uploads / binary data
    ✅ You need REST's maturity (HATEOAS, status codes)
  
  Compromise (GraphQL + REST):
    - GraphQL for BFF (Backend For Frontend)
    - REST for internal microservices
    - Both exposed with proper documentation
"""


@dataclass
class GraphQLResult:
    """Production GraphQL response."""

    def __init__(self):
        self.data = None
        self.errors = []
        self.extensions = {}
    
    def to_dict(self) -> dict:
        result = {}
        if self.data is not None:
            result["data"] = self.data
        if self.errors:
            result["errors"] = self.errors
        if self.extensions:
            result["extensions"] = self.extensions
        return result
```

## 2. Production GraphQL Patterns

### DataLoader (N+1 Prevention)

```python
"""DataLoader for batch loading (N+1 prevention).

Battle Scar: GraphQL без DataLoader — каждый вложенный запрос
создавал N запросов к БД. Запрос списка заказов с товарами:
1 (orders) + N (products). С DataLoader: 1 + 1.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")


class DataLoader(Generic[K, T]):
    """Batch loading with dedup and caching."""
    
    def __init__(self, batch_fn):
        self._batch_fn = batch_fn
        self._cache: dict[K, T] = {}
        self._queue: list[K] = []
    
    async def load(self, key: K) -> T:
        if key in self._cache:
            return self._cache[key]
        self._queue.append(key)
        
        if len(self._queue) >= 100:
            await self._flush()
        
        # Return promise
        future = asyncio.get_event_loop().create_future()
        self._pending[key] = future
        return await future
    
    async def _flush(self) -> None:
        if not self._queue:
            return
        keys = self._queue
        self._queue = []
        
        results = await self._batch_fn(keys)
        for key, value in zip(keys, results):
            self._cache[key] = value
            if key in self._pending:
                self._pending[key].set_result(value)
                del self._pending[key]


# Usage:
# loader = DataLoader(lambda ids: db.fetch("SELECT * FROM users WHERE id = ANY($1)", ids))
# user = await loader.load(42)
```

### GraphQL Error Handling

```python
"""Structured error handling in GraphQL."""
from __future__ import annotations


ERROR_CODES = {
    "UNAUTHENTICATED": "Authentication required",
    "FORBIDDEN": "Insufficient permissions",
    "NOT_FOUND": "Resource not found",
    "VALIDATION_ERROR": "Input validation failed",
    "RATE_LIMITED": "Too many requests",
    "INTERNAL_ERROR": "Internal server error",
    "BAD_USER_INPUT": "Invalid input provided",
}


def format_graphql_error(error: Exception, code: str = "INTERNAL_ERROR") -> dict:
    """Format error according to GraphQL spec."""
    return {
        "message": str(error),
        "extensions": {
            "code": code,
            "timestamp": time.time(),
            "request_id": get_request_id(),
        },
    }


### Resolver Patterns

```python
"""Production resolver patterns."""
from __future__ import annotations


async def resolve_user(parent, info, user_id: str) -> dict:
    """Simple resolver with error handling."""
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise GraphQLError("User not found", code="NOT_FOUND")
        return user_to_dict(user)
    except GraphQLError:
        raise
    except Exception as e:
        logger.exception(f"Error resolving user {user_id}")
        raise GraphQLError("Internal error", code="INTERNAL_ERROR")


def resolver_with_dataloader(loader_name: str, key_field: str = "id"):
    """Decorator for DataLoader integration."""
    def decorator(resolver):
        @functools.wraps(resolver)
        async def wrapper(parent, info, *args, **kwargs):
            loader = get_data_loader(info.context, loader_name)
            key = getattr(parent, key_field) if parent else kwargs.get(key_field)
            if loader and key:
                return await loader.load(key)
            return await resolver(parent, info, *args, **kwargs)
        return wrapper
    return decorator
```

## 3. Federation & Schema Composition

```python
"""Apollo Federation patterns for distributed GraphQL."""
from __future__ import annotations


# Service A (User Service)
USER_TYPES = """
  type User @key(fields: "id") {
    id: ID!
    name: String!
    email: String!
    orders: [Order]  # External type
  }
  
  extend type Query {
    user(id: ID!): User
    users: [User]
  }
"""

# Service B (Order Service)
ORDER_TYPES = """
  type Order @key(fields: "id") {
    id: ID!
    total: Float!
    userId: ID!
    user: User @requires(fields: "userId")  # Reference to User Service
  }
  
  extend type User @key(fields: "id") {
    id: ID! @external
    orders: [Order]  # Resolved by Order Service
  }
  
  extend type Query {
    order(id: ID!): Order
  }
"""


@dataclass
class FederationResolver:
    """Resolver for federated GraphQL types."""
    
    async def resolve_reference(self, reference: dict) -> dict:
        """Resolve entity reference from other service."""
        if reference.get("__typename") == "User":
            user = await self.get_user(reference["id"])
            return user_to_dict(user)
        return reference
```

## 4. Performance & Cost Management

```python
"""GraphQL performance patterns."""
from __future__ import annotations


# Query complexity analysis
QUERY_COMPLEXITY = """
  Each field has a complexity cost:
    - Simple field (scalar): 1 point
    - Object field: 1 + children complexity
    - List field: 1 + 10 * children complexity
    - Nested list: 1 + 100 * children complexity
  
  Max query complexity: 1000 points
  Max query depth: 7 levels
  
  Reject queries that exceed limits:
    - Complexity > 1000
    - Depth > 7
    - Aliases > 50
"""


@dataclass
class QueryValidator:
    """Validate GraphQL queries before execution."""
    
    MAX_COMPLEXITY = 1000
    MAX_DEPTH = 7
    MAX_ALIASES = 50
    
    def validate(self, query: str) -> tuple[bool, str]:
        """Validate query against limits."""
        complexity = self._calculate_complexity(query)
        depth = self._calculate_depth(query)
        aliases = query.count("alias")
        
        if complexity > self.MAX_COMPLEXITY:
            return False, f"Query too complex: {complexity} > {self.MAX_COMPLEXITY}"
        if depth > self.MAX_DEPTH:
            return False, f"Query too deep: {depth} > {self.MAX_DEPTH}"
        if aliases > self.MAX_ALIASES:
            return False, f"Too many aliases: {aliases}"
        
        return True, "OK"
```

## 5. Subscription Patterns

```python
"""GraphQL subscriptions for real-time data."""
from __future__ import annotations


async def order_subscription(generator):
    """Subscribe to order updates with backpressure."""
    try:
        async for order in generator:
            yield {
                "orderUpdated": {
                    "id": order.id,
                    "status": order.status,
                    "timestamp": time.time(),
                }
            }
    except asyncio.CancelledError:
        logger.info("Subscription cancelled")
        raise
    finally:
        logger.info("Subscription cleanup")
```


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
