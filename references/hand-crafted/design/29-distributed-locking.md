# Distributed Locking: Coordinate Access to Shared Resources

Distributed locks prevent race conditions across multiple service instances.

## When You Need a Distributed Lock

1. Prevent duplicate payment processing
2. Coordinate inventory updates
3. Prevent concurrent job execution
4. Rate limiting across instances
5. Leader election

## Redis-Based Lock

import asyncio
import uuid
from dataclasses import dataclass

@dataclass
class RedisLock:
    redis: any
    key: str
    ttl: int = 30
    retry_delay: float = 0.1
    max_retries: int = 10

    def __post_init__(self):
        self.lock_key = f"lock:{self.key}"
        self.token = str(uuid.uuid4())

    async def acquire(self) -> bool:
        for _ in range(self.max_retries):
            acquired = await self.redis.set(
                self.lock_key,
                self.token,
                nx=True,
                ex=self.ttl,
            )
            if acquired:
                return True
            await asyncio.sleep(self.retry_delay)
        return False

    async def release(self):
        # Lua script ensures atomic check-and-delete
        await self.redis.eval("""
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
        """, 1, self.lock_key, self.token)

    async def __aenter__(self):
        acquired = await self.acquire()
        if not acquired:
            raise LockError(f"Could not acquire lock: {self.key}")
        return self

    async def __aexit__(self, *args):
        await self.release()

## Usage

async def process_payment(order_id: str):
    async with RedisLock(redis, f"payment:{order_id}"):
        # Only one instance processes this order
        order = await get_order(order_id)
        if order.status == "paid":
            return  # Already processed
        await charge_payment(order)
        await update_order_status(order_id, "paid")

## Lock Renewal

For long operations, renew the lock:

class RenewableLock(RedisLock):
    async def keep_alive(self):
        while True:
            await asyncio.sleep(self.ttl / 3)
            await self.redis.expire(self.lock_key, self.ttl)

## Redlock Algorithm

For stronger guarantees, use Redlock (acquire lock on multiple Redis nodes):

1. Get current time
2. Acquire lock on N/2 + 1 Redis nodes
3. If acquired within window, lock is held
4. If not, release all partial locks
5. Set TTL to reduce window of vulnerability


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.
