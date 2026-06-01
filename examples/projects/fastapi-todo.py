#!/usr/bin/env python3
"""Пример FastAPI ToDo приложения с полным циклом."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime

app = FastAPI(title="ToDo API", version="0.1.0")

# ── In-memory DB ───────────────────────────────────────────────────
class TodoDB:
    def __init__(self):
        self._items: dict[int, dict] = {}
        self._counter = 0

    def create(self, title: str, description: str = "") -> dict:
        self._counter += 1
        item = {
            "id": self._counter,
            "title": title,
            "description": description,
            "done": False,
            "created_at": datetime.now().isoformat(),
        }
        self._items[self._counter] = item
        return item

    def list(self, done: bool | None = None) -> list[dict]:
        items = list(self._items.values())
        if done is not None:
            items = [i for i in items if i["done"] == done]
        return sorted(items, key=lambda x: x["id"])

    def get(self, item_id: int) -> dict | None:
        return self._items.get(item_id)

    def update(self, item_id: int, data: dict) -> dict | None:
        if item_id not in self._items:
            return None
        self._items[item_id].update(data)
        return self._items[item_id]

    def delete(self, item_id: int) -> bool:
        return self._items.pop(item_id, None) is not None


db = TodoDB()


# ── Schemas ────────────────────────────────────────────────────────
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    done: bool = False


class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    done: bool
    created_at: str


# ── Endpoints ──────────────────────────────────────────────────────
@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(data: TodoCreate):
    return db.create(data.title, data.description)


@app.get("/todos", response_model=list[TodoResponse])
async def list_todos(done: bool | None = None):
    return db.list(done)


@app.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int):
    item = db.get(todo_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item


@app.patch("/todos/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: int, data: TodoUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    item = db.update(todo_id, update_data)
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    if not db.delete(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")


# ── Real-World Production Extensions ─────────────────────────────

"""Production-grade patterns for this example."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator with exponential backoff and jitter."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + (base_delay * 0.1 * hash(str(args)) % 1)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s: {e}")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Circuit breaker with half-open recovery."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _failures: int = 0
    _state: str = "closed"
    _last_failure: float = 0.0
    
    async def call(self, fn: Callable[..., Awaitable[Any]], fallback: Callable[..., Awaitable[Any]] | None = None, *args, **kwargs) -> Any:
        if self._state == "open":
            if time.monotonic() - self._last_failure >= self.recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit half-open, testing recovery")
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError("Circuit breaker is open")
        
        try:
            result = await fn(*args, **kwargs)
            self._failures = 0
            self._state = "closed"
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = "open"
                logger.error(f"Circuit opened after {self._failures} failures")
            raise


@dataclass
class GracefulShutdownManager:
    """Graceful shutdown with dependency ordering."""
    _hooks: list = None
    
    def __post_init__(self):
        self._hooks = []
        self._shutting_down = False
    
    def register(self, name: str, hook: Callable[[], Awaitable[None]], order: int = 10):
        self._hooks.append((order, name, hook))
    
    async def shutdown(self, sig: str = "SIGTERM"):
        self._shutting_down = True
        logger.info(f"Initiating graceful shutdown (signal: {sig})...")
        
        for order, name, hook in sorted(self._hooks, key=lambda x: -x[0]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                logger.info(f"  ✓ {name} stopped")
            except asyncio.TimeoutError:
                logger.warning(f"  ✗ {name} stop timed out")
            except Exception as e:
                logger.error(f"  ✗ {name} stop failed: {e}")
        
        logger.info("Graceful shutdown complete")
    
    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down
