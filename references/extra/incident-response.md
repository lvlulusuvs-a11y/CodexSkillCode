# Incident Response Runbook

**Что делать, когда прод горит. Пошаговые playbook'и для Principal Engineer.**

---

## 1. Incident Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| SEV1 | System down / data loss | 5 min | Payment service down |
| SEV2 | Major feature broken | 15 min | Search not working |
| SEV3 | Minor issue | 1 hour | UI glitch |
| SEV4 | Cosmetic | Next sprint | Wrong color |

## 2. SEV1 Playbook

### Step 1: Stop the Bleeding (0-2 min)
- Rollback last deploy
- Feature flag off
- Traffic redirect (if multi-region)
- Scale up (more replicas)

### Step 2: Communication (2-5 min)
- Create incident channel (#incident-xxx)
- Ping on-call + secondary
- Update status page
- Notify stakeholders

### Step 3: Investigate (5-15 min)
- Check dashboards (error rate, latency, saturation)
- Check recent changes (git log, deploy history)
- Check alerts (Prometheus, Sentry, PagerDuty)
- Reproduce locally if possible

### Step 4: Mitigate (15-30 min)
- Apply hotfix
- Verify fix in staging
- Deploy fix (with override if needed)
- Monitor after fix

### Step 5: Resolve (30+ min)
- Confirm all metrics back to baseline
- Declare incident resolved
- Schedule postmortem (within 48h)

## 3. Common Incident Patterns

### High Error Rate

```python
TRIAGE_CHECKLIST = [
    "Check deploy time vs alert time",
    "Check feature flags changed recently",
    "Check dependency status (DB, Redis, Kafka)",
    "Check recent config changes",
    "Check traffic pattern changes",
    "Look at error samples in Sentry",
]
```

### High Latency

```python
LATENCY_CHECKLIST = [
    "Check p50 vs p99 (is it everyone or just slow requests?)",
    "Check DB query times",
    "Check external API call times",
    "Check CPU/memory usage",
    "Check garbage collection (if JVM/Go)",
    "Check connection pool exhaustion",
    "Check disk I/O (logging level changed?)",
]
```

### Service Down

```python
DOWN_CHECKLIST = [
    "Check kubernetes pod status",
    "Check resource limits (OOMKilled?)",
    "Check health endpoints (live/ready/startup)",
    "Check recent logs before crash",
    "Check upstream dependencies",
    "Check DNS resolution",
    "Check TLS certificates expiry",
]
```

## 4. Runbook Templates

### Database Connection Issues

```yaml
# Runbook: DB Connection Pool Exhaustion

symptoms:
  - "cannot acquire connection from pool"
  - "timeout waiting for idle connection"
  - "too many connections"

checks:
  - "SELECT count(*) FROM pg_stat_activity"  # Current connections
  - "SHOW max_connections"                    # Configured max
  - "pg_stat_activity where state = 'idle'"   # Idle connections
  
mitigations:
  - "Increase pool_size in application"
  - "Kill idle connections: SELECT pg_terminate_backend(pid)"
  - "Check for long-running queries: SELECT * FROM pg_stat_activity WHERE state = 'active'"

prevention:
  - "Add connection pool monitoring alert"
  - "Set idle_in_transaction_session_timeout"
  - "Set statement_timeout on all queries"
```

### Kafka Consumer Lag

```yaml
# Runbook: Kafka Consumer High Lag

symptoms:
  - "consumer_lag > 10000"
  - "Processing delay > 5 minutes"

checks:
  - "kafka-consumer-groups --describe"  # Current lag
  - "Check consumer logs for errors"
  - "Check if consumer is running"
  
mitigations:
  - "Restart consumer group"
  - "Increase partitions"
  - "Add more consumer instances"
  - "Reset offset to latest (careful with data loss!)"

prevention:
  - "Add lag monitoring alert"
  - "Auto-scaling based on lag"
  - "DLQ for failed messages"
```

## 5. Postmortem Template

```markdown
# Postmortem Incident #123

## Summary
- Date: YYYY-MM-DD
- Duration: XX minutes
- Impact: X% users affected
- Severity: SEV1/SEV2

## Timeline
| Time | Event |
|------|-------|
| 14:23 | Alert triggered |
| 14:25 | On-call acknowledged |
| 14:30 | Root cause identified |
| 14:45 | Mitigation applied |
| 15:00 | All metrics normal |

## Root Cause
[Describe what caused the incident]

## Contributing Factors
- [Factor 1]
- [Factor 2]

## What Went Well
- [Thing 1]
- [Thing 2]

## What Went Wrong
- [Thing 1]
- [Thing 2]

## Action Items
| Priority | Action | Owner | Due |
|----------|--------|-------|-----|
| P0 | [Critical fix] | @person | 24h |
| P1 | [Improvement] | @person | 1w |
| P2 | [Nice to have] | @person | 1m |

## Lessons Learned
- [Lesson 1]
- [Lesson 2]

## Blameless Statement
This incident was caused by systemic issues, not individual mistakes.
The goal is to improve our systems, not assign blame.
```

## 6. On-Call Best Practices

### Before On-Call
- [ ] Review recent changes
- [ ] Check current dashboards
- [ ] Update runbook if needed
- [ ] Test alert notification
- [ ] Prepare escalation contacts

### During On-Call
- [ ] Acknowledge alerts within SLA
- [ ] Communicate clearly in incident channel
- [ ] Document timeline
- [ ] Escalate early if stuck (>15min)
- [ ] Take breaks (2h max sustained)

### After On-Call
- [ ] Complete shift handoff
- [ ] Update runbooks with new findings
- [ ] File follow-up tickets
- [ ] Rest and recover

## 7. Incident Communication Templates

### Initial Alert
```
🔴 SEV1: [Service] is down
Impact: [Description of user impact]
Time: [Current time]
Action: Investigating
Channel: #incident-xxx
```

### Update (every 15 min)
```
🔄 Update: [service] incident
Progress: [What we know and what we're doing]
ETA: [Estimated time to fix]
Workaround: [If available]
```

### Resolution
```
✅ Resolved: [service] incident
Duration: XX minutes
Root cause: [Brief description]
Action items: [Link to postmortem]
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


---

## Production Usage

```python
"""Production implementation with full resilience."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass 
class ResilientOperation:
    """Execute operations with full production patterns."""
    
    async def execute(self, operation: str, fn: callable, *args, **kwargs) -> Any:
        for attempt in range(3):
            try:
                async with asyncio.timeout(30):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Operation '{operation}' timed out")
                    raise
            except Exception:
                logger.exception(f"Operation '{operation}' failed")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    raise
        return None
    

### Principal Engineer Summary

This pattern encapsulates everything a Principal Engineer knows:
1. Always set timeouts
2. Always retry transient failures
3. Always log with context
4. Always have a fallback plan
5. Always think about observability

Apply this to every external interaction in your system.
