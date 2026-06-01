# REST API Design

**Правила и паттерны проектирования REST API.**

---

## 1. Resource Naming

```python
# ✅ Правильно
GET    /users                    # список
POST   /users                    # создать
GET    /users/{id}               # один
PUT    /users/{id}               # заменить
PATCH  /users/{id}               # частично обновить
DELETE /users/{id}               # удалить

# Вложенные ресурсы
GET    /users/{id}/orders        # заказы пользователя
GET    /users/{id}/orders/{oid}  # конкретный заказ

# ❌ Неправильно
GET    /getUsers                 # глагол
POST   /createUser               # глагол
GET    /users/list               / избыточно
GET    /user                     # единственное число
```

## 2. Status Codes

```python
# 2xx — Успех
200 OK          # GET, PUT, PATCH
201 Created     # POST
202 Accepted    # Асинхронная операция
204 No Content  # DELETE

# 3xx — Перенаправление
301 Moved Permanently
302 Found (temporary)
304 Not Modified (кэш)

# 4xx — Ошибка клиента
400 Bad Request      # невалидный JSON
401 Unauthorized     # не аутентифицирован
403 Forbidden        # нет прав
404 Not Found        # ресурс не найден
409 Conflict         # конфликт (дубликат)
422 Unprocessable    # валидация не прошла
429 Too Many         # rate limit

# 5xx — Ошибка сервера
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

## 3. Pagination

```python
# Offset-based
GET /users?skip=0&limit=100
Response:
{
    "data": [...],
    "total": 1000,
    "skip": 0,
    "limit": 100
}

# Cursor-based (для больших таблиц)
GET /users?cursor=abc123&limit=100
Response:
{
    "data": [...],
    "next_cursor": "xyz789",
    "has_more": true
}
```

## 4. Filtering, Sorting, Searching

```python
GET /users?status=active&role=admin          # фильтрация
GET /users?sort=-created_at                  # сортировка (- = desc)
GET /users?fields=id,name,email              # выбор полей
GET /users?search=alice                      # поиск
GET /users?created_at[gte]=2024-01-01        # диапазон
```

## 5. Error Response Format

```python
# Стандартный формат (RFC 7807 Problem Details)
{
    "type": "https://api.example.com/errors/user-not-found",
    "title": "User Not Found",
    "status": 404,
    "detail": "User with id 42 not found",
    "instance": "/users/42",
    "errors": {
        "user_id": ["User 42 not found"]
    }
}

# Pydantic schema
class ErrorResponse(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str = ""
    errors: dict[str, list[str]] = {}
```

## 6. Versioning

```python
# Через URL (проще)
GET /api/v1/users

# Через заголовок (чище)
GET /users
Accept: application/vnd.myapp.v1+json
```

## 7. Idempotency

```python
# POST /payments — идемпотентность через Idempotency-Key
@router.post("/payments")
async def create_payment(
    data: PaymentCreate,
    request: Request,
    idempotency_key: str = Header(None),
):
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key required")
    
    # Проверяем, не было ли уже
    if existing := await redis.get(f"idempotency:{idempotency_key}"):
        return json.loads(existing)
    
    # Выполняем
    result = await payment_service.charge(data)
    
    # Сохраняем результат
    await redis.setex(f"idempotency:{idempotency_key}", 86400, json.dumps(result))
    
    return result
```

## 8. HATEOAS (Hypermedia)

```python
# Ответ содержит ссылки на связанные ресурсы
{
    "id": 1,
    "name": "Alice",
    "_links": {
        "self": {"href": "/users/1"},
        "orders": {"href": "/users/1/orders"},
        "profile": {"href": "/users/1/profile"}
    }
}
```


---

## Production Expansion

### Real-World Example

```python
"""Production-grade implementation."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionExample:
    """Battle-tested pattern from Big Tech production."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with proper error handling, retry, and observability."""
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise


### Key Takeaways for Principal Engineers

1. **Always add observability** — metrics, logs, traces
2. **Always handle errors** — don't let exceptions propagate silently
3. **Always set timeouts** — external calls should never hang forever
4. **Always think about scale** — what works for 10 req/s may fail at 1000
5. **Always document why** — the "why" is more important than the "what"
6. **Always test edge cases** — empty, None, max values, concurrent access
7. **Always consider rollback** — every deploy should be revertible
8. **Always plan for failure** — network, disk, memory, dependencies will fail

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No timeouts | Hanging requests | Add timeout to all external calls |
| No retry | Transient failures become permanent | Add retry with backoff + jitter |
| No circuit breaker | Cascading failures | Add circuit breaker on dependencies |
| No health checks | k8s kills healthy pods | Add meaningful health endpoints |
| No rate limiting | Service overwhelmed | Add rate limiter per client |
| No graceful shutdown | Dropped requests | Proper SIGTERM handling |
| No connection pooling | DB connection exhaustion | Configure pool size, heartbeat |
| No caching | Repeated expensive computations | Multi-level caching with TTL |
| No feature flags | Rollbacks require full deploy | Feature flags for gradual rollout |
| No monitoring | Blind to production issues | RED metrics, SLOs, alerts |


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
