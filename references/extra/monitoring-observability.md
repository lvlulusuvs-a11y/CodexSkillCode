# Monitoring & Observability

**Как настроить observability в Python-проекте. Три столпа: логи, метрики, трейсинг.**

---

## 1. Structured Logging

### Почему print() не подходит
```python
# ❌ Плохо
print(f"User {user_id} created order {order_id}")

# ✅ Хорошо
logger.info("order_created", user_id=user_id, order_id=order_id, amount=total)
```

### loguru (простая альтернатива)

```python
from loguru import logger

# Настройка
logger.add(
    "logs/app.log",
    rotation="100 MB",      # новый файл при 100MB
    retention="30 days",    # хранить 30 дней
    compression="zip",      # архивировать старые
    level="INFO",
    format="{time} {level} {message} {extra}",
    serialize=True,         # JSON для отправки в систему сбора
)

# Использование
logger.info("User registered", user_id=42, source="web")

# Контекст
with logger.contextualize(request_id="abc123"):
    logger.info("Processing")  # request_id добавляется автоматически
```

### structlog (структурированное логирование)

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if DEBUG else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Контекст запроса
async def middleware(request, call_next):
    structlog.contextvars.bind_contextvars(
        request_id=uuid.uuid4().hex[:8],
        method=request.method,
        path=str(request.url),
    )
    return await call_next(request)

# Использование
logger.info("request_start", user_id=user.id)
```

## 2. Metrics (Prometheus)

### Установка
```bash
pip install prometheus-client
```

### Базовые метрики

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from prometheus_client import start_http_server

# Counter — счётчик (только увеличивается)
REQUESTS = Counter("http_requests_total", "Total HTTP requests", 
                   ["method", "endpoint", "status"])

# Histogram — распределение (latency, размер)
LATENCY = Histogram("http_request_duration_seconds", "Request latency",
                    ["method", "endpoint"],
                    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])

# Gauge — значение (текущее)
IN_FLIGHT = Gauge("http_requests_in_flight", "Current in-flight requests")
DB_CONNECTIONS = Gauge("db_connections_active", "Active DB connections")

# Использование в middleware
async def metrics_middleware(request, call_next):
    IN_FLIGHT.inc()
    start = time.perf_counter()
    
    try:
        response = await call_next(request)
        REQUESTS.labels(method=request.method, endpoint=str(request.url), 
                       status=response.status_code).inc()
        return response
    except Exception:
        REQUESTS.labels(method=request.method, endpoint=str(request.url),
                       status=500).inc()
        raise
    finally:
        IN_FLIGHT.dec()
        LATENCY.labels(method=request.method, endpoint=str(request.url)) \
               .observe(time.perf_counter() - start)
```

### RED метод (микросервисы)

```python
# Rate — запросов в секунду
rate = REQUESTS.labels(method="GET", endpoint="/users", status=200)
# Считаем: sum(rate[1m])
# Alert: rate > expected threshold

# Errors — ошибки в секунду  
errors = REQUESTS.labels(method="GET", endpoint="/users", status="5xx")
# Alert: errors / total > 1% за 5 минут

# Duration — время обработки
p99 = LATENCY.labels(method="GET", endpoint="/users")
# Alert: p99 > expected SLA
```

### USE метод (инфраструктура)

```python
# Utilization — загрузка
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage in %")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage in %")

# Saturation — насыщение
DB_POOL_WAIT = Gauge("db_pool_wait_seconds", "Time waiting for DB connection")

# Errors — ошибки
DB_ERRORS = Counter("db_errors_total", "Database errors")

# Системные метрики (psutil)
import psutil

async def collect_system_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent(interval=1))
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        DISK_USAGE.set(psutil.disk_usage("/").percent)
        await asyncio.sleep(15)
```

## 3. Distributed Tracing

```python
# OpenTelemetry — стандарт для трейсинга
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Настройка
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Использование
async def process_order(order_id: int) -> None:
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order_id", order_id)
        
        with tracer.start_as_current_span("validate_order") as child:
            result = await validate(order_id)
            span.set_attribute("valid", result)
        
        with tracer.start_as_current_span("charge_payment"):
            await charge(order_id)
```

## 4. Health Checks

```python
from fastapi import APIRouter
import redis.asyncio as aioredis

health_router = APIRouter()

@health_router.get("/health")
async def health():
    """Liveness probe — сервер жив."""
    return {"status": "alive"}

@health_router.get("/ready")
async def readiness():
    """Readiness probe — готов принимать трафик."""
    checks = {
        "database": await check_db(),
        "redis": await check_redis(),
        "storage": await check_storage(),
    }
    all_healthy = all(checks.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
    }

async def check_db() -> bool:
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_redis() -> bool:
    try:
        await redis.ping()
        return True
    except Exception:
        return False
```

## 5. Alert Rules

```yaml
# prometheus-rules.yml
groups:
  - name: python_app
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate ({{ $value | humanizePercentage }})"
      
      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency is {{ $value }}s"
      
      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
```

## 6. Log Aggregation

```yaml
# docker-compose.yml
version: '3'
services:
  app:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    labels:
      logging: "promtail"
  
  # Loki + Promtail (Grafana Stack)
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
  
  loki:
    image: grafana/loki:latest
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

## 7. Application Performance Monitoring (APM)

```python
# Sentry — ошибки и производительность
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% запросов трейсим
    environment="production",
    release="1.0.0",
)
```

## 8. Что мониторить в первую очередь

```python
# Критические метрики:
# 1. Error rate (5xx / total requests)
# 2. Latency p50, p95, p99
# 3. Request rate
# 4. Active users
# 5. Database connections
# 6. Queue depth
# 7. Cache hit ratio
# 8. Memory usage
# 9. CPU usage
# 10. Disk I/O

# Бизнес-метрики:
# 1. Registrations/day
# 2. Orders/minute 
# 3. Revenue/hour
# 4. Active users
# 5. Conversion rate
```


---

## Advanced Monitoring Patterns

### Custom Metrics

```python
"""Custom application metrics for monitoring."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class ApplicationMetrics:
    """Track application-level metrics."""
    _metrics: dict[str, Any] = field(default_factory=dict, init=False)
    
    def track_latency(self, operation: str, duration_ms: float) -> None:
        """Track operation latency."""
        key = f"latency.{operation}"
        if key not in self._metrics:
            self._metrics[key] = []
        self._metrics[key].append(duration_ms)
    
    def track_count(self, metric: str, value: int = 1) -> None:
        """Increment counter."""
        key = f"count.{metric}"
        self._metrics[key] = self._metrics.get(key, 0) + value
    
    def track_gauge(self, metric: str, value: float) -> None:
        """Set gauge value."""
        self._metrics[f"gauge.{metric}"] = value
    
    def snapshot(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        snapshot = {}
        for key, value in self._metrics.items():
            if key.startswith("latency."):
                if isinstance(value, list) and value:
                    sorted_vals = sorted(value)
                    n = len(sorted_vals)
                    snapshot[key] = {
                        "avg": sum(value) / n,
                        "p50": sorted_vals[int(n * 0.50)],
                        "p95": sorted_vals[int(n * 0.95)],
                        "p99": sorted_vals[int(n * 0.99)],
                        "count": n,
                    }
            else:
                snapshot[key] = value
        return snapshot


# Key metrics every service should expose:
REQUIRED_METRICS = {
    # RED metrics (Rate, Errors, Duration)
    "request_rate": "Requests per second",
    "error_rate": "Error percentage",
    "latency_p50": "Median latency",
    "latency_p99": "99th percentile latency",
    
    # USE metrics (Utilization, Saturation, Errors)
    "cpu_utilization": "CPU usage %",
    "memory_utilization": "Memory usage %",
    "connection_pool_usage": "DB pool utilization %",
    "queue_depth": "Message queue depth",
    
    # Business metrics
    "active_users": "Currently active users",
    "orders_per_second": "Order throughput",
    "cache_hit_ratio": "Cache hit percentage",
}
```

### Structured Logging Best Practices

```python
"""Structured logging with context."""
from __future__ import annotations

import structlog
from structlog.processors import JSONRenderer


def setup_structlog(service_name: str) -> None:
    """Configure structured logging with structlog."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Usage:
# logger = structlog.get_logger("my_service")
# logger.info("user.created", user_id=123, email="test@example.com")
```

### Health Check Best Practices

```python
"""Health check implementation patterns."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import time


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthEndpoint:
    """Standard health check endpoint.
    
    /health/live — Is the process alive? (livenessProbe)
    /health/ready — Can we serve traffic? (readinessProbe)
    /health/startup — Has the app started? (startupProbe)
    """
    
    dependencies: dict[str, Callable]
    
    async def check_liveness(self) -> dict:
        """Simple process health."""
        return {"status": "alive"}
    
    async def check_readiness(self) -> dict:
        """Check all dependencies."""
        status = HealthStatus.HEALTHY
        checks = {}
        
        for name, check_fn in self.dependencies.items():
            try:
                async with asyncio.timeout(2):
                    result = await check_fn()
                    checks[name] = {"status": "healthy"}
            except Exception as e:
                checks[name] = {"status": "unhealthy", "error": str(e)}
                status = HealthStatus.UNHEALTHY
        
        return {
            "status": status.value,
            "checks": checks,
            "timestamp": time.time(),
        }
```

### Observability Budget

```python
"""Observability overhead tracking."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ObservabilityBudget:
    """Track observability overhead.
    
    Rule: observability should consume < 5% of resources.
    """
    max_cpu_percent: float = 5.0
    max_memory_mb: float = 128.0
    max_latency_overhead_ms: float = 5.0
    max_logs_per_second: int = 1000
    
    _current_cpu: float = 0.0
    _current_memory: float = 0.0
    _current_latency: float = 0.0
    _logs_per_second: int = 0
    
    def check_budget(self, logger):
        if self._current_cpu > self.max_cpu_percent:
            logger.warning("Observability CPU budget exceeded")
        if self._current_memory > self.max_memory_mb:
            logger.warning("Observability memory budget exceeded")
```

### SLO Monitoring

```python
"""Service Level Objective monitoring."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SLO:
    """Service Level Objective tracking."""
    name: str
    target: float  # e.g., 0.9999 for 99.99%
    window: timedelta = timedelta(days=30)
    
    def calculate_burn_rate(self, current_sli: float) -> float:
        """Calculate error budget burn rate.
        
        > 1: burning too fast, will exhaust budget before window
        < 1: within budget
        """
        budget_remaining = 1 - current_sli
        budget_total = 1 - self.target
        if budget_total == 0:
            return 0
        return 1 - (budget_remaining / budget_total)


@dataclass
class SLOBudget:
    """Error budget management."""
    slos: list[SLO] = field(default_factory=list)
    _history: list[tuple[datetime, float]] = field(default_factory=list)
    
    def record_sli(self, time: datetime, sli: float) -> None:
        self._history.append((time, sli))
    
    @property
    def burn_rate(self) -> float:
        if not self._history:
            return 0
        current = self._history[-1][1]
        return sum(
            slo.calculate_burn_rate(current)
            for slo in self.slos
        ) / len(self.slos)
    
    def should_freeze_deploys(self, threshold: float = 0.8) -> bool:
        """Check if error budget is nearly exhausted."""
        return self.burn_rate > threshold
```


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
