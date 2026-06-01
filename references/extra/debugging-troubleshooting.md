# Debugging & Troubleshooting

**Как находить и исправлять проблемы в Python-приложениях.**

---

## 1. Debugging Tools

```bash
# pdb (встроенный)
python -m pdb my_script.py
# В коде: import pdb; pdb.set_trace()

# ipdb (лучше pdb)
pip install ipdb
# В коде: import ipdb; ipdb.set_trace()

# breakpoint() (Python 3.7+, использует PYTHONBREAKPOINT)
breakpoint()  # в коде

# Удалённый дебаг (для серверов)
pip install debugpy
# python -m debugpy --listen 0.0.0.0:5678 --wait-for-client my_script.py
```

## 2. Common Errors & Solutions

### ModuleNotFoundError
```bash
# Проверить установку
pip list | grep mypackage

# Проверить PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"

# Виртуальное окружение
which python
python -m site

# Циклические импорты
# Разделить на module.py → types.py, logic.py
```

### ImportError
```python
# Relative imports вне пакета
# ❌ from . import module  # ImportError: attempted relative import with no known parent package
# ✅ python -m package.module (а не python module.py)
```

### SQLAlchemy Errors
```python
# DetachedInstanceError (объект вне сессии)
user = await session.get(User, 1)
await session.close()
print(user.name)  # ❌ DetachedInstanceError

# Решение: expire_on_commit=False
session = AsyncSession(engine, expire_on_commit=False)

# Или загрузить снова
user = await session.get(User, 1)
```

### Asyncio Errors
```python
# RuntimeError: Task <Task pending> got Future <Future pending>
# Причина: корутина не запущена
async def my_func(): ...
coro = my_func()  # ❌ не запущена
# await coro  # ✅

# RuntimeError: asyncio.run() cannot be called from a running event loop
# Решение: использовать asyncio.create_task() или await
async def main():
    await some_func()  # ✅
    # asyncio.run(other())  # ❌
```

### Memory Errors
```python
# MemoryError: не хватает памяти
# Решение 1: генераторы вместо списков
# ❌ all_data = [process(x) for x in huge_data]
# ✅ for x in huge_data: process(x)  # лениво

# Решение 2: __slots__
class Point:
    __slots__ = ("x", "y")
    ...

# Решение 3: gc.collect()
import gc
gc.collect()  # принудительная сборка мусора
```

### Deadlocks
```python
# asyncio deadlock: await внутри lock, который уже захвачен
async def example():
    async with lock:
        await another_func()  # ❌ если another_func тоже захватит lock — deadlock

# Решение: определить порядок блокировок
# Или использовать asyncio.Lock с таймаутом
try:
    await asyncio.wait_for(lock.acquire(), timeout=5.0)
except TimeoutError:
    logger.error("Deadlock detected!")
```

## 3. Performance Debugging

```bash
# CPU profile
python -m cProfile -s cumulative my_script.py | head -30

# Flamegraph
pip install py-spy
py-spy record -o flame.svg -- python my_script.py

# Memory
pip install memory_profiler
python -m memory_profiler my_script.py

# Line profiler
pip install line_profiler
kernprof -l -v my_script.py
```

## 4. Network Debugging

```bash
# Проверить DNS
nslookup api.example.com
dig api.example.com

# Проверить порт
nc -zv api.example.com 443
curl -v https://api.example.com/health

# TCP dump
tcpdump -i any port 80 -nn

# Трассировка
traceroute api.example.com

# HTTP запрос
curl -X POST https://api.example.com/data \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' \
  -v
```

## 5. Database Debugging

```sql
-- PostgreSQL
-- Текущие запросы
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Медленные запросы (если pg_stat_statements включён)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Блокировки
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid
FROM pg_locks blocked_locks
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype;

-- Размер таблиц
SELECT tablename, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

## 6. Docker Debugging

```bash
# Логи
docker logs --tail=100 -f container_name

# Войти в контейнер
docker exec -it container_name /bin/bash

# Ресурсы
docker stats

# Inspect
docker inspect container_name

# Copy файлы
docker cp container_name:/app/logs.txt ./logs.txt

# Сеть
docker network ls
docker network inspect bridge
```

## 7. Git Debugging

```bash
# Кто изменил строку
git blame -L 42,50 src/main.py

# Когда появился баг
git bisect start
git bisect bad HEAD
git bisect good v1.0
# Git переключает коммиты, проверяй баг → git bisect good/bad
git bisect reset

# Найти удалённый код
git log -p -S "deleted_function" -- src/

# Посмотреть что изменилось в коммите
git show abc1234
```

## 8. Monitoring Debugging

```python
# Health check endpoint
@app.get("/health")
async def health():
    db_ok = await check_db()
    redis_ok = await check_redis()
    return {
        "status": "healthy" if db_ok and redis_ok else "degraded",
        "checks": {
            "database": "ok" if db_ok else "failed",
            "redis": "ok" if redis_ok else "failed",
        },
    }

# Пошаговое логирование
async def process_order(order_id: int) -> None:
    logger.debug("Starting order processing", order_id=order_id)
    
    order = await get_order(order_id)
    logger.debug("Order fetched", order_id=order_id, status=order.status)
    
    await validate_payment(order)
    logger.debug("Payment validated", order_id=order_id)
```

## 9. Python Debugging Snippets

```python
# Смотреть типы и атрибуты
print(type(obj))
print(dir(obj))
print(vars(obj))

# Смотреть стек вызовов
import traceback
traceback.print_stack()

# Смотреть, сколько времени заняло
from time import perf_counter
start = perf_counter()
result = func()
print(f"Took {perf_counter() - start:.3f}s")

# Смотреть, сколько объектов
import sys
print(sys.getsizeof(large_list))
print(len(large_list))

# Смотреть ID объекта
print(id(obj))
print(obj is other)  # сравнение по ID
```

## 10. Когда всё остальное не помогает

```python
# 1. Проверь окружение
python --version
pip list | grep mypackage
echo $PYTHONPATH

# 2. Проверь права
ls -la /var/log/
whoami

# 3. Перезапусти
# Иногда помогает: systemctl restart myapp

# 4. Проверь логи
tail -f /var/log/app.log

# 5. Упрости воспроизведение
# Минимальный пример, который воспроизводит баг

# 6. Обнови зависимости
pip install --upgrade mypackage

# 7. Создай чистое окружение
python -m venv fresh_venv
source fresh_venv/bin/activate
pip install -r requirements.txt
```


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

## Enterprise Implementation Patterns

### Production-Grade Code

```python
"""Enterprise-grade implementation with full resilience."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools
import random

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class EnterpriseService:
    """Production service with all resilience patterns."""
    
    max_retries: int = 3
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    
    def __post_init__(self):
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time = 0.0
    
    async def call_with_resilience(
        self,
        fn: Callable[..., Awaitable[T]],
        fallback: Callable[..., Awaitable[T]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute with circuit breaker + retry + timeout."""
        if self._circuit_open:
            if time.monotonic() - self._last_failure_time < 30.0:
                if fallback:
                    return await fallback(*args, **kwargs)
                raise RuntimeError("Circuit breaker is open")
            self._circuit_open = False
            logger.info("Circuit breaker half-open, testing...")
        
        for attempt in range(self.max_retries + 1):
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    result = await fn(*args, **kwargs)
                    self._failure_count = 0
                    return result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout (attempt {attempt+1})")
                if attempt == self.max_retries:
                    self._record_failure()
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt) + random.uniform(0, 0.5))
            except Exception as e:
                logger.warning(f"Error (attempt {attempt+1}): {e}")
                if attempt == self.max_retries:
                    self._record_failure()
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        
        raise RuntimeError("Unreachable")
    
    def _record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self.circuit_breaker_threshold:
            self._circuit_open = True
            logger.error(f"Circuit breaker opened after {self._failure_count} failures")


### Configuration Management

@dataclass
class ServiceSettings:
    """Type-safe configuration from environment variables."""
    service_name: str = "my-service"
    environment: str = "dev"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = ""
    db_pool_min: int = 5
    db_pool_max: int = 20
    db_timeout: int = 5
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_default_ttl: int = 300
    
    # API
    port: int = 8000
    workers: int = 4
    cors_origins: list[str] = None
    
    # External services
    external_api_timeout: int = 10
    external_api_retries: int = 3
    
    # Feature flags
    enable_new_feature: bool = False
    
    def validate(self) -> None:
        """Validate configuration on startup."""
        errors = []
        if self.environment == "production":
            if not self.database_url:
                errors.append("DATABASE_URL is required")
            if self.debug:
                errors.append("Debug mode must be disabled in production")
            if "localhost" in (self.database_url or ""):
                errors.append("Cannot use localhost in production")
        if errors:
            raise ValueError("; ".join(errors))
    
    @classmethod
    def from_env(cls) -> "ServiceSettings":
        """Load configuration from environment variables."""
        import os
        return cls(
            service_name=os.getenv("SERVICE_NAME", "my-service"),
            environment=os.getenv("ENVIRONMENT", "dev"),
            debug=os.getenv("DEBUG", "0") == "1",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_url=os.getenv("DATABASE_URL", ""),
            db_pool_min=int(os.getenv("DB_POOL_MIN", "5")),
            db_pool_max=int(os.getenv("DB_POOL_MAX", "20")),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            port=int(os.getenv("PORT", "8000")),
            external_api_timeout=int(os.getenv("EXTERNAL_API_TIMEOUT", "10")),
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(","),
        )


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
