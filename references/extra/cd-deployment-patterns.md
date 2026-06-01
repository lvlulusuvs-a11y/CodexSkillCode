# CI/CD & Deployment Patterns

**Production deployment strategies, pipelines, and automation for Big Tech.**

---

## 1. Deployment Strategies

### Blue-Green Deployment

```yaml
# Blue-Green: Two identical environments, switch traffic
# Pros: Instant rollback, no downtime
# Cons: 2x infrastructure cost

deployment:
  strategy: blue-green
  
  blue:  # Current production
    replicas: 10
    version: v1.2.3
    
  green:  # New version
    replicas: 10
    version: v1.3.0
    
  switch:
    type: load-balancer  # Update DNS or LB target group
    canary: true         # Send 10% traffic first
    observation_period: 15m
    auto_rollback: true
```

### Canary Deployment

```yaml
# Canary: Gradually shift traffic to new version
# Pros: Risk reduction, A/B testing capability
# Cons: Longer rollout, complexity

deployment:
  strategy: canary
  
  stages:
    - percentage: 1%   # 1% of traffic
      duration: 5m
      metric_check: error_rate < 0.1%
      
    - percentage: 10%  # 10% of traffic
      duration: 10m
      metric_check: error_rate < 0.1% AND latency_p99 < 200ms
      
    - percentage: 50%
      duration: 15m
      metric_check: error_rate < 0.1% AND latency_p99 < 200ms
      
    - percentage: 100%  # Full rollout
      duration: 0
  
  rollback_conditions:
    - error_rate > 1% for 1m
    - latency_p99 > 500ms for 5m
    - any 5xx increase > 50%
```

### Rolling Update (k8s default)

```yaml
# Rolling: Replace pods one by one
# Pros: No extra resources, gradual
# Cons: Longer rollout, both versions run simultaneously

apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max extra pods during update
      maxUnavailable: 1  # Max unavailable pods
```

## 2. CI Pipeline (Production-Grade)

### GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      
      - name: Install
        run: pip install -e ".[dev]"
      
      - name: Lint
        run: |
          ruff check .
          ruff format --check .
      
      - name: Type Check
        run: mypy src/
      
      - name: Security
        run: |
          bandit -r src/ -x tests
          safety check
      
      - name: Test
        run: pytest -v --tb=short --cov=src --cov-report=xml
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage.xml
      
      - name: Quality Gate
        run: |
          python scripts/mega.py check src/
          python metrics/quality-metrics.py src/
      
      - name: Mega-Coding Trees
        run: python scripts/tree-voting/evaluate.py src/
  
  build:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker
        run: |
          docker build -t app:${{ github.sha }} .
          docker tag app:${{ github.sha }} app:latest
      
      - name: Push
        run: |
          docker push app:${{ github.sha }}
      
      - name: SBOM Generation
        run: |
          docker sbom app:${{ github.sha }} > sbom.json
          syft app:${{ github.sha }} -o spdx-json > spdx.json
```

## 3. CD Pipeline (Production-Grade)

### ArgoCD (GitOps)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
spec:
  destination:
    namespace: production
    server: https://kubernetes.default.svc
  source:
    repoURL: https://github.com/org/my-service
    path: k8s/overlays/production
    targetRevision: main
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ApplyOutOfSyncOnly=true
  sync:
    retry:
      limit: 3
      backoff:
        duration: 30s
        factor: 2
        maxDuration: 5m
```

### Feature Flag Automation

```python
"""Automated feature flag management in CI/CD."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeatureFlagPipeline:
    """Manage feature flags through deployment pipeline."""
    
    async def promote(self, flag_name: str, env: str) -> None:
        """Promote flag through environments."""
        stages = {
            "dev": 0.1,      # 10% in dev
            "staging": 0.5,  # 50% in staging
            "prod": 0.01,    # 1% in prod (canary)
        }
        
        percentage = stages.get(env, 1.0)
        await self.flags.set(flag_name, percentage)
        
        # Wait for observability
        await asyncio.sleep(300)  # 5 min observation
        
        if await self._check_metrics(flag_name):
            await self.flags.set(flag_name, 1.0)  # Full rollout
            print(f"✅ {flag_name} fully rolled out in {env}")
        else:
            await self.flags.set(flag_name, 0)
            print(f"❌ {flag_name} rolled back in {env}")
```

## 4. Database Migration Pipeline

```python
"""Database migration automation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MigrationStrategy(Enum):
    EXPAND_MIGRATE_CONTRACT = "expand_migrate_contract"  # Most common
    BACKWARD_COMPATIBLE = "backward_compatible"
    ONLINE_MIGRATION = "online_migration"
    BLUE_GREEN_DB = "blue_green_db"


@dataclass
class DatabaseMigrationPipeline:
    """Safe database migration automation.
    
    Battle Scar: Adding NOT NULL column to a table with 1B rows
    — locked table for 2 hours. Solution: 3-phase migration.
    """
    
    async def execute_migration(self, migration_id: str, strategy: MigrationStrategy) -> None:
        match strategy:
            case MigrationStrategy.EXPAND_MIGRATE_CONTRACT:
                # Phase 1 (Expand): Add column as nullable
                # Both old and new code work
                
                # Phase 2 (Migrate): Backfill data
                # Deploy app to write to new column
                
                # Phase 3 (Contract): Make column NOT NULL
                # Remove old column references
                pass
            
            case MigrationStrategy.ONLINE_MIGRATION:
                # Use triggers/materialized views
                # Zero downtime
                pass
```

## 5. Release Checklist

```markdown
## Pre-Release Checklist

### Code Quality
- [ ] All tests pass (unit + integration + e2e)
- [ ] No regressions (run last 24h tests)
- [ ] Code coverage > 80%
- [ ] Linting passes (zero warnings in new code)
- [ ] Type checking passes (strict mode)
- [ ] Security scan passes (no CVEs in new deps)

### Documentation
- [ ] API changes documented
- [ ] CHANGELOG updated
- [ ] Migration guide (if DB schema changed)
- [ ] Runbook updated (if new dependencies)

### Observability
- [ ] New metrics added (if new features)
- [ ] Dashboard updated
- [ ] Alert thresholds configured
- [ ] Log levels reviewed

### Operations
- [ ] Rollback plan documented
- [ ] Feature flag ready (if canary)
- [ ] Resource limits reviewed
- [ ] Dependencies version locked
- [ ] Performance test passed (if new code path)

### Approval
- [ ] Code review done (minimum 1 senior)
- [ ] QA sign-off (if UI/API change)
- [ ] Security review (if auth/data change)
- [ ] Release manager approval
```

## 6. Rollback Automation

```python
"""Automated rollback on deploy failure."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RollbackAutomation:
    """Automatic rollback with metric evaluation."""
    
    OBSERVATION_PERIOD = 300  # 5 minutes
    METRIC_THRESHOLDS = {
        "error_rate": {"p50": 0.001, "p99": 0.01},          # 0.1% / 1%
        "latency_p99_ms": {"p50": 200, "p99": 500},
        "throughput_rps": {"p50": -0.2, "p99": -0.5},        # Max 20%/50% drop
    }
    
    async def should_rollback(self, metrics: dict[str, float]) -> bool:
        """Check if rollback is needed based on metrics."""
        for metric_name, value in metrics.items():
            if metric_name in self.METRIC_THRESHOLDS:
                threshold = self.METRIC_THRESHOLDS[metric_name].get("p99")
                if threshold and abs(value) > abs(threshold):
                    print(f"🚨 Rollback triggered: {metric_name}={value} > {threshold}")
                    return True
        return False
    
    async def auto_rollback(self, deployment_id: str, version: str) -> None:
        """Execute automated rollback."""
        await self.rollback_deployment(deployment_id, version)
        await self.notify_team(f"⚠️ Auto-rollback: {version}")
        await self.create_jira_ticket(f"Rollback: {version}")
```

## 7. SLO-Based Deployment Gating

```python
"""Deployment gating based on SLO compliance."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DeploymentGate:
    """Prevent deployment if SLO is at risk."""
    
    async def can_deploy(self, service: str) -> tuple[bool, str]:
        """Check if deployment is allowed based on SLO health."""
        budget_remaining = await self.get_error_budget(service)
        
        if budget_remaining < 0.3:  # < 30% budget remaining
            return (False, "Error budget nearly exhausted")
        
        ongoing_incident = await self.check_ongoing_incident(service)
        if ongoing_incident:
            return (False, f"Ongoing incident: {ongoing_incident}")
        
        return (True, "All gates passed")
```

## 8. Infrastructure as Code (Terraform/Pulumi)

```python
"""Infrastructure as Code patterns."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Terraform best practices:
IAM_POLICIES = """
# Principle of least privilege
resource "aws_iam_policy" "service_policy" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
        ]
        Resource = "arn:aws:s3:::my-bucket/*"
      }
    ]
  })
}
"""


@dataclass
class TerraformState:
    """Terraform state management best practices."""
    
    remote_backend = "s3"  # or consul, terraform cloud
    state_locking = "dynamodb"  # Prevent concurrent modifications
    state_encryption = True
    state_versioning = True
    
    @staticmethod
    def backend_config() -> dict:
        return {
            "bucket": "terraform-state-prod",
            "key": "services/my-service/terraform.tfstate",
            "region": "us-east-1",
            "encrypt": True,
            "dynamodb_table": "terraform-locks",
        }
```

## 9. Git Workflow

```text
Branching Strategy: Trunk-Based Development (TBD)

Main principles:
  - Short-lived branches (< 1 day)
  - Feature flags for incomplete work
  - Direct merge to main (no release branches)
  - Automated CI/CD on every merge

Commits:
  Conventional Commits specification:
    feat: add user search API
    fix: correct pagination cursor encoding
    chore: update dependencies
    docs: add migration guide
    refactor: extract validation logic
    test: add unit tests for rate limiter
    perf: optimize cache lookup

PR Checklist:
  □ Less than 400 lines changed
  □ Single concern per PR
  □ Tests for new code
  □ No TODO/FIXME comments
  □ CHANGELOG updated if necessary
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
