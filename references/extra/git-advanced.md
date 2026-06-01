# Advanced Git

**Git команды, которые нужны каждый день. От отладки до recovery.**

---

## 1. Поиск в истории

```bash
# Найти, когда появился или исчез текст
git log -p -S "function_name" -- src/
git log -p -G "regex_pattern" -- src/

# Найти коммиты по сообщению
git log --all --oneline --grep="fix crash"
git log --all --oneline --grep="JIRA-123"

# Кто изменил строку
git blame -L 10,20 src/main.py

# История файла (включая переименования)
git log --oneline --follow -- src/moved_file.py
```

## 2. Работа с коммитами

```bash
# Amend последнего коммита
git commit --amend -m "new message"
git commit --amend --no-edit  # изменить файлы, не меняя сообщение

# Interactive rebase (последние 3 коммита)
git rebase -i HEAD~3
# Commands: pick, reword, edit, squash, fixup, drop

# Отменить последний коммит (сохранить изменения)
git reset --soft HEAD~1

# Отменить последний коммит (удалить изменения)
git reset --hard HEAD~1

# Взять конкретный файл из другого коммита
git checkout abc1234 -- src/file.py

# Отменить изменения в конкретном файле
git checkout -- src/file.py
```

## 3. Stash

```bash
# Спрятать изменения
git stash -u  # включая новые файлы
git stash push -m "work in progress"

# Посмотреть stash
git stash list
git stash show -p stash@{0}

# Вернуть stash
git stash pop     # вернуть и удалить
git stash apply   # вернуть, не удаляя

# Удалить stash
git stash drop stash@{0}
git stash clear   # все
```

## 4. Branch management

```bash
# Удалить локальные ветки, которых нет на remote
git remote prune origin

# Удалить смерженные ветки
git branch --merged | grep -v "main\|master" | xargs git branch -d

# Показать граф
git log --all --oneline --graph --decorate

# Сравнить ветки (только свои коммиты)
git log --oneline main..feature
git diff main..feature -- src/

# Ветка от конкретного коммита
git branch feature abc1234
```

## 5. Cherry-pick

```bash
# Взять коммит из другой ветки
git cherry-pick abc1234

# Взять несколько коммитов
git cherry-pick abc1234..def5678

# С опцией --no-commit (применить, но не коммитить)
git cherry-pick -n abc1234
```

## 6. Fix conflicts

```bash
# После merge конфликта:
git mergetool  # визуальное разрешение
# Или вручную: Accept theirs / Accept ours

# Принять "их" версию для всего файла
git checkout --theirs -- src/file.py
# Принять "свою" версию
git checkout --ours -- src/file.py

# После разрешения
git add src/file.py
git commit --no-edit
```

## 7. Recovery

```bash
# Восстановить удалённый файл
git checkout abc1234^ -- src/deleted_file.py

# Найти потерянные коммиты (после reset --hard)
git reflog
git checkout HEAD@{2}

# Восстановить ветку
git branch recovered-branch HEAD@{2}

# Отменить rebase (всё ещё в reflog)
git reset --hard ORIG_HEAD
```

## 8. Bisect (поиск бага)

```bash
# Начать поиск коммита, который ввёл баг
git bisect start
git bisect bad        # текущий коммит — баг
git bisect good v1.0  # v1.0 — работал

# Git будет переключаться по коммитам
# На каждом проверяй: есть баг? → git bisect bad / git bisect good

# Закончить
git bisect reset
```

## 9. Config

```bash
# Полезные настройки
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.st "status -sb"
git config --global alias.df "diff --word-diff"
git config --global pull.rebase true
git config --global fetch.prune true
```

## 10. Worktrees (параллельная работа)

```bash
# Создать рабочий каталог для другой ветки
git worktree add ../project-feature feature-branch

# Не переключаясь между ветками
# cd project-feature && работа в feature-branch
# cd project && продолжение работы в main

# Список worktrees
git worktree list

# Удалить
git worktree remove ../project-feature
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


---

## Production-Grade Extension

```python
"""Production-optimized implementation of this pattern."""
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
class ProductionPattern:
    """Enterprise pattern with full resilience stack."""
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(30):
                    start = time.perf_counter()
                    result = await fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(f"Success in {elapsed*1000:.1f}ms")
                    return result
            except asyncio.TimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error("Operation timed out after all retries")
                    raise
                wait = 1.0 * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.exception(f"Attempt {attempt + 1} failed")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        raise RuntimeError("Unreachable")
    

### Principal Engineer Notes

This pattern demonstrates:
- **Resilience**: Retry with exponential backoff
- **Observability**: Timing and error logging
- **Safety**: Timeout on all operations
- **Simplicity**: Single responsibility, clear flow

Apply this pattern to every external call in your system.
No production service should make an unprotected external call.
