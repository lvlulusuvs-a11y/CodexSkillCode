# Setting Up Monitoring for a Service

You cannot run a service without monitoring. Here is the minimum setup.

## The Four Golden Signals

1. Latency - how long does it take to respond?
2. Traffic - how many requests are coming in?
3. Errors - how many requests fail?
4. Saturation - how full is the service?

## Prometheus Metrics

Install prometheus_client and add metrics:

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

IN_FLIGHT = Gauge(
    "http_requests_in_flight",
    "Current requests being handled",
    ["method"]
)

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

## Middleware to Track Metrics

from time import monotonic

@app.middleware("http")
async def metrics_middleware(request, call_next):
    method = request.method
    path = request.url.path
    IN_FLIGHT.labels(method=method).inc()

    start = monotonic()
    try:
        response = await call_next(request)
        REQUEST_COUNT.labels(method=method, path=path, status=response.status_code).inc()
        return response
    except Exception:
        REQUEST_COUNT.labels(method=method, path=path, status=500).inc()
        raise
    finally:
        REQUEST_DURATION.labels(method=method, path=path).observe(monotonic() - start)
        IN_FLIGHT.labels(method=method).dec()

## Dashboard Panels

1. RPS by endpoint (line chart)
2. Latency p50, p95, p99 (line chart)
3. Error rate (line chart)
4. CPU/Memory (line chart)
5. Active requests (gauge)
6. Slowest endpoints (table)

## Alerting Rules

Alert when:
- Error rate > 1% for 5 minutes
- p99 latency > 500ms for 5 minutes
- Service down (no metrics for 1 minute)
- High memory (> 90% for 5 minutes)
- High CPU (> 80% for 10 minutes)

## Logging

Send structured logs to a central system:

import structlog

structlog.configure(processors=[
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_log_level,
    structlog.processors.JSONRenderer(),
])

logger = structlog.get_logger()

## Healthcheck Endpoint

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": monotonic() - start_time,
    }


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.
