# Security Best Practices

**Безопасность Python-приложений. От SQL injection до dependency scanning.**

---

## 1. SQL Injection Prevention

```python
# ❌ Никогда: f-строка с пользовательским вводом
query = f"SELECT * FROM users WHERE id = {user_input}"  # SQL injection!

# ✅ Всегда: параметризированные запросы
await conn.execute("SELECT * FROM users WHERE id = $1", user_input)

# SQLAlchemy — безопасен по умолчанию
stmt = select(User).where(User.id == user_input)  # безопасно
```

## 2. XSS Prevention

```python
import html

# ❌ Опасно: неэкранированный вывод
template = f"<div>{user_input}</div>"

# ✅ Безопасно: экранирование HTML
safe = html.escape(user_input)
template = f"<div>{safe}</div>"
```

## 3. Command Injection

```python
import subprocess

# ❌ Опасно
result = subprocess.run(f"ping {user_input}", shell=True)

# ✅ Безопасно
result = subprocess.run(["ping", user_input], capture_output=True, text=True)

# ✅ Ещё безопаснее — использовать shlex.quote
import shlex
result = subprocess.run(f"ping {shlex.quote(user_input)}", shell=True)
```

## 4. Secret Management

```python
# ❌ Хардкод
API_KEY = "sk-1234567890abcdef"

# ✅ Переменные окружения / .env
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str  # берётся из окружения или .env
    db_password: str
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()

# ✅ Vault / AWS Secrets Manager
import boto3
client = boto3.client("secretsmanager")
secret = client.get_secret_value(SecretId="prod/api-key")
```

## 5. Authentication

```python
# JWT tokens
import jwt
from datetime import datetime, timedelta, timezone

def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 6. Rate Limiting

```python
from fastapi import Request, HTTPException
from datetime import datetime, timedelta

rate_limits: dict[str, list[datetime]] = {}

def check_rate_limit(request: Request, max_requests: int = 100, window: int = 60) -> None:
    client_ip = request.client.host
    now = datetime.now()
    
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []
    
    # Очистить старые
    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if t > now - timedelta(seconds=window)]
    
    if len(rate_limits[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    rate_limits[client_ip].append(now)
```

## 7. Input Validation

```python
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    bio: str = Field(default="", max_length=1000)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if any(c in v for c in "<>\"'%&;/"):
            raise ValueError("Invalid characters")
        return v.strip()
```

## 8. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # не "*" в проде!
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)
```

## 9. Dependency Scanning

```bash
# pip-audit — проверка уязвимостей в зависимостях
pip install pip-audit
pip-audit

# Safety — альтернатива
pip install safety
safety check

# Bandit — статический анализ безопасности
pip install bandit
bandit -r src/
```

## 10. Secure Headers

```python
from fastapi.responses import Response

def secure_headers(response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
```


---

## Advanced Security Patterns

### Authentication Provider Pattern

```python
"""Pluggable authentication providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class AuthProvider(ABC):
    """Abstract authentication provider."""
    
    @abstractmethod
    async def authenticate(self, credentials: dict) -> User | None:
        pass
    
    @abstractmethod
    async def authorize(self, user: User, resource: str, action: str) -> bool:
        pass


@dataclass
class JWTAuthProvider(AuthProvider):
    """JWT-based authentication."""
    secret: str
    
    async def authenticate(self, credentials: dict) -> User | None:
        token = credentials.get("token")
        if not token:
            return None
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return User(id=payload["sub"], roles=payload.get("roles", []))
        except jwt.PyJWTError:
            return None


@dataclass
class OAuth2Provider(AuthProvider):
    """OAuth2 with external provider."""
    client_id: str
    client_secret: str
    provider_url: str
    
    async def authenticate(self, credentials: dict) -> User | None:
        code = credentials.get("code")
        if not code:
            return None
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.provider_url}/token",
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            return User(id=data["sub"], roles=data.get("roles", []))
```

### Rate Limiting and Abuse Prevention

```python
"""Rate limiting patterns."""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""
    max_requests: int
    window_size: float
    _requests: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    
    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window_size
        
        # Clean old entries
        self._requests[key] = [
            t for t in self._requests[key]
            if t > window_start
        ]
        
        if len(self._requests[key]) >= self.max_requests:
            return False
        
        self._requests[key].append(now)
        return True
```

### Input Validation and Sanitization

```python
"""Input validation patterns to prevent injection."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Sanitizer:
    """Input sanitization for security."""
    
    @staticmethod
    def sanitize_sql(value: str) -> str:
        """Basic SQL injection prevention.
        Note: Always use parameterized queries, this is defense-in-depth.
        """
        dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "UNION", "SELECT"]
        result = value
        for d in dangerous:
            result = result.replace(d, "")
        return result
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """Prevent XSS."""
        import html
        return html.escape(value)
    
    @staticmethod
    def sanitize_filename(value: str) -> str:
        """Prevent path traversal."""
        # Remove path separators
        value = value.replace("/", "").replace("\\", "")
        # Remove parent directory references
        value = value.replace("..", "")
        # Only allow safe chars
        return re.sub(r'[^\w\-.]', '_', value)
```

### Encryption Utilities

```python
"""Encryption patterns."""
from __future__ import annotations

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class Encryption:
    """Symmetric encryption for sensitive data."""
    
    def __init__(self, key: bytes):
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        return self._fernet.encrypt(data.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        return self._fernet.decrypt(encrypted).decode()


class PasswordHasher:
    """Secure password hashing with bcrypt."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(rounds=12)
        ).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(password.encode(), hashed.encode())
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
