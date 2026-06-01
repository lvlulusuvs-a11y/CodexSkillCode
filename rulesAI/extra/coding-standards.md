# Coding Standards

## Обязательно
- `from __future__ import annotations` — во всех файлах
- Type hints для всех функций и методов
- Docstrings для публичного API
- Максимум 100 символов на строку
- Функции не длиннее 60 строк

## Запрещено
- `except:` без типа исключения
- `print()` в production-коде (кроме cli.py)
- Магические числа без константы
- Хардкоженные токены/пароли
- `eval()` / `exec()`

## Именование
- `snake_case` — функции, переменные
- `PascalCase` — классы
- `UPPER_CASE` — константы
- `_private` — приватные методы/переменные

## Импорты
```python
# Порядок:
# 1. Стандартная библиотека
# 2. Третьесторонние
# 3. Локальные

import os
import sys
from typing import NamedTuple

import pytest
from pydantic import BaseModel

from mypackage import core
```

# Extended Coding Standards for Principal Engineers

## 5. Production Standards

### Error Handling
```python
# ✅ DO: Be specific with exception types
try:
    result = await risky_operation()
except ValueError as e:
    logger.warning("Validation failed", extra={"error": str(e)})
    return fallback_result
except (ConnectionError, TimeoutError) as e:
    logger.error("Service unavailable", extra={"error": str(e)})
    raise ServiceUnavailable from e
except Exception as e:
    logger.exception("Unexpected error")
    raise

# ❌ DON'T: Bare except or too broad
try:
    ...
except:
    pass  # Bad
```

### Logging
```python
# ✅ DO: Structured logging with context
logger.info("Order created", extra={
    "order_id": order.id,
    "user_id": user.id,
    "total": order.total,
    "items_count": len(order.items),
})

# ❌ DON'T: String interpolation
logger.info(f"Order {order.id} created")  # Bad — computed even if log level disabled
```

### Configuration
```python
# ✅ DO: Configuration from environment, validated at startup
settings = Settings.from_env()
settings.validate()

# ❌ DON'T: Hardcoded values, non-validated config
DATABASE_URL = "postgres://localhost:5432/db"  # Bad
```

### Async
```python
# ✅ DO: Proper async patterns
async with asyncio.timeout(30):
    async with pool.acquire() as conn:
        result = await conn.fetch(query)

# ❌ DON'T: Blocking calls in async
await asyncio.get_event_loop().run_in_executor(None, blocking_io)  # Acceptable if necessary
time.sleep(1)  # Bad — never in async code
```

## 6. Review Checklist Additions

### For Principal Engineers
- [ ] Is the solution over-engineered? (YAGNI)
- [ ] Are we solving the right problem?
- [ ] What's the cost of this decision? (maintenance, infra, complexity)
- [ ] Can a junior engineer maintain this?
- [ ] Is there monitoring for this feature?
- [ ] Can we rollback safely?
- [ ] Is the data model future-proof?
- [ ] Are there security implications?
- [ ] Does this affect SLOs?
- [ ] Is the documentation updated?
