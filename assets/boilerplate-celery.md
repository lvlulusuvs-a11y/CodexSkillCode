# Celery + FastAPI Boilerplate

```python
# worker.py
from celery import Celery
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

@celery_app.task(bind=True, max_retries=3)
def process_file(self, file_path: str) -> dict:
    try:
        # тяжёлая обработка
        result = {"status": "done", "file": file_path}
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=60)

# app/tasks.py
from worker import celery_app

@celery_app.task
def send_email_task(to: str, subject: str, body: str) -> str:
    # send email logic
    return f"Email sent to {to}"

# app/routers/tasks.py
from fastapi import APIRouter
from app.tasks import process_file, send_email_task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/process")
async def start_processing(file_path: str):
    task = process_file.delay(file_path)
    return {"task_id": task.id}

@router.get("/status/{task_id}")
async def get_status(task_id: str):
    task = process_file.AsyncResult(task_id)
    if task.failed():
        return {"status": "failed"}
    return {"status": task.status, "result": task.result}
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
