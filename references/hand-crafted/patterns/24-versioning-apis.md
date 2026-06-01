# Versioning APIs: Evolve Without Breaking Clients

API versioning is about managing change without breaking consumers.

## When to Version

1. Removing a field
2. Changing a fields type
3. Adding required fields
4. Changing response format
5. Changing error format
6. Changing authentication method

## Versioning Strategies

### URL Versioning (Simple)

GET /v1/users
GET /v2/users

Pros: Simple, easy to test.
Cons: URIs change, SEO impact, no fine-grained control.

### Header Versioning (Clean)

GET /users
Accept: application/vnd.myapp.v2+json

Pros: URI stays the same, clean separation.
Cons: Harder to test, hidden in headers.

### Query Parameter Versioning

GET /users?version=2

Pros: Simple, easy to test.
Cons: Pollutes query string, caching issues.

## My Recommendation

Use URL versioning for major versions.
Use header versioning for minor or canary versions.

Major version: breaking changes (new endpoints, formats)
Minor version: backward-compatible additions

## Implementation

from fastapi import APIRouter

v1 = APIRouter(prefix="/v1")
v2 = APIRouter(prefix="/v2")

@v1.get("/users")
async def get_users_v1():
    return [{"id": 1, "name": "Alice"}]

@v2.get("/users")
async def get_users_v2():
    return [{"id": 1, "name": "Alice", "email": "alice@example.com"}]

app.include_router(v1)
app.include_router(v2)

## Deprecation Policy

1. Announce deprecation 6 months in advance
2. Add Deprecation header to responses
3. Keep old version running for 6-12 months
4. Provide migration guides
5. Monitor old version usage
6. Sunset old version when usage drops below threshold

Deprecation: "This endpoint is deprecated. Use /v2/users instead."

## Avoiding Versioning

1. Add fields instead of changing them
2. Use nullable defaults for new fields
3. Make fields optional, not required
4. Use HATEOAS for discoverability
5. Use GraphQL (clients control response shape)

Additive changes dont need new versions.
Breaking changes need new versions.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.
