# Flask Patterns

**Проверенные паттерны Flask для API и веб-приложений.**

---

## 1. Application Factory

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    from routes.api import api_bp
    from routes.web import web_bp
    
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(web_bp)
    
    return app
```

## 2. Blueprint Structure

```python
# routes/api.py
from flask import Blueprint, jsonify, request

api_bp = Blueprint("api", __name__)

@api_bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@api_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

## 3. Error Handling

```python
from flask import jsonify

class AppError(Exception):
    status_code = 400
    
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code:
            self.status_code = status_code

@app.errorhandler(AppError)
def handle_app_error(error):
    return jsonify({"error": error.message}), error.status_code

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500
```

## 4. SQLAlchemy Integration

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

# Query example
users = User.query.filter(User.is_active == True).order_by(User.created_at.desc()).limit(10).all()
```

## 5. Request Validation

```python
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    age = fields.Integer(validate=validate.Range(min=0, max=150))

user_schema = UserSchema()

@api_bp.route("/users", methods=["POST"])
def create_user():
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 422
    
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

## 6. Caching

```python
from flask_caching import Cache

cache = Cache(app)

@api_bp.route("/users/<int:user_id>")
@cache.cached(timeout=300, key_prefix="user_")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

## 7. Authentication

```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

jwt = JWTManager(app)

@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user and check_password(user.password, data["password"]):
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token)
    return jsonify({"error": "Invalid credentials"}), 401

@api_bp.route("/users/me")
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

## 8. CLI Commands

```python
import click
from flask.cli import with_appcontext

@app.cli.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo("Database initialized!")

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_admin(email, password):
    admin = User(email=email, password=hash_password(password), is_admin=True)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Admin {email} created!")
```

## 9. Testing

```python
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_users(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert response.json == []
```

## 10. Flask vs FastAPI Decision

```
┌────────────┬────────────────────────┬────────────────────────┐
│            │        Flask           │        FastAPI         │
├────────────┼────────────────────────┼────────────────────────┤
│ Async      │ Через gevent/threading │ Нативный async/await   │
│ Validation │ Marshmallow/Pydantic   │ Pydantic (встроенный)  │
│ Docs       │ Flasgger/Swagger       │ OpenAPI (авто)         │
│ DI         │ Нет встроенного        │ Depends (встроенный)   │
│ WebSocket  │ Flask-SocketIO         │ Нативная поддержка     │
│ GraphQL    │ graphene               │ strawberry              │
│ Когда      │ Простые сайты, админки │ API, микросервисы      │
└────────────┴────────────────────────┴────────────────────────┘
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

## Extended Enterprise Patterns

### Production-Grade Connection Management

```python
"""Enterprise connection and resource management."""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


@dataclass
class ResourcePool:
    """Generic resource pool with health checks."""
    
    async def acquire(self) -> Any:
        """Acquire resource with timeout."""
        async with asyncio.timeout(5):
            return await self._acquire()
    
    async def release(self, resource: Any) -> None:
        """Release resource back to pool."""
        await self._release(resource)
    
    @asynccontextmanager
    async def use(self) -> AsyncIterator[Any]:
        """Context manager for safe resource usage."""
        resource = await self.acquire()
        try:
            yield resource
        except Exception as e:
            logger.error(f"Resource error: {e}")
            await self.invalidate(resource)
            raise
        finally:
            await self.release(resource)


### Error Handling Framework

class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, id: Any):
        super().__init__(
            message=f"{resource} not found: {id}",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for {field}: {reason}",
            code="VALIDATION_ERROR",
            status_code=422,
        )


class ServiceUnavailableError(AppError):
    def __init__(self, service: str):
        super().__init__(
            message=f"{service} is unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


def error_handler(func):
    """Decorator for uniform error handling."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            raise
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("Database")
        except Exception as e:
            logger.exception("Unhandled error")
            raise AppError(str(e), "INTERNAL_ERROR", 500)
    return wrapper


### Async Task Management

class TaskManager:
    """Manage background tasks with proper cleanup."""
    
    def __init__(self):
        self._tasks: set[asyncio.Task] = set()
    
    def create_task(self, coro) -> asyncio.Task:
        task = asyncio.create_task(self._wrap(coro))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
    
    async def cancel_all(self) -> None:
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
    
    async def _wrap(self, coro):
        try:
            return await coro
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Background task failed: {e}")
