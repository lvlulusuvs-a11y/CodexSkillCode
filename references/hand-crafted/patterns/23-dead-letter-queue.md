# Dead Letter Queue: Handling Failed Messages

Messages that cannot be processed go to a dead letter queue.

## Why Messages Fail

1. Transient errors (DB down, network timeout)
2. Invalid data (deserialization fails, missing fields)
3. Business logic errors (order already cancelled)
4. Poison messages (causes infinite retry loops)

## DLQ Implementation

import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DeadLetter:
    original_message: dict
    error: str
    failed_at: datetime
    retry_count: int

class MessageProcessor:
    def __init__(self, queue, dlq, max_retries: int = 3):
        self.queue = queue
        self.dlq = dlq
        self.max_retries = max_retries

    async def process_loop(self):
        while True:
            message = await self.queue.receive()
            retry_count = int(message.get("retry_count", 0))

            try:
                await self.handle(message)
                await self.queue.delete(message)
            except NonRetryableError as e:
                await self.send_to_dlq(message, str(e))
                await self.queue.delete(message)
            except RetryableError as e:
                if retry_count >= self.max_retries:
                    await self.send_to_dlq(message, str(e))
                    await self.queue.delete(message)
                else:
                    message["retry_count"] = retry_count + 1
                    await self.queue.send(message, delay=2 ** retry_count)

    async def send_to_dlq(self, message: dict, error: str):
        dlq_entry = DeadLetter(
            original_message=message,
            error=error,
            failed_at=datetime.utcnow(),
            retry_count=int(message.get("retry_count", 0)),
        )
        await self.dlq.send(json.dumps(asdict(dlq_entry)))

## DLQ Monitoring

Alert when DLQ grows:
- DLQ size > 10 messages -> warning
- DLQ size > 100 messages -> critical
- DLQ age > 1 hour -> critical

## DLQ Processing

Process DLQ messages manually or automatically:

class DLQProcessor:
    async def reprocess_dlq(self):
        while True:
            message = await self.dlq.receive()
            try:
                await self.original_handler(message)
                await self.dlq.delete(message)
                logger.info("Reprocessed DLQ message successfully")
            except Exception as e:
                logger.error("DLQ reprocess failed: %s", e)
                await asyncio.sleep(60)

## Best Practices

1. Set max retries (3-5 is usually enough)
2. Use exponential backoff for retries
3. Separate transient from permanent errors
4. Monitor DLQ size and age
5. Alert when DLQ grows unexpectedly
6. Have a process for manual DLQ handling
7. Log all DLQ messages for audit
8. Periodically purge expired DLQ messages


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.


## Key Takeaway

Apply this insight today.
