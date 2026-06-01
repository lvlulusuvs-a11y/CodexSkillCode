#!/usr/bin/env python3
"""Простой анализатор данных на Python."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Any


class DataAnalyzer:
    def __init__(self, path: Path):
        self.path = path
        self.raw: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        ext = self.path.suffix.lower()
        if ext == ".csv":
            with self.path.open(newline="", encoding="utf-8") as f:
                self.raw = list(csv.DictReader(f))
        elif ext == ".json":
            self.raw = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            raise ValueError(f"Unsupported format: {ext}")

    @property
    def columns(self) -> list[str]:
        return list(self.raw[0].keys()) if self.raw else []

    @property
    def row_count(self) -> int:
        return len(self.raw)

    def value_counts(self, column: str) -> dict[str, int]:
        return dict(Counter(r.get(column, "") for r in self.raw).most_common())

    def filter(self, column: str, value: Any) -> list[dict]:
        return [r for r in self.raw if r.get(column) == value]

    def summary(self) -> dict[str, Any]:
        if not self.raw:
            return {"error": "No data"}
        result: dict[str, Any] = {
            "file": str(self.path),
            "rows": self.row_count,
            "columns": len(self.columns),
            "column_names": self.columns,
        }
        for col in self.columns:
            values = [r.get(col) for r in self.raw if r.get(col)]
            if values and all(v.replace(".", "", 1).isdigit() for v in values if v):
                nums = [float(v) for v in values]
                result[f"{col}_stats"] = {
                    "min": min(nums),
                    "max": max(nums),
                    "avg": sum(nums) / len(nums),
                }
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.raw, indent=indent, ensure_ascii=False)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: data-analyzer.py <file.csv|file.json> [--summary]")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    analyzer = DataAnalyzer(path)
    print(f"Loaded {analyzer.row_count} rows, {len(analyzer.columns)} columns")
    print(f"Columns: {', '.join(analyzer.columns)}")

    if "--summary" in sys.argv:
        sm = analyzer.summary()
        print(json.dumps(sm, indent=2, ensure_ascii=False))

    return 0


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
