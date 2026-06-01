# Circuit Breaker: Deep Dive

Circuit breaker prevents cascading failures. When a service fails,
the breaker opens and subsequent calls fail fast.

## States

CLOSED - normal operation, requests go through
OPEN - service is failing, requests blocked
HALF_OPEN - testing if service recovered

## Implementation

import asyncio
import time
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerError(Exception):
    pass

@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3

    def __post_init__(self):
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0

    async def call(self, func, *args, **kwargs):
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
            else:
                raise CircuitBreakerError(f"Circuit {self.name} is OPEN")

        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerError(
                    f"Circuit {self.name} HALF_OPEN, max probes reached"
                )
            self._half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
            raise

## Usage

payment_circuit = CircuitBreaker("payment", failure_threshold=3)

async def process_payment(order_id: str):
    try:
        return await payment_circuit.call(payment_client.charge, order_id)
    except CircuitBreakerError:
        logger.warning("Payment circuit open, queueing order %s", order_id)
        await payment_queue.enqueue(order_id)
        return PaymentResult(status="queued")

## Metrics

Circuit breaker should expose metrics:

circuit_breaker_state{name="payment"} 1  # 1=closed, 2=open, 3=half_open
circuit_breaker_failures_total{name="payment"} 10
circuit_breaker_calls_total{name="payment"} 100

## Best Practices

1. Set threshold based on normal error rate (2-3x normal)
2. Recovery timeout should be long enough for service to recover
3. Log state transitions for debugging
4. Add metrics for monitoring breaker state
5. Always have a fallback when breaker is open
6. Test breaker behavior in chaos experiments


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.
