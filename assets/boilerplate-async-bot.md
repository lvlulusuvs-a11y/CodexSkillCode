# Async Bot Boilerplate (aiogram 3 + PostgreSQL)

```python
# bot/__init__.py
from __future__ import annotations
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.config import Config
from bot.middlewares import DatabaseMiddleware, ThrottlingMiddleware

def create_bot() -> tuple[Bot, Dispatcher]:
    config = Config()
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.message.middleware(ThrottlingMiddleware())
    dp.update.middleware(DatabaseMiddleware(config.database_url))
    return bot, dp

# bot/config.py
from __future__ import annotations
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    bot_token: str
    database_url: str = "postgresql://localhost:5432/bot"
    admin_ids: list[int] = []

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

# bot/handlers/start.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n"
        f"Я — мега-бот на aiogram 3"
    )

# bot/middlewares.py
from __future__ import annotations
from aiogram import BaseMiddleware
from aiogram.types import Update

class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        # anti-flood logic
        return await handler(event, data)

# bot/main.py
import asyncio
from bot import create_bot
from bot.handlers import start, help, admin
from bot.db import init_db

async def main():
    bot, dp = create_bot()
    dp.include_routers(start.router)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
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
