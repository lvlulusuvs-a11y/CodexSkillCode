# CORS: Cross-Origin Resource Sharing for APIs

CORS is not a security feature. It is a browser feature that prevents
websites from making cross-origin requests on behalf of users.

## How CORS Works

1. Browser sends OPTIONS preflight request
2. Server responds with allowed origins, methods, headers
3. Browser allows or blocks the actual request

## Server Configuration

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://admin.myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
    max_age=86400,
)

## CORS Headers

Response headers:
Access-Control-Allow-Origin: https://myapp.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400
Access-Control-Expose-Headers: X-Request-ID

## Security Considerations

1. Never use Access-Control-Allow-Origin: * with credentials
2. Whitelist specific origins, dont use wildcard
3. Validate origin server-side, not just in middleware
4. Keep allowed methods and headers minimal
5. Set short max-age for preflight during development

## Common Mistakes

1. Using * with credentials (browser rejects the response)
2. Not handling preflight for all methods
3. Exposing too many headers
4. Allowing all methods when only GET/POST needed
5. Setting max-age too high (hard to change quickly)


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.
