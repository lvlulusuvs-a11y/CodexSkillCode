# ADR 010: Use Async SQLAlchemy 2.0

Status: Accepted

## Context

We use FastAPI (async) but our database layer was synchronous.
This blocks the event loop under load.

## Decision

Migrate to SQLAlchemy 2.0 with async support.

## Implementation

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Async query
async def get_user(user_id: str) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)

# Async create
async def create_user(data: CreateUser) -> User:
    async with async_session() as session:
        user = User(**data.model_dump())
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

## Migration Steps

1. Add asyncpg and SQLAlchemy 2.0
2. Create async engine alongside sync engine
3. Migrate one repository at a time
4. Run integration tests
5. Remove sync engine when done
6. Rollback plan: fall back to sync if async has issues


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.
