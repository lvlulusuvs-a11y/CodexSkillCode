"""Aiogram 3 bot production template."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from pydantic_settings import BaseSettings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# ── Config ─────────────────────────────────────
class Settings(BaseSettings):
    bot_token: str
    admin_ids: list[int] = []
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()


# ── FSM States ─────────────────────────────────
class Form(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_email = State()


# ── Router ─────────────────────────────────────
router = Router()


# ── Commands ───────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    await msg.answer(
        f"👋 <b>Привет, {msg.from_user.first_name}!</b>\n\n"
        "Я шаблон aiogram 3 бота.\n"
        "Команды:\n"
        "/help — помощь\n"
        "/form — форма обратной связи\n"
        "/info — информация",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("help"))
async def cmd_help(msg: Message) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📘 Документация", url="https://docs.aiogram.dev")],
            [InlineKeyboardButton(text="🐛 Сообщить о баге", callback_data="bug_report")],
        ]
    )
    await msg.answer("Помощь и ссылки:", reply_markup=kb)


@router.message(Command("info"))
async def cmd_info(msg: Message) -> None:
    await msg.answer(
        f"ID: <code>{msg.from_user.id}</code>\n"
        f"Username: @{msg.from_user.username or 'нет'}\n"
        f"Chat type: {msg.chat.type}",
        parse_mode=ParseMode.HTML,
    )


# ── FSM Form ───────────────────────────────────
@router.message(Command("form"))
async def cmd_form(msg: Message, state: FSMContext) -> None:
    await state.set_state(Form.waiting_name)
    await msg.answer("Как вас зовут?")


@router.message(Form.waiting_name, F.text)
async def form_name(msg: Message, state: FSMContext) -> None:
    await state.update_data(name=msg.text)
    await state.set_state(Form.waiting_phone)
    await msg.answer("Ваш номер телефона?")


@router.message(Form.waiting_phone, F.text)
async def form_phone(msg: Message, state: FSMContext) -> None:
    await state.update_data(phone=msg.text)
    await state.set_state(Form.waiting_email)
    await msg.answer("Ваш email?")


@router.message(Form.waiting_email, F.text)
async def form_email(msg: Message, state: FSMContext) -> None:
    data = await state.update_data(email=msg.text)
    await state.clear()

    user_info = (
        f"✅ <b>Форма заполнена!</b>\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Email: {data['email']}"
    )
    await msg.answer(user_info, parse_mode=ParseMode.HTML)

    # Уведомить админов
    for admin_id in settings.admin_ids:
        try:
            await msg.bot.send_message(admin_id, f"Новая форма: {data}")
        except Exception as e:
            logger.warning("failed to notify admin %s: %s", admin_id, e)


# ── Callbacks ──────────────────────────────────
@router.callback_query(F.data == "bug_report")
async def cb_bug_report(cq: CallbackQuery) -> None:
    await cq.answer("Спасибо! Функция в разработке.", show_alert=True)


# ── Free text ──────────────────────────────────
@router.message(F.text)
async def echo(msg: Message) -> None:
    """Если не команда — эхо (или ignore в проде)."""
    await msg.answer(f"Вы написали: {msg.text}")


# ── Main ───────────────────────────────────────
async def main() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.info("starting bot...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


# ═══════════════════════════════════════════════════════════════════
# Extended Production Implementation
# ═══════════════════════════════════════════════════════════════════

"""Production-grade extensions with error handling, retry, 
monitoring, and graceful shutdown."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
import functools
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


# ── Resilience Patterns ──────────────────────────────────────────

def with_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Retry with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Simple circuit breaker for external dependencies."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    
    def __post_init__(self):
        self._failures = 0
        self._last_failure = 0.0
        self._state = "closed"
    
    async def call(self, fn, fallback=None, *args, **kwargs):
        if self._state == "open":
            if time.monotonic() - self._last_failure >= self.recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit half-open, testing recovery")
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError("Circuit breaker is open")
        
        try:
            result = await fn(*args, **kwargs)
            self._failures = 0
            self._state = "closed"
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = "open"
                logger.error(f"Circuit opened after {self._failures} failures")
            raise


@asynccontextmanager
async def db_transaction(pool):
    """Database transaction with automatic rollback."""
    conn = await pool.acquire()
    try:
        await conn.execute("BEGIN")
        yield conn
        await conn.execute("COMMIT")
    except Exception:
        await conn.execute("ROLLBACK")
        raise
    finally:
        await pool.release(conn)


# ── Observability ────────────────────────────────────────────────

def monitor(name: str = ""):
    """Monitor function execution time and errors."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(f"{name or func.__name__}: {elapsed*1000:.1f}ms")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(f"{name or func.__name__} failed after {elapsed*1000:.1f}ms: {e}")
                raise
        return wrapper
    return decorator


# ── Graceful Shutdown ────────────────────────────────────────────

class GracefulShutdown:
    """Managed graceful shutdown with proper ordering."""
    
    def __init__(self):
        self._hooks: list[tuple[str, callable, int]] = []
        self._shutting_down = False
    
    def register(self, name: str, hook: callable, order: int = 10):
        self._hooks.append((name, hook, order))
    
    async def shutdown(self):
        self._shutting_down = True
        logger.info("Initiating graceful shutdown...")
        
        for name, hook, _ in sorted(self._hooks, key=lambda x: -x[2]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                    logger.info(f"Shutdown: {name} completed")
            except asyncio.TimeoutError:
                logger.warning(f"Shutdown: {name} timed out")
            except Exception as e:
                logger.error(f"Shutdown: {name} failed: {e}")
        
        logger.info("Graceful shutdown complete")


# ── Configuration ────────────────────────────────────────────────

@dataclass
class Settings:
    """12-factor app configuration from environment."""
    debug: bool = False
    database_url: str = ""
    redis_url: str = ""
    log_level: str = "INFO"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: list[str] = None
    jwt_secret: str = ""
    feature_flags: dict[str, bool] = None
    
    @classmethod
    def from_env(cls) -> "Settings":
        import os
        return cls(
            debug=os.getenv("DEBUG", "0") == "1",
            database_url=os.getenv("DATABASE_URL", ""),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_port=int(os.getenv("PORT", "8000")),
            api_workers=int(os.getenv("WORKERS", "4")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            feature_flags={
                "new_pipeline": os.getenv("FEATURE_NEW_PIPELINE", "0") == "1",
                "enhanced_search": os.getenv("FEATURE_ENHANCED_SEARCH", "0") == "1",
            },
        )
    
    def validate(self) -> None:
        """Validate critical settings."""
        errors = []
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        if not self.jwt_secret and not self.debug:
            errors.append("JWT_SECRET is required")
        if errors:
            raise ValueError("; ".join(errors))


# ── Health Checks ─────────────────────────────────────────────────

@dataclass
class HealthCheck:
    """Composite health check for microservice."""
    
    async def check_liveness(self) -> dict:
        return {"status": "alive", "timestamp": time.time()}
    
    async def check_readiness(self, deps: dict[str, callable]) -> dict:
        status = "healthy"
        checks = {}
        for name, check_fn in deps.items():
            try:
                async with asyncio.timeout(2):
                    await check_fn()
                checks[name] = "healthy"
            except Exception as e:
                checks[name] = f"unhealthy: {e}"
                status = "unhealthy"
        return {"status": status, "checks": checks}
    
    async def check_startup(self) -> dict:
        return {"status": "started", "timestamp": time.time()}
