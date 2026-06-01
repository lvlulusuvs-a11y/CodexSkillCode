# Platform Engineering Patterns

**Building internal developer platforms (IDP) that engineers actually want to use.**

---

## 1. Internal Developer Platform (IDP) Architecture

```python
"""Platform engineering patterns for Big Tech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PLATFORM_COMPONENTS = {
    "developer_portal": {
        "description": "Single pane of glass for developers",
        "tools": ["Backstage", "Port", "Humanitec"],
        "features": [
            "Service catalog",
            "Documentation",
            "API references",
            "Deployment status",
            "Cost tracking",
        ],
    },
    "ci_cd_pipelines": {
        "description": "Automated build, test, deploy",
        "tools": ["GitHub Actions", "GitLab CI", "Jenkins X"],
        "features": [
            "Standardized pipelines",
            "Security scanning",
            "Artifact management",
            "Environment promotion",
        ],
    },
    "environments": {
        "description": "On-demand ephemeral environments",
        "tools": ["Kubernetes", "Terraform", "Crossplane"],
        "features": [
            "Preview environments per PR",
            "Ephemeral test environments",
            "Production-like staging",
            "Auto-cleanup",
        ],
    },
    "observability": {
        "description": "Built-in monitoring and debugging",
        "tools": ["Grafana", "Prometheus", "Loki", "Tempo"],
        "features": [
            "Pre-built dashboards",
            "Standard alerts",
            "Distributed tracing",
            "Centralized logging",
        ],
    },
    "secrets_management": {
        "description": "Secure secrets handling",
        "tools": ["Vault", "AWS Secrets Manager", "External Secrets"],
        "features": [
            "Auto-rotation",
            "Audit logging",
            "Access control",
            "Encryption at rest",
        ],
    },
}
```

## 2. Golden Path (Paved Road)

```python
"""Golden path templates for common service types."""
from __future__ import annotations


GOLDEN_PATHS = {
    "crud_api": {
        "description": "RESTful CRUD API service",
        "stack": ["FastAPI", "PostgreSQL", "Redis", "Docker"],
        "template": "templates/fastapi/",
        "features": [
            "Health checks",
            "Structured logging",
            "JWT authentication",
            "Rate limiting",
            "API documentation (OpenAPI)",
            "Database migrations",
            "CI/CD pipeline",
        ],
    },
    "event_consumer": {
        "description": "Kafka event consumer service",
        "stack": ["FastAPI", "Kafka", "PostgreSQL", "Redis"],
        "template": "assets/boilerplate-event-driven.md",
        "features": [
            "Consumer group management",
            "Dead letter queue",
            "At-least-once processing",
            "Idempotent handlers",
            "Lag monitoring",
        ],
    },
    "batch_processor": {
        "description": "Scheduled batch processing service",
        "stack": ["Python", "PostgreSQL", "S3", "Airflow"],
        "features": [
            "Checkpoint recovery",
            "Error reporting",
            "Progress tracking",
            "Resource limits",
            "Data quality checks",
        ],
    },
    "cli_tool": {
        "description": "Command-line tool",
        "stack": ["Python", "Click/Typer", "httpx"],
        "template": "templates/cli/",
        "features": [
            "Argument validation",
            "Colored output",
            "Progress bars",
            "Config file support",
            "Auto-completion",
        ],
    },
}
```

## 3. Developer Experience (DX) Principles

```python
"""Developer Experience optimization."""
from __future__ import annotations


DX_PRINCIPLES = """
  1. Fast feedback loops (< 5 seconds for lint, < 2 minutes for tests)
  2. Easy local development (docker-compose up = full stack)
  3. Predictable deployments (same process every time)
  4. Self-service (no tickets for common operations)
  5. Transparent (everything is measurable and visible)
  6. Opinionated but flexible (golden paths with escape hatches)
  7. Gradual complexity (simple by default, power when needed)
"""


DEV_PRODUCTIVITY_METRICS = """
  Lead Time: Code committed → Deployed to production
    Target: < 1 hour
    Measurement: Time from merge to deploy
  
  Deployment Frequency:
    Target: Multiple times per day
    Measurement: Deploy events per day
  
  Change Failure Rate:
    Target: < 5%
    Measurement: Failed deploys / total deploys
  
  Mean Time to Recovery (MTTR):
    Target: < 1 hour
    Measurement: Time from incident to resolution
  
  Developer Satisfaction:
    Target: NPS > 50
    Measurement: Quarterly developer survey
"""


@dataclass
class DeveloperPortal:
    """Internal Developer Portal features."""
    
    capabilities = [
        "Service catalog (all microservices with metadata)",
        "API documentation (auto-generated from OpenAPI specs)",
        "Deployment history (who deployed what, when)",
        "Resource costs (per service, per environment)",
        "On-call schedules (who's responsible)",
        "Runbooks (how to handle common issues)",
        "Scorecards (compliance, security, best practices)",
        "Templates (create new service in 5 minutes)",
    ]
```

## 4. Platform Team Topologies

```python
"""Platform team structures that work."""
from __future__ import annotations


TEAM_TOPOLOGIES = """
  Enabling Team:
    - Helps stream-aligned teams adopt new tech
    - Provides training, documentation, consulting
    - No ownership of production services
  
  Stream-Aligned Team:
    - Owns a service/product end-to-end
    - Can request platform services
    - Autonomous within platform boundaries
  
  Platform Team:
    - Builds and maintains the platform
    - Treats developers as customers
    - Measures success by developer productivity
    - Provides self-service capabilities
  
  Complicated-Subsystem Team:
    - Owns a technically complex component
    - Examples: payment engine, ML platform, auth
    - Small team of experts
"""


PLATFORM_TEAM_FOCUS = """
  Phase 1 (Foundation):
    - CI/CD pipeline
    - Container orchestration
    - Observability stack
    - Secrets management
  
  Phase 2 (Scale):
    - Self-service environments
    - Service templates
    - Developer portal
    - Cost management
  
  Phase 3 (Optimization):
    - Platform automation
    - Policy-as-code
    - Chaos engineering
    - Internal marketplace
"""
```

## 5. Service Templates & Scaffolding

```python
"""Service scaffolding automation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ServiceScaffolder:
    """Create new services from templates."""
    
    def scaffold(self, name: str, template: str, path: Path) -> None:
        """Create a new service from template."""
        # Create directory structure
        (path / name).mkdir(parents=True)
        (path / name / "src").mkdir()
        (path / name / "tests").mkdir()
        
        # Copy template files
        # Replace placeholders ({{service_name}}, etc.)
        # Initialize git repo
        # Install dependencies
        # Run initial tests
        pass
```

## 6. Internal Developer Loop

```python
"""Optimizing the inner development loop."""
from __future__ import annotations


INNER_LOOP = """
  Code → Build → Test → Debug → Repeat
  
  Target: < 5 seconds for complete loop
  Tools: 
    - watchexec (auto-restart on file changes)
    - pytest-watch (auto-run tests)
    - docker-compose (local dependencies)
    - Telepresence (connect local to remote cluster)
  
  Optimization:
    - Hot reload (uvicorn --reload)
    - Test selection (only run affected tests)
    - Lazy imports (import only what's needed)
    - Parallel test execution (pytest -n auto)
"""


@dataclass
class LocalDevEnvironment:
    """Containerized local development."""
    
    docker_compose = {
        "services": {
            "app": {"build": ".", "ports": ["8000:8000"]},
            "db": {"image": "postgres:16", "ports": ["5432:5432"]},
            "redis": {"image": "redis:7", "ports": ["6379:6379"]},
            "kafka": {"image": "confluentinc/cp-kafka:latest"},
        }
    }
```

## 7. Platform Metrics & SLAs

```python
"""Platform service level objectives."""
from __future__ import annotations


PLATFORM_SLOS = {
    "ci_pipeline": {
        "description": "CI pipeline duration",
        "target": "p95 < 10 minutes",
        "measurement": "Pipeline duration percentile",
    },
    "cd_pipeline": {
        "description": "Deploy to production",
        "target": "p95 < 5 minutes",
        "measurement": "Time from merge to production",
    },
    "environment_provision": {
        "description": "Ephemeral environment creation",
        "target": "p95 < 2 minutes",
        "measurement": "Time from request to ready",
    },
    "platform_uptime": {
        "description": "Platform components availability",
        "target": "> 99.9%",
        "measurement": "Uptime of CI/CD, portal, registry",
    },
    "secret_rotation": {
        "description": "Secret auto-rotation",
        "target": "< 1 hour for critical secrets",
        "measurement": "Time from rotation trigger to completion",
    },
}
```

## 8. Compliance & Governance

```python
"""Automated compliance and governance."""
from __future__ import annotations


POLICY_AS_CODE = """
  Automated checks:
    - License compliance (no GPL in production)
    - Dependency vulnerabilities (no critical CVEs)
    - Secret scanning (no hardcoded credentials)
    - Code quality (minimum coverage, max complexity)
    - Security scanning (SAST, DAST, container scan)
  
  Enforcement:
    - Block PR if policies fail
    - Exception process for justified violations
    - Regular compliance reports
    - Audit trail for all changes
"""


COMPLIANCE_CHECKLIST = """
  □ All secrets stored in vault (not in code)
  □ All dependencies scanned for CVEs
  □ All containers scanned for vulnerabilities
  □ All API endpoints authenticated
  □ All data encrypted at rest and in transit
  □ All access logged and auditable
  □ All changes tracked in version control
  □ All deployments approved by code review
  □ All incidents have postmortems
  □ All dependencies have licenses reviewed
"""


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
