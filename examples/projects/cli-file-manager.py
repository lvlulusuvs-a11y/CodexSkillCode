#!/usr/bin/env python3
"""CLI файловый менеджер с аргументами."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


class FileManager:
    def __init__(self, base: Path = Path(".")):
        self.base = base.resolve()

    def ls(self, pattern: str = "*") -> list[dict[str, Any]]:
        items = []
        for p in sorted(self.base.glob(pattern)):
            items.append({
                "name": p.name,
                "size": p.stat().st_size,
                "is_dir": p.is_dir(),
                "modified": p.stat().st_mtime,
            })
        return items

    def info(self, path: str) -> dict[str, Any]:
        p = self.base / path
        if not p.exists():
            return {"error": f"File not found: {path}"}
        return {
            "name": p.name,
            "path": str(p.relative_to(self.base)),
            "size": p.stat().st_size,
            "is_dir": p.is_dir(),
            "is_file": p.is_file(),
            "modified": p.stat().st_mtime,
            "extension": p.suffix,
        }

    def tree(self, max_depth: int = 2) -> list[str]:
        lines: list[str] = []

        def _walk(p: Path, depth: int) -> None:
            if depth > max_depth:
                return
            indent = "  " * depth
            lines.append(f"{indent}{p.name}/" if p.is_dir() else f"{indent}{p.name}")
            if p.is_dir():
                for child in sorted(p.iterdir()):
                    _walk(child, depth + 1)

        _walk(self.base, 0)
        return lines


def cmd_ls(args: argparse.Namespace) -> int:
    fm = FileManager(Path(args.path))
    items = fm.ls(args.pattern)
    for item in items:
        icon = "📁" if item["is_dir"] else "📄"
        print(f"{icon} {item['name']:30s} {item['size']:>8d} B")
    return 0


def cmd_tree(args: argparse.Namespace) -> int:
    fm = FileManager(Path(args.path))
    for line in fm.tree(args.depth):
        print(line)
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    fm = FileManager(Path(args.path))
    info = fm.info(args.file)
    for key, val in info.items():
        print(f"  {key}: {val}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="fm", description="File Manager CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ls = sub.add_parser("ls")
    p_ls.add_argument("path", nargs="?", default=".")
    p_ls.add_argument("--pattern", default="*")
    p_ls.set_defaults(func=cmd_ls)

    p_tree = sub.add_parser("tree")
    p_tree.add_argument("path", nargs="?", default=".")
    p_tree.add_argument("--depth", type=int, default=2)
    p_tree.set_defaults(func=cmd_tree)

    p_info = sub.add_parser("info")
    p_info.add_argument("path", nargs="?", default=".")
    p_info.add_argument("file", help="File to inspect")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())


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
