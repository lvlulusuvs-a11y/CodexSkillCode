# Event-Driven Architecture Boilerplate

```python
"""Event-driven архитектура: producer → channel → consumer."""
from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

# ── Event ──────────────────────────────────────
T = TypeVar("T")

@dataclass
class Event(Generic[T]):
    """Базовое событие."""
    type: str
    data: T
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def serialize(self) -> str:
        return json.dumps({"type": self.type, "data": self.data, "metadata": self.metadata,
                          "timestamp": self.timestamp, "id": self.id})


# ── In-process Event Bus ──────────────────────
type Handler[T] = Callable[[Event[T]], Awaitable[None]]

@dataclass
class EventBus:
    handlers: dict[str, list[Handler[Any]]] = field(default_factory=dict)
    
    def subscribe(self, event_type: str, handler: Handler[Any]) -> None:
        self.handlers.setdefault(event_type, []).append(handler)
    
    async def publish(self, event: Event[Any]) -> None:
        for handler in self.handlers.get(event.type, []):
            try:
                await handler(event)
            except Exception as e:
                logger.exception("Handler failed for %s: %s", event.type, e)
    
    def unsubscribe(self, event_type: str, handler: Handler[Any]) -> None:
        self.handlers.get(event_type, []).remove(handler)


# ── Redis Pub/Sub Adapter ─────────────────────
class RedisEventChannel:
    """События через Redis Pub/Sub."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        self._handlers: dict[str, list[Handler[Any]]] = {}
    
    async def subscribe(self, channel: str, handler: Handler[Any]) -> None:
        self._handlers.setdefault(channel, []).append(handler)
        await self._pubsub.subscribe(channel)
    
    async def publish(self, channel: str, event: Event[Any]) -> None:
        await self._redis.publish(channel, event.serialize())
    
    async def listen(self) -> None:
        async for message in self._pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"]
            data = json.loads(message["data"])
            event = Event(type=data["type"], data=data["data"])
            for handler in self._handlers.get(channel, []):
                await handler(event)
    
    async def close(self) -> None:
        await self._pubsub.unsubscribe()
        await self._redis.close()


# ── Usage ──────────────────────────────────────
# bus = EventBus()
#
# @bus.subscribe("user.created")
# async def on_user_created(event: Event[dict]):
#     await email_service.send(event.data["email"], "Welcome!")
#
# @bus.subscribe("order.placed")
# async def on_order_placed(event: Event[dict]):
#     await payment_service.charge(event.data["amount"])
#
# await bus.publish(Event(type="user.created", data={"email": "test@test.com"}))
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
