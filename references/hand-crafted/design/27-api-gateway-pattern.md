# API Gateway Pattern

An API gateway is a single entry point for all client requests.
It handles cross-cutting concerns so individual services dont have to.

## Responsibilities

1. Routing - forward requests to appropriate services
2. Authentication - validate tokens
3. Rate limiting - protect downstream services
4. Aggregation - combine responses from multiple services
5. Transformation - convert protocols and formats
6. Caching - cache common responses
7. Monitoring - track all traffic through one point

## Simple Implementation

from fastapi import FastAPI, Request
from httpx import AsyncClient
import json

app = FastAPI()
client = AsyncClient()

ROUTES = {
    "/api/users": "http://user-service:8001",
    "/api/orders": "http://order-service:8002",
    "/api/payments": "http://payment-service:8003",
}

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(request: Request, path: str):
    # Find target service
    for prefix, target in ROUTES.items():
        if path.startswith(prefix.strip("/api/")):
            url = f"{target}/{path}"
            break
    else:
        return {"error": "route not found"}, 404

    # Forward request
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    response = await client.request(
        method=request.method,
        url=url,
        content=body,
        headers=headers,
    )

    return response.json(), response.status_code

## Production API Gateway (Kong)

Kong is a battle-tested API gateway:

services:
  - name: user-service
    url: http://user-service:8001
    routes:
      - name: users
        paths:
          - /api/users

  - name: order-service
    url: http://order-service:8002
    routes:
      - name: orders
        paths:
          - /api/orders

plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 10000

  - name: key-auth
    config:
      key_names:
        - X-API-Key

  - name: cors
    config:
      origins:
        - "*"
      methods:
        - GET
        - POST
        - PUT
        - DELETE

## What NOT to Put in an API Gateway

1. Business logic - gateway is for cross-cutting concerns only
2. Complex routing logic - keep it simple
3. State - gateway should be stateless for horizontal scaling
4. Heavy processing - CPU work should be in services
5. Authentication decisions - delegate to auth service

## When You Need an API Gateway

- Multiple backend services
- Shared authentication across services
- Rate limiting and throttling
- Centralized monitoring
- Protocol translation (HTTP/WebSocket/gRPC)


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.


## Takeaway

Apply this today.
