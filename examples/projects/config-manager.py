#!/usr/bin/env python3
"""Менеджер конфигураций с поддержкой JSON/YAML/TOML/ENV."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class Config:
    def __init__(self, path: str | Path | None = None):
        self._data: dict[str, Any] = {}
        if path:
            self.load(path)

    def load(self, path: str | Path) -> None:
        p = Path(path)
        ext = p.suffix.lower()
        text = p.read_text(encoding="utf-8")

        if ext in (".json",):
            self._data = json.loads(text)
        elif ext in (".yaml", ".yml"):
            import yaml
            self._data = yaml.safe_load(text)
        elif ext in (".toml",):
            import tomllib
            self._data = tomllib.loads(text)
        elif ext in (".env",):
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                self._data[key.strip()] = val.strip().strip("\"'")
        else:
            raise ValueError(f"Unsupported config format: {ext}")

    def export(self, path: str | Path, fmt: str | None = None) -> None:
        p = Path(path)
        fmt = fmt or p.suffix.lstrip(".")
        text = ""
        if fmt == "json":
            text = json.dumps(self._data, indent=2, ensure_ascii=False)
        elif fmt in ("yaml", "yml"):
            import yaml
            text = yaml.dump(self._data, default_flow_style=False)
        elif fmt == "toml":
            import tomli_w
            text = tomli_w.dumps(self._data)
        elif fmt == "env":
            text = "\n".join(f"{k}={v}" for k, v in self._data.items())
        p.write_text(text)

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        data = self._data
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k)
            else:
                return default
            if data is None:
                return default
        return data

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
            if not isinstance(data, dict):
                raise KeyError(f"Cannot set {key}: {k} is not a dict")
        data[keys[-1]] = value

    def __getitem__(self, key: str) -> Any:
        val = self.get(key)
        if val is None and key not in self._data:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __repr__(self) -> str:
        return f"Config({json.dumps(self._data, indent=2)})"


def main() -> int:
    import sys
    if len(sys.argv) < 2:
        print("Usage: config-manager.py <config-file> [key] [value]")
        return 1

    config = Config(sys.argv[1])
    if len(sys.argv) == 2:
        print(config)
    elif len(sys.argv) == 3:
        print(config.get(sys.argv[2]))
    else:
        config.set(sys.argv[2], sys.argv[3])
        config.export(sys.argv[1])
    return 0


if __name__ == "__main__":
    main()


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
