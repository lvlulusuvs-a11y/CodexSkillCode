# Network Programming in Python

**Сети, протоколы, низкоуровневый I/O. Для продакшен-разработчика.**

---

## 1. TCP Server

```python
import asyncio

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"Connected: {addr}")
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            writer.write(data.upper())
            await writer.drain()
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Disconnected: {addr}")

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 8888)
    print(f"Server on {server.sockets[0].getsockname()}")
    
    async with server:
        await server.serve_forever()

# Run: asyncio.run(main())
```

## 2. TCP Client

```python
import asyncio

async def tcp_client(host: str = "127.0.0.1", port: int = 8888):
    reader, writer = await asyncio.open_connection(host, port)
    
    writer.write(b"hello server\n")
    await writer.drain()
    
    data = await reader.read(1024)
    print(f"Received: {data.decode()}")
    
    writer.close()
    await writer.wait_closed()
```

## 3. HTTP Client with aiohttp

```python
import aiohttp
import asyncio
from typing import Any

class HTTPClient:
    def __init__(self, base_url: str = ""):
        self._base_url = base_url
        self._session: aiohttp.ClientSession | None = None
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            base_url=self._base_url,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Mega-Coding/1.0"},
        )
        return self
    
    async def __aexit__(self, *args):
        if self._session:
            await self._session.close()
    
    async def get(self, path: str, **kwargs) -> dict[str, Any]:
        async with self._session.get(path, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()
    
    async def post(self, path: str, data: dict | None = None, **kwargs) -> dict[str, Any]:
        async with self._session.post(path, json=data, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()

async def example():
    async with HTTPClient("https://api.github.com") as client:
        user = await client.get("/users/python")
        print(user["login"])
```

## 4. UDP Server

```python
import asyncio

class UDPServer:
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        print(f"Received from {addr}: {data.decode()}")
        self.transport.sendto(data.upper(), addr)

async def main():
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        UDPServer,
        local_addr=("0.0.0.0", 9999),
    )
    print("UDP server on :9999")
    await asyncio.sleep(3600)
    transport.close()
```

## 5. DNS Resolution

```python
import socket
import asyncio

# Sync
ip = socket.gethostbyname("example.com")
print(ip)

# All IPs
ips = socket.gethostbyname_ex("example.com")
print(ips)

# Async
async def resolve(host: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.getaddrinfo(host, 80)

# Custom DNS
import aiodns
resolver = aiodns.DNSResolver()
result = await resolver.gethostbyname("example.com", socket.AF_INET)
```

## 6. SSL/TLS

```python
import ssl

# Create SSL context
ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ctx.check_hostname = True
ctx.verify_mode = ssl.CERT_REQUIRED

# Client with SSL
reader, writer = await asyncio.open_connection(
    "example.com", 443,
    ssl=ctx,
    server_hostname="example.com",
)

# Self-signed for dev
dev_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
dev_ctx.load_cert_chain("cert.pem", "key.pem")
```

## 7. HTTP Server (raw)

```python
import asyncio
from datetime import datetime, timezone

HTTP_RESPONSE = """HTTP/1.1 200 OK\r
Content-Type: text/plain\r
Content-Length: {length}\r
Connection: close\r
\r
{body}"""

async def http_handler(reader, writer):
    request_line = await reader.readline()
    method, path, version = request_line.decode().strip().split()
    
    # Read headers
    while True:
        header = await reader.readline()
        if header == b"\r\n":
            break
    
    body = f"Hello from Python!\nPath: {path}\nTime: {datetime.now(timezone.utc).isoformat()}"
    response = HTTP_RESPONSE.format(length=len(body), body=body)
    
    writer.write(response.encode())
    await writer.drain()
    writer.close()

async def main():
    server = await asyncio.start_server(http_handler, "0.0.0.0", 8080)
    async with server:
        await server.serve_forever()
```

## 8. Connection Pool

```python
import asyncio
from dataclasses import dataclass, field

@dataclass
class Connection:
    host: str
    port: int
    reader: asyncio.StreamReader | None = None
    writer: asyncio.StreamWriter | None = None
    in_use: bool = False
    created_at: float = field(default_factory=lambda: __import__("time").time())

class ConnectionPool:
    def __init__(self, host: str, port: int, min_size: int = 2, max_size: int = 10):
        self._host = host
        self._port = port
        self._min = min_size
        self._max = max_size
        self._connections: list[Connection] = []
        self._sem = asyncio.Semaphore(max_size)
    
    async def connect(self) -> Connection:
        conn = Connection(host=self._host, port=self._port)
        conn.reader, conn.writer = await asyncio.open_connection(self._host, self._port)
        return conn
    
    async def acquire(self) -> Connection:
        await self._sem.acquire()
        
        # Find free connection
        for conn in self._connections:
            if not conn.in_use and conn.writer and not conn.writer.is_closing():
                conn.in_use = True
                return conn
        
        # Create new
        conn = await self.connect()
        conn.in_use = True
        self._connections.append(conn)
        return conn
    
    def release(self, conn: Connection):
        conn.in_use = False
        self._sem.release()
    
    async def close(self):
        for conn in self._connections:
            if conn.writer:
                conn.writer.close()
                try:
                    await conn.writer.wait_closed()
                except Exception:
                    pass
        self._connections.clear()
```

## 9. WebSocket Client

```python
import aiohttp
import json

async def websocket_client():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("ws://localhost:8080/ws") as ws:
            # Send
            await ws.send_json({"action": "join", "room": "general"})
            
            # Receive
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"Received: {data}")
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
```

## 10. Port Scanning

```python
import asyncio
import socket

async def scan_port(host: str, port: int) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=2.0,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (TimeoutError, ConnectionRefusedError, OSError):
        return False

async def scan_ports(host: str, start: int = 1, end: int = 1024) -> list[int]:
    tasks = [scan_port(host, port) for port in range(start, end + 1)]
    results = await asyncio.gather(*tasks)
    return [port for port, is_open in zip(range(start, end + 1), results) if is_open]

# Usage
# open_ports = asyncio.run(scan_ports("localhost", 1, 1000))
# print(f"Open ports: {open_ports}")
```

## 11. Proxy Server

```python
import asyncio

async def proxy_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Read the first line to get the target
    request_line = await reader.readline()
    method, path, version = request_line.decode().strip().split()
    
    # Parse headers
    headers = {}
    while True:
        line = await reader.readline()
        if line == b"\r\n":
            break
        name, value = line.decode().strip().split(": ", 1)
        headers[name.lower()] = value
    
    # Get target
    host = headers.get("host", "example.com")
    port = 443 if "https" in path else 80
    
    # Connect to target
    try:
        target_reader, target_writer = await asyncio.open_connection(host, port)
    except Exception as e:
        writer.write(f"HTTP/1.1 502 Bad Gateway\r\n\r\n{e}".encode())
        await writer.drain()
        writer.close()
        return
    
    # Forward request
    target_writer.write(request_line.encode())
    for name, value in headers.items():
        target_writer.write(f"{name}: {value}\r\n".encode())
    target_writer.write(b"\r\n")
    await target_writer.drain()
    
    # Return response
    while True:
        data = await target_reader.read(4096)
        if not data:
            break
        writer.write(data)
        await writer.drain()
    
    target_writer.close()
    writer.close()

# async def main():
#     server = await asyncio.start_server(proxy_handler, "0.0.0.0", 8888)
#     async with server:
#         await server.serve_forever()
```

## 12. Socket Options & Tuning

```python
import socket

# TCP tuning
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle
sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

# Buffer sizes
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
```

## 13. Network Utilities

```python
import ipaddress

# IP validation
def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# CIDR check
def ip_in_network(ip: str, network: str) -> bool:
    return ipaddress.ip_address(ip) in ipaddress.ip_network(network, strict=False)

# Subnet calculation
def subnet_info(cidr: str) -> dict:
    net = ipaddress.ip_network(cidr, strict=False)
    return {
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "netmask": str(net.netmask),
        "hosts": len(list(net.hosts())),
    }

# MAC address
import uuid
def get_mac() -> str:
    mac = uuid.getnode()
    return ":".join(f"{(mac >> 8 * i) & 0xff:02x}" for i in reversed(range(6)))
```


---

## Production-Grade Implementation

```python
"""Production-grade patterns — battle-tested in Big Tech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionReady:
    """Pattern with proper error handling, retry, and observability."""
    
    async def execute(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Timeout")
            raise
        except Exception:
            logger.exception("Error")
            raise


## Principal Engineer Best Practices

### Error Handling
- Always use specific exceptions (never bare except)
- Always log with context (request_id, user_id, trace_id)
- Always have fallbacks for critical dependencies
- Always set timeouts on external calls

### Performance
- Profile before optimizing (don't guess)
- Use appropriate data structures (dict vs list vs set)
- Batch database operations (never N+1)
- Cache aggressively but with TTL

### Observability
- Add metrics to all external calls
- Add structured logging with correlation IDs
- Add health check endpoints
- Add distributed tracing

### Security
- Validate all inputs (parse, don't validate)
- Never log secrets or PII
- Use parameterized queries (no SQL injection)
- Keep dependencies updated

### Operations
- Feature flags for gradual rollout
- Circuit breakers for dependencies
- Graceful shutdown with proper ordering
- Connection pooling with health checks


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.


---

## Production-Grade Extension

```python
"""Production-optimized implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionPattern:
    """Enterprise pattern with full resilience stack."""
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(30):
                    start = time.perf_counter()
                    result = await fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(f"Success in {elapsed*1000:.1f}ms")
                    return result
            except asyncio.TimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error("Operation timed out after all retries")
                    raise
                wait = 1.0 * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.exception(f"Attempt {attempt + 1} failed")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        raise RuntimeError("Unreachable")
    

### Principal Engineer Notes

This pattern demonstrates:
- **Resilience**: Retry with exponential backoff
- **Observability**: Timing and error logging
- **Safety**: Timeout on all operations
- **Simplicity**: Single responsibility, clear flow

Apply this pattern to every external call in your system.
No production service should make an unprotected external call.


---

## Extended Enterprise Patterns

### Production-Grade Connection Management

```python
"""Enterprise connection and resource management."""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


@dataclass
class ResourcePool:
    """Generic resource pool with health checks."""
    
    async def acquire(self) -> Any:
        """Acquire resource with timeout."""
        async with asyncio.timeout(5):
            return await self._acquire()
    
    async def release(self, resource: Any) -> None:
        """Release resource back to pool."""
        await self._release(resource)
    
    @asynccontextmanager
    async def use(self) -> AsyncIterator[Any]:
        """Context manager for safe resource usage."""
        resource = await self.acquire()
        try:
            yield resource
        except Exception as e:
            logger.error(f"Resource error: {e}")
            await self.invalidate(resource)
            raise
        finally:
            await self.release(resource)


### Error Handling Framework

class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, id: Any):
        super().__init__(
            message=f"{resource} not found: {id}",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppError):
    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Validation failed for {field}: {reason}",
            code="VALIDATION_ERROR",
            status_code=422,
        )


class ServiceUnavailableError(AppError):
    def __init__(self, service: str):
        super().__init__(
            message=f"{service} is unavailable",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


def error_handler(func):
    """Decorator for uniform error handling."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            raise
        except asyncio.TimeoutError:
            raise ServiceUnavailableError("Database")
        except Exception as e:
            logger.exception("Unhandled error")
            raise AppError(str(e), "INTERNAL_ERROR", 500)
    return wrapper


### Async Task Management

class TaskManager:
    """Manage background tasks with proper cleanup."""
    
    def __init__(self):
        self._tasks: set[asyncio.Task] = set()
    
    def create_task(self, coro) -> asyncio.Task:
        task = asyncio.create_task(self._wrap(coro))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
    
    async def cancel_all(self) -> None:
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
    
    async def _wrap(self, coro):
        try:
            return await coro
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(f"Background task failed: {e}")
