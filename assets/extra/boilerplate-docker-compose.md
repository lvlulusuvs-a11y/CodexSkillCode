# Docker Compose Boilerplate

## Development

```yaml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/app
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - app-network

  worker:
    build: .
    command: celery -A src.worker worker --loglevel=info
    volumes:
      - ./src:/app/src
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - app-network

  beat:
    build: .
    command: celery -A src.worker beat --loglevel=info
    volumes:
      - ./src:/app/src
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

  test:
    build: .
    command: pytest --cov=src --cov-report=term -v
    volumes:
      - ./src:/app/src
      - ./tests:/app/tests
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/app
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    profiles:
      - test
    networks:
      - app-network

volumes:
  pgdata:
  redis_data:

networks:
  app-network:
    driver: bridge
```

## Production (Docker Compose)

```yaml
version: "3.9"

services:
  app:
    image: ghcr.io/org/app:latest
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/app
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    deploy:
      placement:
        constraints: [node.role == manager]

secrets:
  db_password:
    external: true
```

## nginx.conf

```nginx
upstream app {
    server app:8000;
}

server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/static/;
        expires 30d;
    }
    
    location /health {
        proxy_pass http://app;
        proxy_connect_timeout 5s;
    }
}
```


## Production-Level Implementation

```python
"""Bonus: Production-ready pattern."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtendedImplementation:
    """Extended with error handling, logging, retry."""
    
    async def process(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(10):
                result = await self._execute()
                return result
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            raise
        except Exception:
            logger.exception("Processing failed")
            raise
