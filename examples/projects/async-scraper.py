#!/usr/bin/env python3
"""Асинхронный веб-скрапер с aiohttp."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class PageResult:
    url: str
    title: str
    status: int
    links: list[str]
    text_length: int
    error: str | None = None


class AsyncScraper:
    def __init__(self, max_concurrent: int = 10):
        self._sem = asyncio.Semaphore(max_concurrent)
        self._results: list[PageResult] = []

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> PageResult:
        async with self._sem:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    text = await resp.text()
                    soup = BeautifulSoup(text, "html.parser")
                    title = soup.title.string if soup.title else "No title"
                    links = [
                        a.get("href") for a in soup.find_all("a", href=True)
                        if a.get("href", "").startswith("http")
                    ]
                    return PageResult(
                        url=url,
                        title=title.strip()[:100],
                        status=resp.status,
                        links=links[:20],
                        text_length=len(text),
                    )
            except Exception as e:
                return PageResult(
                    url=url, title="", status=0,
                    links=[], text_length=0, error=str(e),
                )

    async def scrape(self, urls: list[str]) -> list[PageResult]:
        connector = aiohttp.TCPConnector(limit=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.fetch(session, url) for url in urls]
            self._results = await asyncio.gather(*tasks)
        return self._results


async def main():
    logging.basicConfig(level=logging.INFO)
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://invalid.url.test",
    ]
    scraper = AsyncScraper(max_concurrent=5)
    results = await scraper.scrape(urls)

    for r in results:
        status = "✓" if r.error is None else "✗"
        print(f"{status} {r.url}: {r.title} ({r.status}) [{r.text_length}b]")
        if r.error:
            print(f"   Error: {r.error}")


if __name__ == "__main__":
    asyncio.run(main())


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
