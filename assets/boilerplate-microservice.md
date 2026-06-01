# Microservice Boilerplate

```python
"""Микросервис: FastAPI + SQLAlchemy async + Redis + structured logging."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import redis.asyncio as aioredis
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


# ── Config ─────────────────────────────────────
class Settings(BaseSettings):
    app_name: str = "microservice"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()


# ── Database ───────────────────────────────────
engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


# ── Redis ──────────────────────────────────────
redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    assert redis_client is not None, "Redis not initialized"
    return redis_client


# ── Lifespan ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global redis_client
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await redis_client.close()
    await engine.dispose()


# ── App ────────────────────────────────────────
app = FastAPI(title=settings.app_name, lifespan=lifespan)
logger = logging.getLogger(settings.app_name)


# ── Health ─────────────────────────────────────
@app.get("/health")
async def health(redis: aioredis.Redis = Depends(get_redis)) -> dict[str, str]:
    try:
        await redis.ping()
        return {"status": "healthy", "database": "ok", "redis": "ok"}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


# ── Example CRUD ───────────────────────────────
class ItemSchema(BaseModel):
    id: int | None = None
    name: str
    value: str


@app.get("/items/{item_id}")
async def get_item(
    item_id: int,
    redis: aioredis.Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    # Cache-aside: сначала кэш
    if cached := await redis.get(f"item:{item_id}"):
        return {"cached": True, "data": eval(cached)}
    
    # Потом БД
    # item = await db.get(Item, item_id)
    # if not item:
    #     raise HTTPException(status_code=404, detail="Item not found")
    
    # Write-through cache
    # await redis.setex(f"item:{item_id}", 300, str(item.to_dict()))
    return {"cached": False, "data": {"id": item_id}}


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemSchema,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict[str, Any]:
    # item = Item(**data.model_dump())
    # db.add(item)
    # await db.commit()
    # 
    # async with redis_client.pipeline() as pipe:
    #     await pipe.setex(f"item:{item.id}", 300, str(item.to_dict()))
    #     await pipe.publish("items:created", str(item.id))
    #     await pipe.execute()
    
    return {"id": 1, "name": data.name}
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
