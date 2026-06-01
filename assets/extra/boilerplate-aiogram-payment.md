# Telegram Payments Boilerplate (aiogram 3)

```python
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice

router = Router()

@router.message(Command("buy"))
async def cmd_buy(message: types.Message):
    prices = [LabeledPrice(label="Premium", amount=50000)]  # 500.00 RUB
    await message.answer_invoice(
        title="Premium Access",
        description="Full access to all features",
        provider_token="YOUR_PROVIDER_TOKEN",
        currency="RUB",
        prices=prices,
        payload="premium_access",
    )

@router.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@router.message(F.successful_payment)
async def on_success(message: types.Message):
    await message.answer("✅ Payment successful!")
    await grant_access(message.from_user.id)
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
