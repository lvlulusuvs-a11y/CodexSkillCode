# Refactoring Recipes

**Пошаговые рецепты для типичных ситуаций. Каждый рецепт = проблема → диагноз → лечение.**

---

## 🔧 Рецепт 1: God Function (функция-монстр)

### Симптомы
- Функция > 60 строк
- Делает 3+ разных вещи
- Трудно назвать (если нужно "и" в имени — явный признак)
- Комментарии внутри тела

### Лечение: Extract Method + SRP

**До:**
```python
def process_order(order_id: int) -> dict:
    # Получить заказ
    order = db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    if not order:
        raise ValueError(f"Order {order_id} not found")
    
    # Проверить оплату
    payment = db.query(f"SELECT * FROM payments WHERE order_id = {order_id}")
    if not payment or payment["status"] != "confirmed":
        raise ValueError("Payment not confirmed")
    
    # Рассчитать скидку
    discount = 0
    if order["total"] > 1000:
        discount = order["total"] * 0.1
    elif order["total"] > 500:
        discount = order["total"] * 0.05
    
    # Применить скидку
    final_total = order["total"] - discount
    
    # Обновить заказ
    db.query(f"UPDATE orders SET total = {final_total} WHERE id = {order_id}")
    
    # Отправить уведомление
    send_email(order["user_email"], f"Order {order_id} processed", f"Total: {final_total}")
    
    return {"order_id": order_id, "total": final_total, "discount": discount}
```

**После:**
```python
def process_order(order_id: int) -> ProcessResult:
    order = _get_order(order_id)
    _ensure_payment_confirmed(order_id)
    discount = _calculate_discount(order.total)
    final_total = order.total - discount
    _update_order_total(order_id, final_total)
    _notify_user(order.user_email, order_id, final_total)
    return ProcessResult(order_id=order_id, total=final_total, discount=discount)

def _get_order(order_id: int) -> Order:
    if not (order := order_repo.get(order_id)):
        raise NotFoundError(f"Order {order_id} not found")
    return order

def _ensure_payment_confirmed(order_id: int) -> None:
    if not payment_repo.is_confirmed(order_id):
        raise PaymentError(f"Payment for order {order_id} not confirmed")

def _calculate_discount(total: float) -> float:
    match total:
        case t if t > 1000: return t * 0.10
        case t if t > 500:  return t * 0.05
        case _: return 0.0

def _update_order_total(order_id: int, total: float) -> None:
    order_repo.update_total(order_id, total)

def _notify_user(email: str, order_id: int, total: float) -> None:
    notification_service.send(email, f"Order {order_id} processed", f"Total: {total}")
```

### Проверка
- [ ] Каждая функция делает одну вещь
- [ ] Все функции < 10 строк
- [ ] Имена читаются без комментариев
- [ ] Легко тестировать каждую часть отдельно

---

## 🔧 Рецепт 2: Deep Nesting (глубокая вложенность)

### Симптомы
- if внутри for внутри with внутри try
- Уровень вложенности > 3
- Код похож на ёлку

### Лечение: Early Return + Guard Clauses + Reverse Condition

**До:**
```python
def process_user(user_id: int, data: dict | None) -> str | None:
    if user_id > 0:
        user = db.get_user(user_id)
        if user:
            if data:
                if "name" in data:
                    user.name = data["name"]
                    db.save(user)
                    return "updated"
                else:
                    return "no_name"
            else:
                return "no_data"
        else:
            return "not_found"
    else:
        return "invalid_id"
```

**После:**
```python
def process_user(user_id: int, data: dict | None) -> str | None:
    if user_id <= 0:
        return "invalid_id"
    
    if not (user := db.get_user(user_id)):
        return "not_found"
    
    if not data:
        return "no_data"
    
    if "name" not in data:
        return "no_name"
    
    user.name = data["name"]
    db.save(user)
    return "updated"
```

### Правило: если есть `else` после `return`/`raise` — удали else

---

## 🔧 Рецепт 3: Switch-on-Type (код, зависящий от типа)

### Симптомы
- Цепочка `if isinstance()` или match на тип
- Добавление нового типа требует правки всех if-ов
- Запах: OCP violation (открыт для модификации, закрыт для расширения)

### Лечение: Polymorphism + Strategy Pattern

**До:**
```python
def export_report(report: Report, format: str) -> str:
    if format == "csv":
        lines = []
        for row in report.data:
            lines.append(",".join(str(v) for v in row.values()))
        return "\n".join(lines)
    elif format == "json":
        return json.dumps(report.data, indent=2)
    elif format == "xml":
        result = ["<report>"]
        for row in report.data:
            result.append("  <row>")
            for k, v in row.items():
                result.append(f"    <{k}>{v}</{k}>")
            result.append("  </row>")
        result.append("</report>")
        return "\n".join(result)
    else:
        raise ValueError(f"Unknown format: {format}")
```

**После:**
```python
from abc import ABC, abstractmethod
from typing import Any

class Exporter(ABC):
    @abstractmethod
    def export(self, data: list[dict[str, Any]]) -> str: ...

class CSVExporter(Exporter):
    def export(self, data: list[dict[str, Any]]) -> str:
        lines = [",".join(str(v) for v in row.values()) for row in data]
        return "\n".join(lines)

class JSONExporter(Exporter):
    def export(self, data: list[dict[str, Any]]) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)

class XMLExporter(Exporter):
    def export(self, data: list[dict[str, Any]]) -> str:
        rows = "\n".join(
            "  <row>\n" + "\n".join(f"    <{k}>{v}</{k}>" for k, v in row.items()) + "\n  </row>"
            for row in data
        )
        return f"<report>\n{rows}\n</report>"

# Фабрика
EXPORTERS: dict[str, type[Exporter]] = {
    "csv": CSVExporter,
    "json": JSONExporter,
    "xml": XMLExporter,
}

def export_report(report: Report, format: str) -> str:
    if exporter_cls := EXPORTERS.get(format):
        return exporter_cls().export(report.data)
    raise ValueError(f"Unknown format: {format}")
```

### Преимущества
- Новый формат = новый класс, без изменения export_report
- Каждый формат тестируется отдельно
- Можно добавить настройки через конструктор (CSVExporter(delimiter=";"))

---

## 🔧 Рецепт 4: Long Parameter List (много параметров)

### Симптомы
- Функция принимает 5+ параметров
- Часто параметры передаются группами
- Сигнатура не помещается на экране

### Лечение: Parameter Object + Dataclass

**До:**
```python
def create_user(name: str, email: str, phone: str, age: int, 
                country: str, city: str, street: str, house: str) -> User:
    ...
```

**После:**
```python
from dataclasses import dataclass

@dataclass
class Address:
    country: str
    city: str
    street: str
    house: str

@dataclass
class CreateUserRequest:
    name: str
    email: str
    phone: str
    age: int
    address: Address

def create_user(request: CreateUserRequest) -> User:
    ...
```

### Когда не надо
- Если параметры разнородны и не группируются → просто оставь
- Если функция внутренняя и редко вызывается → иногда OK

---

## 🔧 Рецепт 5: Mutable Default Arguments

### Симптомы
- `def func(items=[])` или `def func(config={})`
- Баги, которые воспроизводятся не всегда

### Лечение: None + Guard

**До:**
```python
def process(items: list[str] = []) -> list[str]:  # ОДИН список для всех вызовов!
    items.append("processed")
    return items
```

**После:**
```python
def process(items: list[str] | None = None) -> list[str]:
    items = items or []  # или items if items is not None else []
    items.append("processed")
    return items
```

---

## 🔧 Рецепт 6: Copy-Paste Code

### Симптомы
- 3+ одинаковых блока кода
- Исправляешь баг → надо править в 3 местах, забыл → баг живёт
- Параметры отличаются на 1-2 переменные

### Лечение: Extract + Parameterize

**До:**
```python
# В одном файле:
users = db.query("SELECT * FROM users WHERE active = 1")
user_names = [u["name"] for u in users]
user_names.sort()
for name in user_names[:10]:
    print(f"User: {name}")

# В другом файле:
admins = db.query("SELECT * FROM admins WHERE active = 1")
admin_names = [a["name"] for a in admins]
admin_names.sort()
for name in admin_names[:10]:
    print(f"Admin: {name}")
```

**После:**
```python
def get_active_names(table: str, label: str, limit: int = 10) -> None:
    rows = db.query(f"SELECT * FROM {table} WHERE active = 1")
    names = sorted(row["name"] for row in rows)
    for name in names[:limit]:
        print(f"{label}: {name}")

get_active_names("users", "User")
get_active_names("admins", "Admin")
```

### Правило трёх
1 раз — пиши inline
2 раза — задумайся
3 раза — вынеси в функцию

---

## 🔧 Рецепт 7: Global State (глобальные переменные)

### Симптомы
- `global x` в функциях
- Модульные переменные, которые меняются
- Тесты, которые зависят от порядка запуска

### Лечение: DI + Config Object

**До:**
```python
# config.py
DB_URL = "postgres://localhost:5432/db"
API_KEY = "secret"

# service.py
from config import DB_URL, API_KEY

def process() -> None:
    db = connect(DB_URL)  # не подменить в тестах
    ...
```

**После:**
```python
from dataclasses import dataclass, field
from functools import lru_cache

@dataclass
class Config:
    db_url: str = "postgres://localhost:5432/db"
    api_key: str = "secret"

class Service:
    def __init__(self, config: Config, db: Database | None = None) -> None:
        self._config = config
        self._db = db or Database(config.db_url)
    
    def process(self) -> None:
        # использует self._db и self._config
        pass

# Для тестов:
config = Config(db_url="sqlite:///:memory:")
service = Service(config, mock_db)
```

---

## 🔧 Рецепт 8: Nested Callbacks / Callback Hell

### Симптомы
- Асинхронный код с вложенными коллбеками (редко, но бывает)
- Цепочка `.then().then().catch()`

### Лечение: async/await

**До (гипотетический callback-style код):**
```python
def fetch_data(callback):
    api.get("/data", lambda resp: callback(resp.json()))
```

**После:**
```python
async def fetch_data() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get("/data") as resp:
            return await resp.json()
```

---

## Рецепт 9: Dead Code (мёртвый код)

### Симптомы
- Функции, которые никто не вызывает
- `if False:`
- Закомментированные блоки
- Переменные, которые никогда не читаются

### Лечение: DELETE. Просто delete.

```python
# ❌ Не надо:
def old_function():  # не используется, но вдруг пригодится
    ...

# ✅ Надо:
# Удали. Если понадобится — git restore.
```

### Исключения
- Публичное API библиотеки (backward compatibility)
- Код для миграции данных (пока миграция не завершена)

---

## Рецепт 10: Primitive Obsession (одержимость примитивами)

### Симптомы
- `user_id: int`, `email: str`, `status: str` (везде строки)
- Одна и та же валидация повторяется (проверка email в 10 местах)

### Лечение: Value Objects

**До:**
```python
def register_user(email: str, phone: str) -> None:
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email")
    if not phone.startswith("+") or len(phone) < 10:
        raise ValueError("Invalid phone")
    # ...
```

**После:**
```python
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self) -> None:
        if "@" not in self.value or "." not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

@dataclass(frozen=True)
class Phone:
    value: str
    
    def __post_init__(self) -> None:
        if not self.value.startswith("+") or len(self.value) < 10:
            raise ValueError(f"Invalid phone: {self.value}")

def register_user(email: Email, phone: Phone) -> None:
    # email и phone уже валидны
    pass
```

---

## 📊 Шпаргалка: Симптом → Рефакторинг

| Симптом | Рефакторинг | Сложность |
|---------|------------|-----------|
| Функция > 60 строк | Extract Method | ★☆☆ |
| Вложенность > 3 | Early Return, Guard Clauses | ★☆☆ |
| Много параметров | Parameter Object | ★☆☆ |
| Copy-paste | Extract + Parameterize | ★☆☆ |
| Switch-on-type | Strategy Pattern | ★★☆ |
| God class | Extract Class | ★★☆ |
| Глобальное состояние | Dependency Injection | ★★☆ |
| Примитивы везде | Value Objects | ★★☆ |
| Shotgun surgery | Move Field/Method | ★★★ |
| Divergent change | Extract Class/Separate Ways | ★★★ |
| Feature envy | Move Method | ★★★ |
| Message chain | Hide Delegate | ★★★ |
| Middle man | Remove Middle Man | ★☆☆ |
| Inappropriate intimacy | Change Bidirectional to Unidirectional | ★★★ |
| Alternative classes | Extract Superclass | ★★☆ |
| Large class | Extract Class/Interface | ★★☆ |
| Lazy class | Inline Class | ★☆☆ |
| Speculative generality | Collapse Hierarchy | ★☆☆ |
| Temporary field | Extract Class | ★★☆ |
| Data clump | Parameter Object | ★☆☆ |


---

## Production Expansion

### Real-World Example

```python
"""Production-grade implementation."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionExample:
    """Battle-tested pattern from Big Tech production."""
    
    async def execute(self) -> dict[str, Any]:
        """Execute with proper error handling, retry, and observability."""
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Operation timed out")
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise


### Key Takeaways for Principal Engineers

1. **Always add observability** — metrics, logs, traces
2. **Always handle errors** — don't let exceptions propagate silently
3. **Always set timeouts** — external calls should never hang forever
4. **Always think about scale** — what works for 10 req/s may fail at 1000
5. **Always document why** — the "why" is more important than the "what"
6. **Always test edge cases** — empty, None, max values, concurrent access
7. **Always consider rollback** — every deploy should be revertible
8. **Always plan for failure** — network, disk, memory, dependencies will fail

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| No timeouts | Hanging requests | Add timeout to all external calls |
| No retry | Transient failures become permanent | Add retry with backoff + jitter |
| No circuit breaker | Cascading failures | Add circuit breaker on dependencies |
| No health checks | k8s kills healthy pods | Add meaningful health endpoints |
| No rate limiting | Service overwhelmed | Add rate limiter per client |
| No graceful shutdown | Dropped requests | Proper SIGTERM handling |
| No connection pooling | DB connection exhaustion | Configure pool size, heartbeat |
| No caching | Repeated expensive computations | Multi-level caching with TTL |
| No feature flags | Rollbacks require full deploy | Feature flags for gradual rollout |
| No monitoring | Blind to production issues | RED metrics, SLOs, alerts |


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
