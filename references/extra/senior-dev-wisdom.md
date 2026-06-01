# Senior Dev Wisdom

**5 лет опыта, сжатые в один файл. То, что знает senior, но редко пишет.**

---

## I. Как думать о задачах

### Матрица оценки

| Вопрос | Junior спрашивает | Senior решает |
|--------|-------------------|---------------|
| "Сколько времени?" | "Дай подумать" | Оценка ±30% после 30с анализа |
| "Как писать?" | "Где пример?" | Выбор паттерна за 10с |
| "Что если ошибка?" | Напишет try/except | Спроектирует обработку |
| "А если поменяется?" | "Потом перепишу" | Выберет гибкое решение сейчас |
| "Где это положить?" | Создаст новый файл | Положит туда, где найдут |

### Как оценивать задачу (30-секундное сканирование)

```
Задача → (1) Что ДОЛЖНО измениться?
       → (2) Как узнать, что готово?
       → (3) Какой минимальный код?
       → (4) Какие edge cases?
       → (5) Что может сломаться?
```

Если не можешь ответить на (1) и (2) → задача не готова, переспроси.

### Решения: когда что выбирать

```python
# ─── ВЫБОР: исключение vs Result тип ────────────────────────────
# Исключение:     программист не может ничего сделать (нет файла, нет БД)
# Result/Option:  пользователь/ввод может быть невалидным (нет юзера, пустой список)

# ─── ВЫБОР: функция vs класс vs декоратор ──────────────────────
# Функция:        одна операция, нет состояния
# Класс:          состояние + методы, разные конфигурации
# Декоратор:      сквозная логика (логирование, кэш, таймаут)
# Генератор:      ленивая последовательность, бесконечные данные
# Контекст-мен:   ресурс с setup/teardown

# ─── ВЫБОР: sync vs async ───────────────────────────────────────
# Async:          I/O-bound, много соединений, долгие запросы
# Sync:           CPU-bound, простые скрипты, CLI утилиты
# Multiprocessing: CPU-bound, тяжелые вычисления

# ─── ВЫБОР: монолит vs микросервисы ─────────────────────────────
# Монолит:        команда <10 чел, один домен, стартап
# Микросервисы:   команда >10 чел, несколько доменов, разные темпы релиза
# К сведению:     90% проектов не нуждаются в микросервисах
```

## II. Что отличает production-код от pet-проекта

### 1. Работа с конфигами

```python
# ✅ Production
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Читает из .env, переменных окружения, с валидацией
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str  # Обязательный, из .env/окружения

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()  # Один раз, глобально
```

### 2. Логирование

```python
# ✅ Production: структурированное логирование с контекстом
import structlog  # или loguru

logger = structlog.get_logger()

# Вместо print() — везде logger
logger.info("user_created", user_id=user.id, source="registration")

# Уровни: DEBUG (dev), INFO (штатные события), 
#         WARNING (подозрительно), ERROR (сбой), CRITICAL (система падает)
```

### 3. Обработка ошибок — слои

```python
# Слой 1: На границе системы (API/CLI) — поймать всё, отдать понятный ответ
# Слой 2: В сервисах — специфичные исключения
# Слой 3: В репозиториях — только DB-specific ошибки

# Слой 1 (контроллер/хендлер)
async def handler(request):
    try:
        result = await service.process(request.data)
        return Response(result, status=200)
    except NotFoundError as e:
        return Response({"error": str(e)}, status=404)
    except ValidationError as e:
        return Response({"error": str(e)}, status=422)
    except Exception as e:
        logger.exception("unhandled error")  # logger.exception() включает traceback
        return Response({"error": "internal error"}, status=500)

# Слой 2 (сервис)
class UserService:
    async def get(self, user_id: int) -> User:
        if user := await self.repo.get(user_id):
            return user
        raise NotFoundError(f"User {user_id} not found")
```

### 4. Graceful Shutdown

```python
import asyncio, signal

async def main() -> None:
    # Создать ресурсы
    db = await asyncpg.create_pool(settings.database_url)
    server = await asyncio.start_server(...)
    
    # Ждать сигнала завершения
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)
    
    await stop.wait()
    
    # Graceful shutdown (порядок важен: сначала сервер, потом зависимости)
    server.close()
    await server.wait_closed()
    await db.close()
```

### 5. Rate limiting и Retry

```python
from asyncio import sleep
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """Декоратор с exponential backoff."""
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_error = None
            wait = delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await sleep(wait)
                        wait *= backoff  # 1s → 2s → 4s
            raise last_error  # type: ignore
        return wrapper
    return decorator
```

## III. Типичные грабли (и как не наступить)

### SQL Injection (да, это до сих пор актуально)
```python
# ❌ Никогда
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ Всегда
query = "SELECT * FROM users WHERE name = $1"
await conn.fetch(query, user_input)  # драйвер экранирует сам
```

### Race Condition
```python
# ❌ Гонка: два запроса одновременно прочитают count, оба прибавят 1
user.balance += amount  
await session.commit()

# ✅ Атомарно
await session.execute(
    update(User).where(User.id == uid).values(
        balance=User.balance + amount  # SQL делает атомарно
    )
)

# Или через asyncio.Lock
async with lock:
    user = await session.get(User, uid)
    user.balance += amount
    await session.commit()
```

### N+1 запросов
```python
# ❌ N+1: для каждого user отдельный запрос к orders
users = await session.execute(select(User))
for user in users.scalars():
    orders = await session.execute(select(Order).where(Order.user_id == user.id))

# ✅ Один запрос с join
stmt = select(User).options(selectinload(User.orders))
users = await session.execute(stmt)
```

### Мьютеблющие объекты в asyncio
```python
# ❌ Ужас: блокирует весь event loop
await some_sync_http_library.get(url)  # синхронная библиотека

# ✅ async библиотека
async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        data = await resp.json()

# Если нет async библиотеки:
data = await asyncio.to_thread(sync_library.get, url)  # в отдельном потоке
```

## IV. Коммуникация и процесс

### Как отвечать на баг-репорт
1. ✅ "Можешь дать шаги воспроизведения?"
2. ✅ "На каком окружении?"
3. ✅ "Сколько раз смог воспроизвести?"
4. ❌ "У меня работает" — это не ответ, это начало расследования
5. ❌ "Странно" — всегда есть причина

### Как ревьюить код
1. **Сначала архитектура**: правильный ли паттерн?
2. **Потом логика**: есть ли баги?
3. **Потом стиль**: читаемо? тесты есть?
4. Не придирайся к мелочам (пробелы, формат — это работа линтера)
5. Если замечание исправить дольше, чем оно стоит — пропусти
6. Вопрос вместо утверждения: "А что если пользователь передаст None?" VS "Ты не обработал None"

### Как оставлять код (для себя через 6 месяцев)
1. Если функция >30 строк — разбей
2. Если файл >500 строк — вынеси часть
3. Если функция делает две вещи — раздели
4. Имена переменных: длина пропорциональна области видимости
   - `i`, `j` — только в однострочном цикле
   - `user`, `order` — в функции
   - `app_config`, `database_url` — глобально

## V. Инструментальные привычки

```bash
# Узнать, кто написал строку
git blame -L 42,50 src/main.py

# Найти, когда появился/исчез текст
git log -p -S "specific_function_name" -- src/

# Найти коммиты по сообщению
git log --all --oneline --grep="fix crash"

# Увидеть эволюцию файла
git log --oneline --follow -- src/main.py

# Сравнить ветки (только свои коммиты)
git log --oneline main..feature

# Откатить один файл до определённого коммита
git checkout abc1234 -- src/broken.py
```

## VI. Ментальные модели

### Закон Хофштадтера
> "Всё всегда занимает больше времени, чем ожидается, даже если учесть закон Хофштадтера."

Умножай свою оценку на 2-3. Серьёзно.

### Принцип Парето (80/20)
80% результата = 20% усилий. 
- 20% фич приносят 80% бизнес-ценности
- 20% кода содержит 80% багов
- Фокусируйся на тех 20%, остальное — "достаточно хорошо"

### Оккам
> "Не множь сущности без необходимости."

Самое простое решение, которое работает — обычно лучшее.

### Теорема Конвея
> "Система отражает структуру коммуникаций в организации, которая её создала."

Хочешь нормальную архитектуру? Наладь коммуникацию в команде.

### Cargo Cult Programming
Копирование паттернов без понимания, зачем они нужны.
- "Мы используем микросервисы, потому что Google так делает"
- "Нужно написать тесты coverage 100%"
- "Этот код плохой, там switch, надо паттерн стратегия"

Понимай, зачем ты что-то делаешь. Если не знаешь — спроси или не делай.

## VII. Продвинутый Python, который junior-ы не знают

### `__slots__` — меньше памяти, быстрее атрибуты
```python
class Point:
    __slots__ = ("x", "y")  # Нельзя добавить новые атрибуты
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
# Экономия ~50% памяти на тысячах объектов
```

### `__init_subclass__` — контроль наследования
```python
class PluginBase:
    _registry: dict[str, type["PluginBase"]] = {}
    
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._registry[cls.__name__] = cls
        # Автоматически регистрируем все подклассы
```

### `__set_name__` — дескрипторы для повторного использования
```python
class ValidatedField:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"  # _name в инстансе
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return getattr(obj, self.name)
    
    def __set__(self, obj: Any, value: Any) -> None:
        if not value:
            raise ValueError(f"{self.name[1:]} cannot be empty")
        setattr(obj, self.name, value)

class User:
    name = ValidatedField()
    
    def __init__(self, name: str) -> None:
        self.name = name  # вызывает ValidatedField.__set__
```

### `__match_args__` — поддержка match/case
```python
@dataclass
class Point:
    x: float
    y: float
    __match_args__ = ("x", "y")

match point:
    case Point(0, 0): print("origin")
    case Point(x, y): print(f"{x}, {y}")
```

### `contextlib.contextmanager` — быстрый контекстный менеджер
```python
from contextlib import contextmanager

@contextmanager
def transaction(session):
    """Автоматический commit/rollback."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise

# Использование
async with transaction(db.session) as sess:
    sess.add(new_user)
    # если здесь ошибка → rollback, иначе commit
```

### `functools.singledispatch` — перегрузка функций
```python
from functools import singledispatch

@singledispatch
def serialize(obj: Any) -> str:
    raise NotImplementedError(f"No serializer for {type(obj)}")

@serialize.register
def _(obj: User) -> str:
    return f"User(id={obj.id}, name={obj.name})"

@serialize.register
def _(obj: Order) -> str:
    return f"Order(id={obj.id}, amount={obj.amount})"

# serialize(user) → автоматически выбирает нужный регистр
```

### `weakref` — борьба с циклическими ссылками
```python
import weakref

class Cache:
    def __init__(self) -> None:
        self._data: weakref.WeakValueDictionary[int, ExpensiveObject] = weakref.WeakValueDictionary()
    
    def get(self, key: int) -> ExpensiveObject | None:
        return self._data.get(key)  # объект удалится, если на него нет ссылок
```

## VIII. Рефакторинг: когда стоп-сигнал

Немедленно рефактори, если видишь:

1. **Функция > 60 строк** → разбей на 2-3 функции
2. **Файл > 1000 строк** → вынеси модули
3. **Вложенность > 3** → ранний return, extract method
4. **God object** → класс, который делает всё → раздели
5. **Shotgun surgery** → чтобы изменить одну вещь, надо править 10 файлов
6. **Copy-paste > 3 строк** → вынеси в функцию
7. **Magic number** → `if status == 3:` → `if status == OrderStatus.SHIPPED:`
8. **`//` TODO в коде** → TODO, которые висят > недели — технический долг

## IX. Fast Code Review Checklist (30s edition)

- [ ] **Понятно?** Если через 30с не понял — проси переписать
- [ ] **Работает?** Тесты есть? Тесты падают?
- [ ] **Опасно?** SQL injection? race condition? утечка памяти?
- [ ] **Хрупко?** Сломается от изменения входных данных?
- [ ] **Медленно?** N+1? лишние аллокации? блокирующий вызов?
- [ ] **Избыточно?** Есть ли более простое решение?

## X. Аксиомы (не обсуждается)

1. Тесты не опция. Тесты — спецификация.
2. Код читается в 10 раз чаще, чем пишется.
3. Если баг воспроизводится не всегда — это race condition, пока не доказано обратное.
4. "У меня работает" ≠ "система работает".
5. Комментарии врут. Код — единственная правда.
6. Быстрое и грязное решение живёт дольше, чем обещали.
7. Любая автоматизация окупается, если делать >3 раз.
8. Называть вещи — самая сложная задача в программировании.


---

## Battle-Tested Production Patterns

### Error Handling & Resilience

```python
"""Production-grade error handling patterns."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ResiliencePolicy:
    """Resilience policy for external service calls."""
    max_retries: int = 3
    timeout_seconds: float = 10.0
    circuit_breaker_failures: int = 5
    rate_limit_per_second: int = 100


async def resilient_call[T](
    fn: Any,
    *args: Any,
    policy: ResiliencePolicy | None = None,
    **kwargs: Any,
) -> T:
    """Execute call with retry, timeout, and circuit breaker."""
    policy = policy or ResiliencePolicy()
    
    for attempt in range(policy.max_retries + 1):
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                return await fn(*args, **kwargs)
        except asyncio.TimeoutError:
            if attempt == policy.max_retries:
                raise
            delay = 1.0 * (2 ** attempt)
            logger.warning(f"Timeout (attempt {attempt+1}), retrying in {delay}s")
            await asyncio.sleep(delay)
        except Exception as e:
            if attempt == policy.max_retries:
                raise
            logger.warning(f"Error (attempt {attempt+1}): {e}")
            await asyncio.sleep(1.0 * (2 ** attempt))
    
    raise RuntimeError("Should not reach here")


### Observability Best Practices

```python
"""Observability patterns for production."""
from __future__ import annotations

import time
import functools
from typing import Any, Callable


def observe(name: str = ""):
    """Decorator to add observability to any function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.info(
                    f"{name or func.__name__} completed",
                    extra={"duration_ms": elapsed * 1000},
                )
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start
                logger.error(
                    f"{name or func.__name__} failed",
                    extra={"duration_ms": elapsed * 1000, "error": str(e)},
                )
                raise
        return wrapper
    return decorator


### Configuration Management

```python
"""Type-safe configuration management."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceConfig:
    """Application configuration from environment."""
    
    # Service metadata
    service_name: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "app"))
    environment: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    
    # Database
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "1") == "1"
    
    # Cache
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))
    
    # API
    api_port: int = int(os.getenv("PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    
    # Feature flags
    enable_new_algo: bool = os.getenv("FEATURE_NEW_ALGO", "0") == "1"
    enable_debug_mode: bool = os.getenv("DEBUG", "0") == "1"
    
    def validate(self) -> None:
        """Validate config on startup."""
        errors = []
        if self.environment == "prod" and not self.database_url:
            errors.append("DATABASE_URL required in production")
        if self.environment == "prod" and "localhost" in (self.database_url or ""):
            errors.append("Cannot use localhost database in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"
    
    @property
    def is_debug(self) -> bool:
        return self.enable_debug_mode or self.environment == "dev"


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.


---

## More Production Wisdom from the Trenches

### On Code Reviews

```python
"""Code review wisdom from years of Big Tech experience."""
from __future__ import annotations

code_review_wisdom = """
  What I check in order of importance:
    1. Is the problem actually solved? (read the test first)
    2. Will this work in production? (error handling, timeouts, retries)
    3. Can my grandchild debug this at 3 AM? (logging, stack traces)
    4. Is this testable without 12 mocks? (DI, interfaces)
    5. Is the code clean? (naming, structure, duplication)
  
  Red flags in code review:
    - "I'll add error handling later" — no you won't
    - "This is just a quick fix" — all fixes start this way
    - "It works on my machine" — until it doesn't
    - "I didn't change that" — git blame says otherwise
    - "The tests pass" — do they test the right thing?
  
  What I look for in every PR:
    - Any TODO/FIXME comments (they never get done)
    - print() instead of logger (forgotten debug)
    - Bare except clauses (swallowing errors)
    - No error handling on external calls
    - Missing type hints on public APIs
    - Functions longer than 50 lines
"""


### On Technical Debt

debt_wisdom = """
  80% of the value comes from 20% of the code.
  
  Technical debt is like financial debt:
  - Some debt is good (business requires fast delivery)
  - Some debt is bad (sloppy code, no tests)
  - Some debt has high interest (core architecture)
  - Some debt is interest-free (unused features)
  
  Pay off debt strategically:
  - High interest, core paths → pay first
  - Low interest, rarely touched → leave for later
  - Everything else → track, prioritize quarterly
  
  The most expensive technical debt:
  1. No tests (you're afraid to change anything)
  2. Tight coupling (everything depends on everything)
  3. Global state (race conditions, flaky tests)
  4. Copy-paste (fix in one place, broken in 5 others)
  5. Magic numbers (what does 86400 mean?)
"""


### On Production Incidents

incident_wisdom = """
  Every production incident is a gift:
  - It shows you where your system is weak
  - It reveals assumptions that were wrong
  - It creates urgency to fix things
  - It builds team resilience
  
  The 5 stages of incident response:
  1. Denial: "It can't be our code, nothing changed"
  2. Anger: "Who deployed on Friday?!"
  3. Bargaining: "Maybe if we restart..."
  4. Depression: "We have to rollback..."
  5. Acceptance: "Let's fix the root cause"
  
  After every incident:
  - Write the postmortem within 48 hours
  - Focus on systems, not people (blameless)
  - Define 3 action items max (prioritize)
  - Track action items to completion
  - Share learnings with the wider team
"""


### On Career Growth

career_wisdom = """
  The path from Senior to Principal:
  
  Year 1-2 (Senior):
    - You can design and build systems alone
    - You review code effectively
    - You handle on-call without escalation
  
  Year 3-4 (Staff):
    - You influence multiple teams
    - You mentor senior engineers
    - You drive technical strategy
  
  Year 5+ (Principal):
    - You define technical direction for the org
    - You create frameworks others use
    - You change how engineering works
  
  What matters most:
    - Communication > Technical skill
    - Judgment > Speed
    - Simplicity > Cleverness
    - Impact > Activity
    - Relationships > Arguments
"""
