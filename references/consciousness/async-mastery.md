# ⚡ Асинхронность: Не пиши asyncio, пока не прочитаешь это

Я видел больше убитого асинхронного кода, чем хотел бы. Люди пишут `async def` перед каждой функцией и думают, что код стал быстрым. Спойлер: **нет**.

## Когда async нужен, а когда нет

**Async нужен когда:**
- I/O-bound задачи (сеть, диск, БД)
- Много одновременных соединений (1000+)
- Real-time (WebSocket, long-polling)
- Микросервисная коммуникация

**Async НЕ нужен когда:**
- CPU-bound задачи (сортировки, вычисления, криптография)
- Простые CRUD на 10 пользователей
- Внутренние скрипты и утилиты

Если твой `async def` делает `await` только один раз — **он не асинхронный, он просто медленный**.

## Правило №1: Не блокируй event loop

Event loop — это один поток. Если ты его заблокировал — всё встало.

**Плохо:**
```python
async def handle_request(request):
    # CPU-bound операция на 5 секунд
    result = heavy_computation(request.data)  # ❌ Блокирует event loop!
    return Response(result)
```

Пока `heavy_computation` выполняется, **ни один другой запрос не обрабатывается**. Сервис мёртв на 5 секунд.

**Хорошо:**
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

async def handle_request(request):
    # CPU-bound операция в отдельном процессе
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, heavy_computation, request.data)
    return Response(result)
```

**Проверка:** Если ты когда-либо писал `time.sleep(n)` в асинхронной функции (а не `await asyncio.sleep(n)`) — ты блокировал event loop. Признай это и больше так не делай.

## Правило №2: Структурируй concurrency правильно

### Последовательное выполнение (медленно):
```python
async def fetch_all_users():
    users = []
    for uid in range(100):
        user = await fetch_user(uid)  # Каждый следующий ждёт предыдущего
        users.append(user)
    return users
# Total: 100 × 100ms = 10 секунд
```

### Конкурентное выполнение (быстро):
```python
async def fetch_all_users():
    tasks = [fetch_user(uid) for uid in range(100)]
    return await asyncio.gather(*tasks)
# Total: ~100ms (все запросы одновременно)
```

### Ограниченный конкурентный доступ (безопасно):
```python
import asyncio

async def fetch_all_users():
    sem = asyncio.Semaphore(10)  # Не больше 10 одновременных
    
    async def fetch_with_limit(uid):
        async with sem:
            return await fetch_user(uid)
    
    tasks = [fetch_with_limit(uid) for uid in range(100)]
    return await asyncio.gather(*tasks)
```

**Почему semaphore?**
- 100 одновременных HTTP запросов → connection pool overflow
- 100 одновременных запросов к БД → database connection exhaustion
- 100 одновременных запросов к внешнему API → rate limit

Semaphore защищает и тебя, и того, к кому ты обращаешься.

## Правило №3: Таймауты — это не опция, это обязательство

Любой `await` может подвиснуть навсегда.

**Плохо:**
```python
async def call_external_api(data):
    return await http_client.post("https://api.example.com", json=data)
# Если API упало — висим навсегда
```

**Хорошо:**
```python
async def call_external_api(data):
    try:
        async with asyncio.timeout(5.0):  # 5 секунд — и отваливаемся
            return await http_client.post("https://api.example.com", json=data)
    except asyncio.TimeoutError:
        logger.error("External API timeout after 5s")
        raise ServiceUnavailableError("payment service unavailable")
```

**Ещё лучше — с retry:**
```python
async def call_external_api_with_retry(data):
    last_error = None
    for attempt in range(3):
        try:
            async with asyncio.timeout(5.0):
                return await http_client.post("https://api.example.com", json=data)
        except asyncio.TimeoutError as e:
            last_error = e
            wait = (2 ** attempt) + random.uniform(0, 1)
            logger.warning("Attempt %d failed, retrying in %.2fs", attempt, wait)
            await asyncio.sleep(wait)
    
    raise ServiceUnavailableError(f"payment service failed after 3 retries: {last_error}")
```

Каждый `await` — это точка отказа. Каждая точка отказа должна иметь **таймаут**.

## Правило №4: Cancellation — это нормально

`asyncio.CancelledError` — не ошибка. Это сигнал «хватит, сворачивайся».

```python
async def background_task():
    try:
        while True:
            await do_work()
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Background task cancelled, cleaning up...")
        await cleanup()
        raise  # Важно: перевыбрасываем!
```

**Распространённая ошибка:**
```python
try:
    await long_operation()
except Exception:
    pass  # ❌ Перехватывает CancelledError вместе с остальными
```

`asyncio.CancelledError` наследуется от `BaseException`, не от `Exception`. Но всё равно будь аккуратен с голыми `except Exception`.

## Правило №5: Graceful shutdown — признак профессионализма

Сервис должен уметь **заканчивать** свою работу, а не обрываться.

```python
import signal
import asyncio
from contextlib import asynccontextmanager


class Server:
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._tasks: set[asyncio.Task] = set()
    
    async def start(self):
        """Запускает сервер с graceful shutdown."""
        loop = asyncio.get_running_loop()
        
        # Перехватываем сигналы
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._initiate_shutdown)
        
        # Запускаем фоновые задачи
        self._tasks.add(asyncio.create_task(self._healthcheck_loop()))
        self._tasks.add(asyncio.create_task(self._metrics_loop()))
        
        # Ждём сигнал к остановке
        await self._shutdown_event.wait()
        
        # Graceful shutdown
        logger.info("Shutting down gracefully...")
        
        # 1. Останавливаем приём новых запросов
        await self._stop_accepting_requests()
        
        # 2. Ждём завершения текущих запросов (максимум 30 секунд)
        pending = [t for t in self._tasks if not t.done()]
        if pending:
            await asyncio.wait_for(
                asyncio.gather(*pending, return_exceptions=True),
                timeout=30.0
            )
        
        # 3. Закрываем соединения
        await self._close_connections()
        
        logger.info("Shutdown complete.")
    
    def _initiate_shutdown(self):
        """Инициирует shutdown (вызывается из сигнала)."""
        logger.info("Received shutdown signal")
        self._shutdown_event.set()
    
    async def _healthcheck_loop(self):
        """Фоновая проверка здоровья."""
        try:
            while True:
                await asyncio.sleep(10)
                # ...
        except asyncio.CancelledError:
            pass
```

## Правило №6: Не миксуй sync и async без необходимости

```python
# Плохо: синхронная обёртка вокруг async
def get_user_sync(user_id: str) -> User:
    return asyncio.run(fetch_user(user_id))  # ❌ Создаёт новый event loop!
```

```python
# Плохо: async обёртка вокруг sync
async def get_user_async(user_id: str) -> User:
    return get_user_sync(user_id)  # ❌ Блокирует event loop!
```

```python
# Хорошо: либо sync, либо async — последовательно
async def get_user_async(user_id: str) -> User:
    return await fetch_user(user_id)
```

Если тебе нужно вызвать sync код из async — используй `run_in_executor`. Если async из sync — создай event loop на уровне приложения и используй его.

## Паттерн: Producer-Consumer на async

Это база для event-driven систем.

```python
import asyncio
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class EventBus:
    """Простая event bus на asyncio.Queue."""
    _queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=1000))
    _running: bool = False
    
    async def publish(self, event: dict) -> None:
        """Публикует событие."""
        if self._queue.full():
            logger.warning("Event bus queue full, dropping event: %s", event)
            return
        await self._queue.put(event)
    
    async def subscribe(self) -> AsyncIterator[dict]:
        """Подписка на события (бесконечный поток)."""
        self._running = True
        try:
            while self._running:
                try:
                    event = await asyncio.wait_for(
                        self._queue.get(), 
                        timeout=1.0
                    )
                    yield event
                    self._queue.task_done()
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            self._running = False
    
    def stop(self) -> None:
        self._running = False


# Использование
async def main():
    bus = EventBus()
    
    # Producer
    async def producer():
        for i in range(100):
            await bus.publish({"id": i, "data": f"event-{i}"})
            await asyncio.sleep(0.1)
    
    # Consumers
    async def consumer(name: str):
        async for event in bus.subscribe():
            logger.info("Consumer %s: %s", name, event)
    
    # Запуск
    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer())
        tg.create_task(consumer("alpha"))
        tg.create_task(consumer("beta"))
```

## Мои правила async-кода

1. Каждый `await` имеет таймаут
2. Каждый внешний вызов имеет retry
3. Нет `time.sleep()` — только `asyncio.sleep()`
4. Semaphore для конкурентных операций
5. Graceful shutdown для любого сервиса
6. TaskGroup для управления lifetime задач
7. CancelledError не глотать, пробрасывать
8. Асинхронные контекстные менеджеры для ресурсов
9. Не создавать event loop внутри запроса
10. Тестировать асинхронный код через `pytest-asyncio`

---

Async — это не магия. Это просто **другой паттерн** для работы с I/O. Если ты понимаешь event loop, таймауты и конкурентность — ты напишешь быстрый и надёжный код. Если нет — ты напишешь баги, которые воспроизводятся только под нагрузкой.
