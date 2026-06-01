# Authentication Patterns: JWT, Sessions, OAuth

Choose the right authentication for your use case.

## Session-Based Auth

Traditional, but works well for server-rendered apps.

class SessionAuth:
    def __init__(self, redis):
        self.redis = redis

    async def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())
        await self.redis.set(
            f"session:{session_id}",
            json.dumps({"user_id": user_id, "created_at": time.time()}),
            ex=86400  # 24 hours
        )
        return session_id

    async def get_user_id(self, session_id: str) -> str | None:
        data = await self.redis.get(f"session:{session_id}")
        if data:
            return json.loads(data)["user_id"]
        return None

Pros: Easy to revoke. Simple to implement.
Cons: Server-side storage. Not ideal for mobile/SPA.

## JWT Token Auth

Stateless, widely used for APIs.

class JWTAuth:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def create_access_token(self, user_id: str) -> str:
        return jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "type": "access",
            },
            self.secret,
            algorithm=self.algorithm,
        )

    def create_refresh_token(self, user_id: str) -> str:
        return jwt.encode(
            {
                "sub": user_id,
                "exp": datetime.utcnow() + timedelta(days=30),
                "iat": datetime.utcnow(),
                "type": "refresh",
            },
            self.secret,
            algorithm=self.algorithm,
        )

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            return None

Pros: Stateless, works everywhere, no server-side storage.
Cons: Hard to revoke, tokens can be stolen, larger payload.

## OAuth 2.0

Authorization framework. Use with third-party auth providers.

Recommended flow for first-party apps:
1. User logs in via OAuth provider (Google, GitHub)
2. Provider returns authorization code
3. Server exchanges code for tokens
4. Server creates session/JWT for the user

Refresh token flow:
1. Access token expires (1 hour)
2. Client sends refresh token
3. Server validates and issues new access token
4. Old refresh token is rotated

## Password Hashing

Always use bcrypt or argon2:

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

## Which One to Choose

Server-side rendered app: Session auth (simpler, revokable)
SPA/Mobile app: JWT (stateless, works across domains)
Third-party access: OAuth 2.0 (standardized, secure)
Internal APIs: API keys (simple, auditable)


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.
