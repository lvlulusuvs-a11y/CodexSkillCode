# ADR 003: Use FastAPI for REST API

Status: Accepted

## Context

We need a Python web framework for our REST API.
Requirements: async support, automatic OpenAPI docs, type safety,
high performance, active community.

## Decision

Use FastAPI for all REST API endpoints.

## Rationale

1. Async support - handles high concurrency efficiently
2. Automatic OpenAPI docs - Swagger UI out of the box
3. Pydantic integration - request/response validation
4. Type safety - full type hints support
5. Performance - on par with Go and Node.js
6. Dependency injection - clean separation of concerns
7. Active community - fast bug fixes, extensive plugins
8. Starlette foundation - compatible with ASGI ecosystem

## Compare to Alternatives

Django REST Framework: Better admin panel, batteries included.
But slower, synchronous only, less flexible for async use cases.

Flask: Simpler, more lightweight.
But no async, manual validation, manual docs.

## Project Structure

src/
  api/
    v1/
      endpoints/
      schemas/
      dependencies/
  core/
    config.py
    database.py
    security.py
  services/
  repositories/
  models/

## Dependencies

fastapi>=0.110
uvicorn[standard]>=0.29
pydantic>=2.7
sqlalchemy[asyncio]>=2.0
httpx>=0.27


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.
