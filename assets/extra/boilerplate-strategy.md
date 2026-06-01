# Strategy Pattern Boilerplate

## Discount Strategies

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, total: float) -> float: ...

class NoDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return 0.0

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self._percent = percent
    
    def calculate(self, total: float) -> float:
        return total * self._percent / 100

class FixedDiscount(DiscountStrategy):
    def __init__(self, amount: float):
        self._amount = amount
    
    def calculate(self, total: float) -> float:
        return min(self._amount, total)

class TieredDiscount(DiscountStrategy):
    def __init__(self, tiers: list[tuple[float, float]]):
        self._tiers = sorted(tiers, key=lambda x: x[0], reverse=True)
    
    def calculate(self, total: float) -> float:
        for threshold, percent in self._tiers:
            if total >= threshold:
                return total * percent / 100
        return 0.0

class Order:
    def __init__(self, items: list[dict], strategy: DiscountStrategy):
        self._items = items
        self._strategy = strategy
    
    @property
    def subtotal(self) -> float:
        return sum(item["price"] * item["qty"] for item in self._items)
    
    def total(self) -> float:
        return self.subtotal - self._strategy.calculate(self.subtotal)

# Usage
order = Order(
    items=[{"name": "Laptop", "price": 1000, "qty": 1}],
    strategy=TieredDiscount([(500, 5), (1000, 10), (5000, 15)]),
)
print(order.total())  # 900 (1000 - 10%)
```

## Payment Strategies

```python
class PaymentStrategy(ABC):
    @abstractmethod
    async def pay(self, amount: float, currency: str) -> dict: ...

class StripePayment(PaymentStrategy):
    async def pay(self, amount: float, currency: str) -> dict:
        import stripe
        return stripe.Charge.create(amount=int(amount * 100), currency=currency)

class PayPalPayment(PaymentStrategy):
    async def pay(self, amount: float, currency: str) -> dict:
        return {"status": "success", "provider": "paypal"}

class CryptoPayment(PaymentStrategy):
    async def pay(self, amount: float, currency: str) -> dict:
        return {"status": "pending", "provider": "crypto"}

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
    
    async def process(self, amount: float, currency: str = "usd") -> dict:
        return await self._strategy.pay(amount, currency)

# Usage
processor = PaymentProcessor(StripePayment())
result = await processor.process(99.99)
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
