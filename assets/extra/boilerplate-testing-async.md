# Async Testing Boilerplate

```python
"""Шаблон для тестирования асинхронного кода."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio


# ── Fixtures ──────────────────────────────────
@pytest_asyncio.fixture
async def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    await loop.shutdown_asyncgens()
    loop.close()


@pytest_asyncio.fixture
async def mock_redis() -> AsyncMock:
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.setex.return_value = True
    mock.delete.return_value = True
    return mock


@pytest_asyncio.fixture
async def mock_db_session() -> AsyncMock:
    """Mock DB session."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.flush.return_value = None
    return mock


# ── Tests ─────────────────────────────────────
@pytest.mark.asyncio
async def test_async_function():
    """Test a simple async function."""
    result = await some_async_function()
    assert result == expected_value


@pytest.mark.asyncio
async def test_async_with_mock(mock_redis):
    """Test with async mock."""
    service = MyService(redis=mock_redis)
    result = await service.get_data("key")
    
    mock_redis.get.assert_called_once_with("key")
    assert result == expected


@pytest.mark.asyncio
async def test_async_gather():
    """Test parallel execution."""
    async def worker(i: int) -> int:
        await asyncio.sleep(0.01)
        return i * 2
    
    results = await asyncio.gather(*[worker(i) for i in range(5)])
    assert results == [0, 2, 4, 6, 8]


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    mock = AsyncMock()
    mock.__aenter__.return_value = mock
    
    async with mock as m:
        assert m is mock
    
    mock.__aenter__.assert_called_once()
    mock.__aexit__.assert_called_once()


@pytest.mark.asyncio
async def test_async_timeout():
    """Test timeout in async code."""
    async def slow_operation():
        await asyncio.sleep(10)
        return "done"
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.1)


@pytest.mark.asyncio
async def test_async_exception():
    """Test exception in async code."""
    mock_repo = AsyncMock()
    mock_repo.get.side_effect = ValueError("Not found")
    
    service = MyService(repo=mock_repo)
    
    with pytest.raises(ValueError, match="Not found"):
        await service.get(1)


@pytest.mark.asyncio
async def test_async_generator():
    """Test async generator."""
    async def async_gen():
        for i in range(3):
            await asyncio.sleep(0.01)
            yield i
    
    result = [item async for item in async_gen()]
    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_async_queue():
    """Test asyncio queue."""
    queue: asyncio.Queue[int] = asyncio.Queue()
    
    async def producer():
        for i in range(3):
            await queue.put(i)
    
    async def consumer():
        results = []
        for _ in range(3):
            item = await queue.get()
            results.append(item)
        return results
    
    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer())
        results = await consumer()
    
    assert results == [0, 1, 2]


@pytest.mark.asyncio
async def test_async_semaphore():
    """Test semaphore limits concurrency."""
    sem = asyncio.Semaphore(2)
    max_concurrent = 0
    current = 0
    
    async def limited_work():
        nonlocal current, max_concurrent
        async with sem:
            current += 1
            max_concurrent = max(max_concurrent, current)
            await asyncio.sleep(0.05)
            current -= 1
    
    tasks = [limited_work() for _ in range(10)]
    await asyncio.gather(*tasks)
    
    assert max_concurrent == 2  # semaphore limit
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
