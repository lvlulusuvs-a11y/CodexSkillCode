# API Security: Protect Your Endpoints

Security is not a feature you add later. It is built into every endpoint.

## Authentication

### JWT Tokens

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt


class JWTAuth:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def create_token(self, user_id: str, expires_delta: timedelta = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(hours=1)

        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),  # Unique token ID
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None


# FastAPI middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()
auth = JWTAuth(os.getenv("JWT_SECRET", "change-me"))

async def get_current_user(token: str = Depends(security)):
    payload = auth.verify_token(token.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]
```

### Token Best Practices

1. **Short expiry** - 15-60 minutes for access tokens
2. **Refresh tokens** - longer lived, stored securely
3. **Token rotation** - invalidate old tokens on password change
4. **JTI** - unique token ID for revocation
5. **No secrets in payload** - tokens are signed not encrypted

## Authorization (RBAC)

```python
from enum import Enum
from functools import wraps


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


PERMISSIONS = {
    Role.ADMIN: ["read", "write", "delete", "admin"],
    Role.USER: ["read", "write"],
    Role.VIEWER: ["read"],
}


def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if not user:
                raise HTTPException(401)

            user_role = user.get("role")
            allowed = PERMISSIONS.get(Role(user_role), [])

            if permission not in allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires {permission} permission"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


@app.get("/admin/users")
@require_permission("admin")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    return await user_service.get_all()
```

## Rate Limiting

```python
from collections import defaultdict
import time


class TokenBucket:
    def __init__(self, rate: float, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


# Per-endpoint limits
rate_limiters = {
    "/api/login": TokenBucket(rate=5, burst=10),      # 5 per second
    "/api/register": TokenBucket(rate=2, burst=5),    # 2 per second
    "/api/search": TokenBucket(rate=10, burst=20),    # 10 per second
}
```

## Common API Security Mistakes

1. **No rate limiting** - brute force will find weak passwords
2. **Token in URL** - logged, cached, leaked
3. **No input validation** - injection attacks
4. **Verbose errors** - "User not found" vs "Password wrong" leaks info
5. **No HTTPS** - everything is plaintext
6. **CORS too permissive** - Access-Control-Allow-Origin: *
7. **No request size limit** - OOM attacks
8. **Debug endpoints in production** - /debug, /admin without auth

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written
