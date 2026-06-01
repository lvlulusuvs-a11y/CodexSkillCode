# Async vs Sync: Choosing the Right Model

Async is not always better than sync. Here is when to use each.

## The Simple Rule

I/O-bound tasks -> async (waiting for network, disk, database)
CPU-bound tasks -> sync (or multiprocessing)

## I/O-Bound: Async Wins

Async parallelizes waiting:

Sync approach:
for url in urls:
    response = requests.get(url)  # 100ms wait per URL
    process(response)
# 10 URLs * 100ms = 1 second

Async approach:
async with httpx.AsyncClient() as client:
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    for r in responses:
        process(r)
# 10 URLs, all concurrent = ~100ms total

## CPU-Bound: Sync Wins

Async adds overhead for CPU work:

The event loop has scheduling costs. For CPU operations,
just use regular functions. If you need parallelism,
use multiprocessing:

from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:
    results = pool.map(cpu_intensive_func, dataset)

## The Cost of Async

Async is not free. It adds:

1. Event loop overhead (scheduling, context switching)
2. Complexity (harder to debug and trace)
3. Risk of blocking calls (time.sleep blocks everything)
4. Resource contention (too many concurrent tasks)

When NOT to use async:
- Simple CRUD under 100 rps
- CLI tools and scripts
- CPU-heavy services
- Internal ETL pipelines

## Hybrid Approach

The best of both worlds: async for I/O, offload CPU to workers.

from concurrent.futures import ProcessPoolExecutor
import asyncio

pool = ProcessPoolExecutor(max_workers=4)

async def process_report(request):
    data = await storage.download(request.file_id)

    loop = asyncio.get_running_loop()
    report = await loop.run_in_executor(pool, generate_report, data)

    result = await storage.upload(report)
    return result

## My Default Choices

Web API -> async (FastAPI/Starlette)
CLI tool -> sync (click)
Data pipeline -> sync + multiprocessing
WebSocket server -> async
ML inference -> sync with batching
File processing -> async (aiofiles)
Cron jobs -> sync
API gateway -> async

Choose the right tool for the workload, not for the trend.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.
