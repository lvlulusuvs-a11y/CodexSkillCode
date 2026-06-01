#!/usr/bin/env python3
"""Quickstart — быстрый старт с mega-coding.

Запуск:
    python examples/quickstart.py                    # демо всех фич
    python examples/quickstart.py --benchmark        # замер производительности
    python examples/quickstart.py --check path/to/   # quality check
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


# ── Example 1: Data Processing ──────────────────
def process_users(users: list[dict]) -> list[dict]:
    """Обработка списка пользователей.
    
    Демонстрирует: list comprehensions, dataclass-like dicts,
    обработка ошибок, typing, early return.
    """
    if not users:
        return []
    
    def validate(user: dict) -> bool:
        return bool(user.get("name") and user.get("email") and "@" in user.get("email", ""))
    
    def enrich(user: dict) -> dict:
        return {
            "id": user.get("id", 0),
            "name": user["name"].strip().title(),
            "email": user["email"].strip().lower(),
            "domain": user["email"].split("@")[1],
            "active": user.get("active", True),
        }
    
    return [enrich(u) for u in users if validate(u)]


# ── Example 2: Async Pipeline ────────────────────
import asyncio
from typing import Any

async def fetch_data(source: str) -> dict[str, Any]:
    """Симуляция асинхронного запроса."""
    await asyncio.sleep(0.1)  # эмуляция I/O
    return {"source": source, "data": f"data from {source}"}

async def run_async_pipeline(sources: list[str]) -> list[dict[str, Any]]:
    """Параллельная обработка нескольких источников."""
    tasks = [fetch_data(src) for src in sources]
    return await asyncio.gather(*tasks)


# ── Example 3: Retry Decorator ──────────────────
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 0.5):
    """Декоратор retry с экспоненциальной задержкой."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            wait = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        print(f"  Attempt {attempt+1} failed: {e}. Retry in {wait:.1f}s")
                        time.sleep(wait)
                        wait *= 2
            raise last_error
        return wrapper
    return decorator


# ── Example 4: Result Type ──────────────────────
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

type Result[T, E] = Ok[T] | Err[E]

def safe_divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Err("division by zero")
    return Ok(a / b)


# ── Example 5: FastAPI-style handler ────────────
from dataclasses import dataclass, field

@dataclass
class Request:
    path: str
    method: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | None = None

@dataclass  
class Response:
    status: int = 200
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)

class SimpleRouter:
    def __init__(self) -> None:
        self._routes: list[tuple[str, str, Any]] = []
    
    def get(self, path: str):
        def decorator(handler):
            self._routes.append(("GET", path, handler))
            return handler
        return decorator
    
    def post(self, path: str):
        def decorator(handler):
            self._routes.append(("POST", path, handler))
            return handler
        return decorator
    
    def dispatch(self, request: Request) -> Response:
        for method, path, handler in self._routes:
            if request.method == method and request.path == path:
                return handler(request)
        return Response(status=404, body={"error": "not found"})

router = SimpleRouter()

@router.get("/health")
def health(req: Request) -> Response:
    return Response(body={"status": "ok"})

@router.post("/users")
def create_user(req: Request) -> Response:
    return Response(status=201, body={"id": 1, **req.body})


# ── Main Demo ───────────────────────────────────
def run_demo() -> None:
    print("=" * 60)
    print("🚀 Mega-Coding Quickstart Demo")
    print("=" * 60)
    
    # 1. Data processing
    print("\n1️⃣  Data Processing:")
    users = [
        {"id": 1, "name": "  alice  ", "email": "Alice@Example.COM", "active": True},
        {"id": 2, "name": "bob", "email": "bob@test.com", "active": True},
        {"id": 3, "name": "", "email": "invalid"},  # невалидный
    ]
    processed = process_users(users)
    for u in processed:
        print(f"   ✅ {u['name']:12} → {u['email']:20} [{u['domain']}]")
    
    # 2. Async pipeline
    print("\n2️⃣  Async Pipeline:")
    results = asyncio.run(run_async_pipeline(["users", "orders", "payments"]))
    for r in results:
        print(f"   ✅ {r['source']:10} → {r['data']}")
    
    # 3. Retry decorator
    print("\n3️⃣  Retry Decorator:")
    call_count = 0
    
    @retry(max_attempts=2, delay=0.1)
    def flaky_function() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Network timeout")
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # 4. Result type
    print("\n4️⃣  Result Type:")
    for a, b in [(10, 2), (5, 0)]:
        match safe_divide(a, b):
            case Ok(v): print(f"   ✅ {a}/{b} = {v}")
            case Err(e): print(f"   ❌ {a}/{b} = {e}")
    
    # 5. Router
    print("\n5️⃣  Simple Router:")
    for req in [Request("/health", "GET"), Request("/users", "POST", body={"name": "Test"})]:
        resp = router.dispatch(req)
        status_icon = "✅" if resp.status < 400 else "❌"
        print(f"   {status_icon} {req.method} {req.path} → {resp.status}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo complete! See SKILL.md for more.")
    print("=" * 60)


def run_benchmark() -> None:
    """Простой бенчмарк."""
    from scripts.benchmark import compare
    
    print("\n📊 Benchmark:")
    
    # Data processing benchmark
    test_users = [
        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "active": True}
        for i in range(1000)
    ]
    
    start = time.perf_counter()
    for _ in range(100):
        process_users(test_users)
    elapsed = time.perf_counter() - start
    print(f"   process_users() x100: {elapsed:.3f}s ({elapsed/100*1000:.1f}ms avg)")


def run_quality_check(path: str) -> None:
    """Запустить проверку качества кода."""
    from scripts.code_review_bot import review_file
    from pathlib import Path
    
    p = Path(path)
    if p.is_dir():
        exit_code = 0
        for pyfile in sorted(p.rglob("*.py")):
            exit_code += review_file(pyfile)
        sys.exit(exit_code)
    else:
        sys.exit(review_file(p))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mega-Coding Quickstart")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--check", type=str, help="Run quality check on path")
    
    args = parser.parse_args(argv)
    
    if args.benchmark:
        run_benchmark()
    elif args.check:
        run_quality_check(args.check)
    else:
        run_demo()


if __name__ == "__main__":
    main()


# ── Extended Production Example ─────────────────────────────────────

"""Extended with error handling, retry, logging, and monitoring.
This is what production-grade code looks like in Big Tech.
"""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
import functools

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        wait = delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt + 1}/{max_attempts} after {wait:.1f}s")
                        await asyncio.sleep(wait)
            raise last_error
        return wrapper
    return decorator


def timed(func):
    """Log execution time."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed*1000:.1f}ms")
    return wrapper


@dataclass
class ProductionService:
    """Production-grade service with full observability."""
    
    async def health_check(self) -> dict[str, Any]:
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
        }
    
    @retry(max_attempts=3)
    @timed
    async def process_with_resilience(self, data: dict) -> dict:
        """Process data with retry and timing."""
        async with asyncio.timeout(30):
            result = await self._process(data)
            logger.info("Processed", extra={"data_size": len(data)})
            return result
    
    async def _process(self, data: dict) -> dict:
        """Core processing logic."""
        return {"status": "ok", "data": data}


# Использование:
# service = ProductionService()
# result = await service.process_with_resilience({"key": "value"})
