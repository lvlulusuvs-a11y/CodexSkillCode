# Бойлерплейты для Telegram ботов на aiogram 3.x

> **Важно:** По умолчанию делай всё в одном файле (монокод), если пользователь
> не попросил «не монокод». Когда просит не монокод — разбивай как написано ниже.

---

## Бойлерплейт №1: Базовая структура (не монокод)

```
project/
├── bot.py                 # Точка входа
├── .env                   # BOT_TOKEN, ADMIN_IDS
├── config.py              # Pydantic настройки
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   └── admin.py
├── keyboards/
│   ├── __init__.py
│   └── reply.py
├── middlewares/
│   ├── __init__.py
│   └── antispam.py
├── states/
│   └── form.py
├── database/
│   ├── __init__.py
│   ├── db.py              # Пул подключений
│   └── queries.sql
└── utils/
    ├── logger.py
    └── helpers.py
```

## Бойлерплейт №2: Минимальный бот с FSM

Старт → регистрация имени → регистрация возраста → сохранение в БД → финиш.
- Три стейта: `waiting_name`, `waiting_age`, `confirm`
- Выход из любого стейта по команде `/cancel`
- Подтверждение — инлайн-кнопки "Да" и "Нет"

## Бойлерплейт №3: Команды админа с фильтрацией

- Фильтр `AdminFilter`, проверяющий `user_id` в списке из конфига
- `/broadcast` — рассылка всем юзерам с подтверждением
- `/stats` — количество юзеров в БД, активных за сутки, количество сообщений
- `/ban` и `/unban` с аргументом `@username` или `user_id`

## Бойлерплейт №4: Инлайн-режим

- Обработчик `@dp.inline_query()`
- Результаты — список из `InlineQueryResultArticle`
- Три предопределённых ответа с разными `id`
- Максимум 50 результатов
- `cache_time = 5`
- Работает в группах и личке без добавления бота

## Бойлерплейт №5: Платежи через Telegram Stars

- Обработчик `@dp.pre_checkout_query()`, внутри `await pre_checkout_query.answer(ok=True)`
- Обработчик `@dp.message(F.successful_payment)`
- В `successful_payment.invoice_payload` передаёшь ID товара
- После оплаты выдаёшь юзеру товар и логируешь транзакцию с `provider_payment_charge_id`

## Бойлерплейт №6: Вебхук вместо поллинга

```python
# Вместо start_polling:
await bot.set_webhook(url="https://domain.com/webhook")

# aiohttp app
app = web.Application()
app.router.post("/webhook", handle_webhook)

async def handle_webhook(request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response(status=200)

web.run_app(app, port=8443)  # SSL обязателен
```

## Бойлерплейт №7: Ротация сессий для нескольких аккаунтов

- Словарь `bots: dict[int, Bot]`
- В цикле создаёшь ботов по списку токенов
- Каждому — отдельный диспетчер
- Запуск: `asyncio.gather(*[dp.start_polling(bot) for bot in bots.values()])`
- Общие хендлеры подключаешь к каждому диспетчеру
- Разные хендлеры — через проверку `bot.id`

## Бойлерплейт №8: Пагинация списка (кнопки вперёд/назад)

- Одна инлайн-клавиатура с кнопками `◀️`, `▶️`, `❌`
- Хранишь номер страницы в `callback_data` через `PageCallback(CallbackData, prefix="page")`
- При нажатии пересчитываешь оффсет и редактируешь сообщение
- При достижении края списка кнопки становятся неактивными: `callback_button.disabled = True`


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
