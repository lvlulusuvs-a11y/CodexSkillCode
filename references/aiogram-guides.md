# Гайды по aiogram 3.x

Проверенные годами практики для Telegram ботов на aiogram 3.x.

---

## Гайд №1: Структура хендлеров

- Разбивай хендлеры по папке `handlers/`. Каждый файл — своя группа команд.
- В `__init__.py` импортируешь все роутеры.
- В главном файле `dp.include_routers()` из каждого модуля.
- Используй `FSMContext` через `StateGroup` с полями типа `str`.
- Вызов `state.clear()` обязателен после завершения сценария.

## Гайд №2: Работа с БД через asyncpg

- Ставь `asyncpg` и `pydantic`.
- Создавай пул соединений при старте бота: `await asyncpg.create_pool()`
- Пул передаёшь в хендлеры через `bot["db"]`
- Каждый запрос оборачивай в `async with pool.acquire() as conn:`
- Для миграций — отдельный скрипт с сырым SQL
- Не делай `fetchrow` там, где нужен `fetchval`
- Для вставки нескольких строк — `executemany()`

## Гайд №3: Логирование бота без распечаток

- Ставь `loguru`
- В корне создаёшь папку `logs`
- В коде: `logger.add("logs/бот_{time}.log", rotation="1 day", retention="7 days", level="DEBUG")`
- Убираешь все `print()`
- В продакшене level=`"INFO"`
- Ошибки лови через `@dp.errors()` и пиши `logger.exception()`
- Отдельный лог-файл под ошибки: `logger.add("logs/errors.log", level="ERROR")`

## Гайд №4: Конфиги через .env без слёз

- Ставь `pydantic-settings`
- Создавай класс `Settings` с полями: `BOT_TOKEN: str`, `ADMIN_IDS: list[int]`, `DB_URL: str`
- Метод `model_config = SettingsConfigDict(env_file=".env")`
- В админ-айдишники передавай строкой `123,456` и парси через `field_validator`
- В боте держи один объект `settings = Settings()` и импортируй везде оттуда

## Гайд №5: Middleware для антиспама без библиотек

- Пишешь класс `AntiSpamMiddleware(BaseMiddleware)`
- Внутри словарь `user_last_message: dict[int, float]`
- В `call` берёшь `event.from_user.id` и текущее время
- Если разница меньше 0.7 секунды — `return` без передачи дальше
- Словарь раз в минуту чистишь по ключам, у которых прошло >5 секунд
- Вешаешь через `dp.message.middleware()`

## Гайд №6: Парсинг команд с аргументами вручную

```python
@dp.message(Command("send"))
async def cmd_send(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("напиши что отправлять")
        return
    content = parts[1]
```

- Для нескольких аргументов режь через `shlex.split()` — работают кавычки
- Для чисел оборачивай в `try/except`

## Гайд №7: Рассылка без блокировки бота

- Достаёшь из БД список всех `user_id`
- Делишь на чанки по 30 штук
- В каждом чанке — `asyncio.gather()` для отправки
- Между чанками — `await asyncio.sleep(0.5)`
- Отправки оборачивай в `try/except`, выпавших юзеров — удалять из БД
- Процесс рассылки запускай отдельной таской: `asyncio.create_task()`
- Кнопку "остановить" — через флаг в БД

## Гайд №8: Регулярные задачи без костылей

- Ставь `apscheduler` с асинхронным триггером
- При старте бота создаёшь `AsyncIOScheduler()`
- Добавляешь задачу: `scheduler.add_job(функция, "interval", minutes=10, args=(bot,))`
- `args` передаёшь туда, куда нужно
- Не забываешь `scheduler.start()`
- Для задач по расписанию используй `cron` вместо `interval`
- Все исключения внутри задачи лови и логируй — иначе шедулер молча сдохнет
