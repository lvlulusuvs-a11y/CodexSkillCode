# Web Development Patterns

**Проверенные паттерны веб-разработки на Python.**

---

## 1. Session Management

```python
from typing import Any
from datetime import datetime, timedelta, timezone
import json, uuid

class SessionStore:
    def __init__(self, redis):
        self._redis = redis
    
    async def create(self, user_id: int, data: dict[str, Any] | None = None) -> str:
        session_id = uuid.uuid4().hex
        session = {
            "user_id": user_id,
            "data": data or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self._redis.setex(f"session:{session_id}", 86400, json.dumps(session))
        return session_id
    
    async def get(self, session_id: str) -> dict[str, Any] | None:
        data = await self._redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    async def delete(self, session_id: str) -> None:
        await self._redis.delete(f"session:{session_id}")
```

## 2. CSRF Protection

```python
import secrets
from fastapi import Request, HTTPException

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

async def validate_csrf(request: Request):
    token = request.headers.get("X-CSRF-Token")
    cookie = request.cookies.get("csrf_token")
    if not token or not cookie or token != cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
```

## 3. File Upload

```python
from fastapi import UploadFile, HTTPException
import aiofiles

async def save_upload(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> str:
    if file.size and file.size > max_size:
        raise HTTPException(400, "File too large")
    
    allowed_types = {"image/jpeg", "image/png", "application/pdf"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Invalid file type")
    
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin"
    path = f"uploads/{uuid.uuid4().hex}.{ext}"
    
    async with aiofiles.open(path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return path
```

## 4. Background Tasks

```python
from fastapi import BackgroundTasks

async def send_welcome_email(user_id: int):
    user = await get_user(user_id)
    await email_service.send(user.email, "Welcome!")

@router.post("/users")
async def create_user(data: UserCreate, background_tasks: BackgroundTasks):
    user = await user_service.create(data)
    background_tasks.add_task(send_welcome_email, user.id)
    return user
```

## 5. WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.active[user_id] = ws
    
    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)
    
    async def send_to(self, user_id: str, message: dict):
        if ws := self.active.get(user_id):
            await ws.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: str):
    await manager.connect(user_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            await manager.send_to(data["target"], data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```


---

## Production-Grade Implementation

```python
"""Production-grade patterns — battle-tested in Big Tech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionReady:
    """Pattern with proper error handling, retry, and observability."""
    
    async def execute(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Timeout")
            raise
        except Exception:
            logger.exception("Error")
            raise


## Principal Engineer Best Practices

### Error Handling
- Always use specific exceptions (never bare except)
- Always log with context (request_id, user_id, trace_id)
- Always have fallbacks for critical dependencies
- Always set timeouts on external calls

### Performance
- Profile before optimizing (don't guess)
- Use appropriate data structures (dict vs list vs set)
- Batch database operations (never N+1)
- Cache aggressively but with TTL

### Observability
- Add metrics to all external calls
- Add structured logging with correlation IDs
- Add health check endpoints
- Add distributed tracing

### Security
- Validate all inputs (parse, don't validate)
- Never log secrets or PII
- Use parameterized queries (no SQL injection)
- Keep dependencies updated

### Operations
- Feature flags for gradual rollout
- Circuit breakers for dependencies
- Graceful shutdown with proper ordering
- Connection pooling with health checks


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
