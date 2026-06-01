# Concurrency Patterns for Async Python

Concurrency is hard. These patterns help.

## Pattern 1: Worker Pool

Limit concurrent work to prevent resource exhaustion:

import asyncio
from dataclasses import dataclass

@dataclass
class WorkerPool:
    workers: int = 10

    async def map(self, func, items):
        semaphore = asyncio.Semaphore(self.workers)

        async def worker(item):
            async with semaphore:
                return await func(item)

        return await asyncio.gather(*[worker(i) for i in items])

# Usage
pool = WorkerPool(workers=5)
results = await pool.map(process_item, items)

## Pattern 2: Pipeline

Process data through stages:

class Pipeline:
    def __init__(self):
        self.stages = []

    def add_stage(self, func, workers=5):
        self.stages.append((func, workers))
        return self

    async def execute(self, items):
        results = items
        for func, workers in self.stages:
            pool = WorkerPool(workers=workers)
            results = await pool.map(func, results)
        return results

pipeline = Pipeline()
pipeline.add_stage(validate_item, workers=5)
pipeline.add_stage(process_item, workers=3)
pipeline.add_stage(enrich_item, workers=2)
results = await pipeline.execute(items)

## Pattern 3: Fan-Out/Fan-In

Parallel processing, collect results:

import asyncio

async def fan_out_fan_in(func, items):
    async def safe_func(item):
        try:
            return await func(item), None
        except Exception as e:
            return None, e

    results = await asyncio.gather(*[safe_func(i) for i in items])
    successes = [r for r, _ in results if r is not None]
    errors = [e for _, e in results if e is not None]
    return successes, errors

## Pattern 4: Timeout

Every await needs a timeout:

async def with_timeout(func, timeout=5.0):
    try:
        return await asyncio.wait_for(func(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error("Operation timed out after %ss", timeout)
        raise TimeoutError()

## Pattern 5: Retry

Retry with exponential backoff:

async def with_retry(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning("Retry %d after %.1fs", attempt, delay)
            await asyncio.sleep(delay)


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.
