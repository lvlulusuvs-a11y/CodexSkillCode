# Rate Limiting на практике

Rate limiting - это не про защиту от DDoS. Это про справедливость: чтобы один клиент не убил сервис для остальных.

## Алгоритмы

### Token Bucket - самый популярный

```python
import time
from dataclasses import dataclass

@dataclass
class TokenBucket:
    """Токен бакет: N запросов в секунду с burst."""

    rate: float        # Токенов в секунду (пополнение)
    burst: int         # Максимальный burst (размер бакета)

    tokens: float = 0
    last_refill: float = 0

    def allow(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
```

Простой и эффективный. rate = 100, burst = 200 - можно выдержать пик на 200 rps, потом стабилизироваться на 100.

### Sliding Window Log - точный, но дорогой

```python
class SlidingWindow:
    """Скользящее окно: N запросов за W секунд."""

    def __init__(self, redis, max_requests: int, window: int):
        self.redis = redis
        self.max = max_requests
        self.window = window

    async def allow(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window

        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window + 1)
        _, count, _, _ = await pipe.execute()

        return int(count) <= self.max
```

### Sliding Window Counter - balance между точностью и памятью

```python
class SlidingWindowCounter:
    """Счётчик скользящего окна через два счётчика."""

    async def allow(self, key: str, max_requests: int) -> bool:
        now = time.time()
        current_window = int(now / 60)
        previous_window = current_window - 1
        position_in_window = (now % 60) / 60

        current_count = await self.redis.get(f"{key}:{current_window}") or 0
        previous_count = await self.redis.get(f"{key}:{previous_window}") or 0

        weighted_count = previous_count * (1 - position_in_window) + current_count
        return weighted_count < max_requests
```

## На каких уровнях ставить

### Глобально (на весь сервис)
```python
global_limiter = TokenBucket(rate=1000, burst=2000)
# Защита от того что весь кластер ляжет
```

### На IP
```python
ip_limiter = SlidingWindow(redis, max_requests=100, window=60)
# 100 запросов в минуту с одного IP
```

### На пользователя
```python
user_limiter = SlidingWindow(redis, max_requests=1000, window=60)
# 1000 запросов в минуту от одного пользователя
```

### На endpoint
```python
endpoint_limiters = {
    "POST /api/login": TokenBucket(rate=5, burst=10),        # Защита от брутфорса
    "GET /api/health": TokenBucket(rate=100, burst=200),     # healthcheck - можно часто
    "POST /api/orders": TokenBucket(rate=50, burst=100),     # создание заказов
}
```

## Что возвращать

```python
async def rate_limit_middleware(request, call_next):
    key = request.client.host
    if not await rate_limiter.allow(key):
        retry_after = 60

        return Response(
            status_code=429,
            content=json.dumps({
                "error": "Too many requests",
                "retry_after": retry_after,
            }),
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after),
            },
        )

    return await call_next(request)
```

429 Too Many Requests + Retry-After header. Клиент знает когда можно повторить.

## Что я не rate-limit'ю

- Health checks (они должны всегда проходить)
- WebSocket upgrade (другая семантика)
- Internal service-to-service calls (они rate-limitятся на уровне клиента)


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

