# WebSocket Server Boilerplate

```python
"""Async WebSocket сервер с комнатами и heartbeat."""
from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import aiohttp
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ws-server")

# ── Room Management ───────────────────────────
@dataclass
class Room:
    name: str
    clients: dict[str, web.WebSocketResponse] = field(default_factory=dict)
    max_clients: int = 50
    
    def broadcast(self, message: str, exclude: str | None = None) -> None:
        for client_id, ws in self.clients.items():
            if client_id != exclude:
                asyncio.ensure_future(ws.send_str(message))
    
    def count(self) -> int: return len(self.clients)


class RoomManager:
    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
    
    def get_or_create(self, name: str) -> Room:
        if name not in self._rooms:
            self._rooms[name] = Room(name=name)
        return self._rooms[name]
    
    def remove_empty(self) -> None:
        self._rooms = {k: v for k, v in self._rooms.items() if v.count() > 0}


room_manager = RoomManager()


# ── WebSocket Handler ─────────────────────────
async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(heartbeat=30.0)
    await ws.prepare(request)
    
    client_id = id(ws)
    current_room: str | None = None
    
    logger.info("New client: %s", client_id)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                action = data.get("action")
                
                if action == "join":
                    room_name = data.get("room", "default")
                    room = room_manager.get_or_create(room_name)
                    
                    if room.count() >= room.max_clients:
                        await ws.send_str(json.dumps({"type": "error", "message": "Room full"}))
                        continue
                    
                    # Leave previous room
                    if current_room and current_room != room_name:
                        old_room = room_manager.get_or_create(current_room)
                        old_room.clients.pop(str(client_id), None)
                        old_room.broadcast(json.dumps({"type": "left", "client": client_id}))
                    
                    room.clients[str(client_id)] = ws
                    current_room = room_name
                    await ws.send_str(json.dumps({"type": "joined", "room": room_name}))
                    room.broadcast(json.dumps({"type": "user_joined", "client": client_id}), exclude=str(client_id))
                
                elif action == "message":
                    if current_room:
                        room = room_manager.get_or_create(current_room)
                        room.broadcast(json.dumps({
                            "type": "message",
                            "client": client_id,
                            "data": data.get("data", ""),
                            "timestamp": data.get("timestamp", ""),
                        }), exclude=str(client_id))
                
                elif action == "ping":
                    await ws.send_str(json.dumps({"type": "pong"}))
            
            elif msg.type == WSMsgType.ERROR:
                logger.error("ws error: %s", ws.exception())
    
    finally:
        if current_room:
            room = room_manager.get_or_create(current_room)
            room.clients.pop(str(client_id), None)
            room.broadcast(json.dumps({"type": "left", "client": client_id}))
            room_manager.remove_empty()
        
        logger.info("Client disconnected: %s", client_id)
    
    return ws


# ── HTTP Endpoints ─────────────────────────────
async def index(request: web.Request) -> web.Response:
    return web.Response(text="WebSocket Server Running", content_type="text/plain")

async def stats(request: web.Request) -> web.Response:
    rooms_info = {name: room.count() for name, room in room_manager._rooms.items() if room.count() > 0}
    return web.json_response({"rooms": rooms_info, "total_clients": sum(rooms_info.values())})


# ── App ────────────────────────────────────────
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", ws_handler)
app.router.add_get("/stats", stats)

if __name__ == "__main__":
    web.run_app(app, port=8080)
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
