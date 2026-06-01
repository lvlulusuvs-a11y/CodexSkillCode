# FastAPI Template

```
app/
├── __init__.py
├── main.py          # entry point
├── routers/         # endpoints
├── models/          # pydantic
├── services/        # business logic
├── db/              # database
└── tests/
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My App", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

# Production Deployment

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Or with Docker
docker build -t my-service .
docker run -p 8000:8000 my-service
```

## Configuration
All configuration via environment variables (12-factor app):
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `LOG_LEVEL` — Logging level (DEBUG, INFO, WARNING, ERROR)
- `PORT` — HTTP server port (default: 8000)

## Health Checks
- `/health/live` — Liveness probe
- `/health/ready` — Readiness probe (checks dependencies)
- `/health/startup` — Startup probe

## Production Checklist
- [ ] Set all required environment variables
- [ ] Configure connection pool size
- [ ] Set up logging (JSON format for production)
- [ ] Add health check endpoints
- [ ] Configure graceful shutdown
- [ ] Set up monitoring (Prometheus metrics)
- [ ] Add rate limiting and circuit breakers
- [ ] Run security scan on dependencies
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## Monitoring
This service exposes:
- Prometheus metrics on `/metrics`
- Structured JSON logs
- OpenTelemetry-compatible tracing
- Health check endpoints

## Related References
See `references/extra/` in the mega-coding skill for:
- Production patterns (circuit breaker, retry, etc.)
- Database optimization
- Async patterns
- Monitoring and observability

## Extended Architecture

### Service Layer
```
src/
├── domain/           # Business entities and logic
├── use_cases/        # Application-specific business rules
├── repositories/     # Data access interfaces + implementations
├── services/         # External integrations
├── api/              # HTTP/gRPC handlers
├── middleware/       # Auth, logging, rate limiting
└── config/           # Configuration
```

### Production Features
- **Resilience**: Circuit breaker, retry with backoff, timeout
- **Observability**: Structured logging, metrics, health checks
- **Security**: Authentication, authorization, input validation
- **Operations**: Graceful shutdown, configuration management

### Dependencies
- Web framework (FastAPI/Fastify/Gin)
- Database ORM (SQLAlchemy/Prisma/GORM)
- Message queue (Kafka/RabbitMQ)
- Cache (Redis)
- Monitoring (Prometheus/Grafana)

### Deployment
- Docker containerization
- Kubernetes manifests
- CI/CD pipeline (GitHub Actions)
- Database migrations (Alembic)
- Feature flags for gradual rollout

### Monitoring
- Health check endpoints (/health/live, /health/ready)
- Prometheus metrics on /metrics
- Structured JSON logging
- OpenTelemetry tracing
- SLO-based alerting
