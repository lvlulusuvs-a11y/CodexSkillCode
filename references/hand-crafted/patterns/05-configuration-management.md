# Конфигурация: ENV, YAML, Feature Flags

Ничто не бесит больше чем hardcoded константы и конфиги, разбросанные по 15 файлам. Вот как я организую конфигурацию.

## Уровни конфигурации

У меня три уровня, каждый для своего:

```yaml
# 1. config.yaml - базовые настройки (commit в git)
app:
  name: my-service
  port: 8080
  environment: development

database:
  max_connections: 20
  min_connections: 5
  timeout: 30s

redis:
  pool_size: 10
  ttl_default: 300

# 2. config.override.yaml - под окружение (в .gitignore)
database:
  url: postgresql://user:pass@prod-host:5432/db
redis:
  url: redis://prod-cache:6379
```

```bash
# 3. ENV variables - секреты (только в CI/CD secrets)
export DATABASE_PASSWORD=xxxx
export STRIPE_API_KEY=sk_xxx
export SENTRY_DSN=https://xxx@sentry.io/xx
```

## Код для загрузки

```python
from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml


@dataclass
class DatabaseConfig:
    url: str
    max_connections: int = 20
    min_connections: int = 5
    timeout: int = 30


@dataclass
class RedisConfig:
    url: str = "redis://localhost:6379"
    pool_size: int = 10
    ttl_default: int = 300


@dataclass
class AppConfig:
    name: str = "my-service"
    port: int = 8080
    environment: str = "development"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)

    @classmethod
    def load(cls) -> "AppConfig":
        config_path = Path("config.yaml")
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Оверрайд из окружения
        env = os.getenv("APP_ENV", "development")

        override_path = Path(f"config.{env}.yaml")
        if override_path.exists():
            with open(override_path) as f:
                override = yaml.safe_load(f)
                if override:
                    cls._deep_merge(data, override)

        config = cls._from_dict(cls, data)

        # Оверрайд из ENV переменных
        config.database.url = os.getenv("DATABASE_URL", config.database.url)
        config.database.password = os.getenv("DATABASE_PASSWORD", "")

        return config

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> None:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._deep_merge(base[key], value)
            else:
                base[key] = value
```

## Feature Flags

Feature flags должны быть отдельно от конфига приложения:

```python
@dataclass
class FeatureFlag:
    name: str
    enabled: bool = False
    rollout_percentage: int = 0

    def is_active(self, user_id: str | None = None) -> bool:
        if not self.enabled:
            return False
        if user_id and self.rollout_percentage < 100:
            return hash(f"{self.name}:{user_id}") % 100 < self.rollout_percentage
        return True
```

## Правила

1. Секреты - только в ENV или Vault
2. Несекретные настройки - YAML в git
3. Feature flags - отдельный сервис
4. Всё что меняется без деплоя - External config service
5. Default values всегда есть (чтобы сервис запустился без конфига)


## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation



## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation

