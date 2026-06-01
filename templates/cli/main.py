#!/usr/bin/env python3
"""CLI tool template with argparse and subcommands."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize a new project."""
    name = args.name
    path = args.dir / name if args.dir else Path.cwd() / name
    path.mkdir(parents=True, exist_ok=True)
    (path / "src").mkdir(exist_ok=True)
    (path / "tests").mkdir(exist_ok=True)
    (path / "README.md").write_text(f"# {name}\n\nProject created by CLI tool.\n")
    print(f"✅ Created project {name} at {path}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Build the project."""
    config = args.config or Path("pyproject.toml")
    if not config.exists():
        print(f"❌ Config not found: {config}", file=sys.stderr)
        return 1
    print(f"🔨 Building with {config}...")
    # Здесь: build logic
    print("✅ Build complete")
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean build artifacts."""
    patterns = ["__pycache__", "*.pyc", ".pytest_cache", "dist", "build", "*.egg-info"]
    for pattern in patterns:
        for p in Path.cwd().rglob(pattern):
            if p.is_dir():
                import shutil
                shutil.rmtree(p, ignore_errors=True)
                print(f"  Removed dir: {p}")
            else:
                p.unlink(missing_ok=True)
                print(f"  Removed file: {p}")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="CLI tool template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", required=True, title="Commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--dir", "-d", type=Path, default=None, help="Parent directory")
    init_parser.set_defaults(func=cmd_init)
    
    # build
    build_parser = subparsers.add_parser("build", help="Build the project")
    build_parser.add_argument("--config", "-c", type=Path, default=None, help="Config file path")
    build_parser.set_defaults(func=cmd_build)
    
    # clean
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.set_defaults(func=cmd_clean)
    
    # version
    subparsers.add_parser("version", help="Show version").set_defaults(
        func=lambda _: print("v0.1.0") or 0
    )
    
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        sys.exit(args.func(args))
    parser.print_help()


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════════════
# Extended Production Implementation
# ═══════════════════════════════════════════════════════════════════

"""Production-grade extensions with error handling, retry, 
monitoring, and graceful shutdown."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
import functools
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


# ── Resilience Patterns ──────────────────────────────────────────

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Retry with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Simple circuit breaker for external dependencies."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    
    def __post_init__(self):
        self._failures = 0
        self._last_failure = 0.0
        self._state = "closed"
    
    async def call(self, fn, fallback=None, *args, **kwargs):
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


@asynccontextmanager
async def db_transaction(pool):
    """Database transaction with automatic rollback."""
    conn = await pool.acquire()
    try:
        await conn.execute("BEGIN")
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await pool.release(conn)


# ── Observability ────────────────────────────────────────────────

def monitor(name: str = ""):
    """Monitor function execution time and errors."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"{name or func.__name__}: {elapsed*1000:.1f}ms")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"{name or func.__name__} failed after {elapsed*1000:.1f}ms: {e}")
                raise
        return wrapper
    return decorator


# ── Graceful Shutdown ────────────────────────────────────────────

class GracefulShutdown:
    """Managed graceful shutdown with proper ordering."""
    
    def __init__(self):
        self._hooks: list[tuple[str, callable, int]] = []
        self._shutting_down = False
    
    def register(self, name: str, hook: callable, order: int = 10):
        self._hooks.append((name, hook, order))
    
    async def shutdown(self):
        self._shutting_down = True
        logger.info("Initiating graceful shutdown...")
        
        for name, hook, _ in sorted(self._hooks, key=lambda x: -x[2]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                    logger.info(f"Shutdown: {name} completed")
            except asyncio.TimeoutError:
                logger.warning(f"Shutdown: {name} timed out")
            except Exception as e:
                logger.error(f"Shutdown: {name} failed: {e}")
        
        logger.info("Graceful shutdown complete")


# ── Configuration ────────────────────────────────────────────────

@dataclass
class Settings:
    """12-factor app configuration from environment."""
    debug: bool = False
    database_url: str = ""
    redis_url: str = ""
    log_level: str = "INFO"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: list[str] = None
    jwt_secret: str = ""
    feature_flags: dict[str, bool] = None
    
    @classmethod
    def from_env(cls) -> "Settings":
        import os
        return cls(
            debug=os.getenv("DEBUG", "0") == "1",
            database_url=os.getenv("DATABASE_URL", ""),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_port=int(os.getenv("PORT", "8000")),
            api_workers=int(os.getenv("WORKERS", "4")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            feature_flags={
                "new_pipeline": os.getenv("FEATURE_NEW_PIPELINE", "0") == "1",
                "enhanced_search": os.getenv("FEATURE_ENHANCED_SEARCH", "0") == "1",
            },
        )
    
    def validate(self) -> None:
        """Validate critical settings."""
        errors = []
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        if not self.jwt_secret and not self.debug:
            errors.append("JWT_SECRET is required")
        if errors:
            raise ValueError("; ".join(errors))


# ── Health Checks ─────────────────────────────────────────────────

@dataclass
class HealthCheck:
    """Composite health check for microservice."""
    
    async def check_liveness(self) -> dict:
        return {"status": "alive", "timestamp": time.time()}
    
    async def check_readiness(self, deps: dict[str, callable]) -> dict:
        status = "healthy"
        checks = {}
        for name, check_fn in deps.items():
            try:
                async with asyncio.timeout(2):
                    await check_fn()
                checks[name] = "healthy"
            except Exception as e:
                checks[name] = f"unhealthy: {e}"
                status = "unhealthy"
        return {"status": status, "checks": checks}
    
    async def check_startup(self) -> dict:
        return {"status": "started", "timestamp": time.time()}
