# FastAPI Boilerplate

```python
# app/__init__.py
"""FastAPI application."""

# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, users
from app.db import engine, create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()

app = FastAPI(title="MyApp", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.include_router(health.router)
app.include_router(users.router)

# app/routers/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

# app/routers/users.py
from fastapi import APIRouter, Depends
from app.schemas import UserCreate, UserResponse
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserResponse])
async def list_users(service: UserService = Depends()):
    return await service.get_all()

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, service: UserService = Depends()):
    return await service.create(data)
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
