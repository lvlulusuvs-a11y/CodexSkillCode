# Middleware Patterns

## FastAPI Middleware Chain

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time, uuid, logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Response-Time"] = f"{duration*1000:.0f}ms"
        logger.debug("Request took %.2fms", duration * 1000)
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return Response(
                status_code=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "3600",
                },
            )
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests: dict[str, list[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.monotonic()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if t > now - self.window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return Response(
                status_code=429,
                content="Too many requests",
            )
        
        self.requests[client_ip].append(now)
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

class CompressionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "gzip" in request.headers.get("Accept-Encoding", ""):
            import gzip
            if hasattr(response, "body") and len(response.body) > 1000:
                response.body = gzip.compress(response.body)
                response.headers["Content-Encoding"] = "gzip"
        return response

# App setup
app = FastAPI()

# Order matters: first = outermost
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CORSMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware)
```

## AIOGram Middleware

```python
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Callable, Awaitable

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[..., Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        logger.info("Event: %s from %s (%d)", event.__class__.__name__, user.full_name, user.id)
        return await handler(event, data)

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 3, per_seconds: int = 1):
        self.rate_limit = rate_limit
        self.per_seconds = per_seconds
        self.users: dict[int, list[float]] = {}
    
    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        now = time.monotonic()
        
        if user_id not in self.users:
            self.users[user_id] = []
        
        self.users[user_id] = [
            t for t in self.users[user_id]
            if t > now - self.per_seconds
        ]
        
        if len(self.users[user_id]) >= self.rate_limit:
            await event.answer("Слишком быстро! Подождите.")
            return
        
        self.users[user_id].append(now)
        return await handler(event, data)
```

## ASGI Middleware

```python
from fastapi import FastAPI
from starlette.types import ASGIApp, Scope, Receive, Send

class SimpleASGIMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start = time.perf_counter()
        
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                duration = time.perf_counter() - start
                message["headers"].append(
                    (b"X-Duration", f"{duration*1000:.0f}ms".encode())
                )
            await send(message)
        
        await self.app(scope, receive, wrapped_send)
```


## Production-Level Implementation

```python
"""Bonus: Production-ready pattern."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtendedImplementation:
    """Extended with error handling, logging, retry."""
    
    async def process(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(10):
                result = await self._execute()
                return result
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            raise
        except Exception:
            logger.exception("Processing failed")
            raise
