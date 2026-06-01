# Middleware: Что должно быть в каждом сервисе

Middleware - это первый и последний слой защиты. Вот минимальный набор, который я добавляю в каждый HTTP сервис.

## Request ID

```python
import uuid
from time import monotonic

async def request_id_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

Каждый запрос имеет уникальный ID. Можно трейсить через все сервисы.

## Request Logging

```python
async def logging_middleware(request, call_next):
    start = monotonic()
    response = await call_next(request)
    duration_ms = (monotonic() - start) * 1000

    logger.info("request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
        request_id=request.state.request_id,
        user_agent=request.headers.get("user-agent", ""),
    )
    return response
```

Каждый запрос залогирован. Можно считать latency, errors, usage patterns.

## Error Handler

```python
async def error_handler_middleware(request, call_next):
    try:
        return await call_next(request)
    except NotFoundError as e:
        return JSONResponse({"error": str(e), "code": "NOT_FOUND"}, status=404)
    except ValidationError as e:
        return JSONResponse({"error": str(e), "code": "VALIDATION"}, status=400)
    except AuthError as e:
        return JSONResponse({"error": str(e), "code": "UNAUTHORIZED"}, status=401)
    except ExternalServiceError as e:
        logger.error("External service error", service=e.service, detail=str(e))
        return JSONResponse({"error": "Service unavailable"}, status=503)
    except Exception as e:
        logger.critical("Unhandled exception", error=str(e), exc_info=True)
        return JSONResponse({"error": "Internal server error"}, status=500)
```

Единая точка обработки всех ошибок. Никаких try/except в каждом хендлере.

## Metrics

```python
async def metrics_middleware(request, call_next):
    start = monotonic()
    response = await call_next(request)
    duration = monotonic() - start

    REQUEST_TOTAL.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        path=request.url.path,
    ).observe(duration)

    return response
```

RED метрики на каждый запрос.

## CORS

```python
async def cors_middleware(request, call_next):
    if request.method == "OPTIONS":
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Max-Age": "86400",
            }
        )

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
```

## Security Headers

```python
async def security_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

## Rate Limiter

```python
import time

class RateLimiter:
    def __init__(self, redis, max_requests: int = 100, window: int = 60):
        self.redis = redis
        self.max = max_requests
        self.window = window

    async def check(self, key: str) -> bool:
        now = int(time.time())
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - self.window)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window + 1)
        _, count, _, _ = await pipe.execute()
        return int(count) < self.max
```

## Порядок

```python
app.add_middleware(RequestIDMiddleware)    # 1 - создаёт request_id
app.add_middleware(LoggingMiddleware)      # 2 - логирует каждый запрос
app.add_middleware(RateLimiterMiddleware)  # 3 - проверяет лимиты
app.add_middleware(SecurityMiddleware)     # 4 - ставит заголовки
app.add_middleware(CORSMiddleware)         # 5 - CORS
app.add_middleware(ErrorHandlerMiddleware) # 6 - ловит ошибки (последний)
app.add_middleware(MetricsMiddleware)      # 7 - метрики (перед ответом)
```

Порядок важен. Request ID должен быть доступен всем остальным middleware. Error handler - последний перед хендлером.


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

