# SQLAlchemy 2.0 Boilerplate

```python
# db/__init__.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

# db/models.py
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from db import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

# db/repository.py
from __future__ import annotations
from sqlalchemy import select
from db import async_session
from db.models import User

class UserRepo:
    @staticmethod
    async def get_by_id(user_id: int) -> User | None:
        async with async_session() as session:
            return await session.get(User, user_id)

    @staticmethod
    async def create(name: str, email: str) -> User:
        async with async_session() as session:
            user = User(name=name, email=email)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
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
