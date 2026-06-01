# Principal Engineer Learning Path

**От Senior до Principal Engineer: что учить, как практиковать, как измерить прогресс.**

---

## 1. Technical Depth Required

```python
"""What a Principal Engineer must master."""
from __future__ import annotations


PRINCIPAL_SKILLS = {
    "system_design": {
        "level": "Expert",
        "skills": [
            "Design systems handling 10M+ users",
            "Trade-off analysis (CAP, consistency models)",
            "Cost estimation and optimization",
            "Migration strategies (strangler fig, blue-green)",
        ],
        "resources": [
            "references/extra/system-design-reference.md",
            "references/extra/system-design-problems.md",
            "references/extra/distributed-systems-patterns.md",
        ],
    },
    "production_excellence": {
        "level": "Expert",
        "skills": [
            "Incident response and postmortem culture",
            "SLO/SLI/Error Budget management",
            "Chaos engineering and game days",
            "Capacity planning and cost optimization",
        ],
        "resources": [
            "references/extra/incident-response.md",
            "references/extra/production-patterns.md",
            "references/battle-scars/production-war-stories.md",
        ],
    },
    "architecture": {
        "level": "Advanced",
        "skills": [
            "Event-driven architecture (Kafka, CQRS, Event Sourcing)",
            "Microservices decomposition strategies",
            "API design and versioning",
            "Platform thinking and internal developer platforms",
        ],
        "resources": [
            "references/infra/kafka-patterns.md",
            "references/extra/cloud-architecture-patterns.md",
            "references/extra/platform-engineering-patterns.md",
        ],
    },
    "leadership": {
        "level": "Advanced",
        "skills": [
            "Technical strategy and roadmapping",
            "Mentoring and growing other engineers",
            "Cross-team influence without authority",
            "Technical decision documentation (ADRs)",
        ],
        "resources": [
            "references/principal-engineer-handbook.md",
            "references/extra/senior-dev-wisdom.md",
        ],
    },
    "coding": {
        "level": "Expert",
        "skills": [
            "Write code that's boring (predictable, testable, maintainable)",
            "Know when NOT to write code",
            "Deep understanding of at least one language",
            "Working knowledge of multiple languages",
        ],
        "resources": [
            "SKILL.md (Speed Mode section)",
            "references/languages/*",
        ],
    },
}
```

## 2. Monthly Learning Plan

```python
"""3-month plan for Senior → Principal transition."""

MONTH_1_SYSTEM_DESIGN = """
  Week 1: Distributed Systems Fundamentals
    - CAP theorem, consistency models
    - Read: references/extra/distributed-systems-patterns.md
    - Practice: Design a distributed key-value store
  
  Week 2: Production Patterns
    - Circuit breaker, bulkhead, retry
    - Read: references/extra/production-patterns.md
    - Practice: Implement circuit breaker in your service
  
  Week 3: Observability
    - RED/U.S.E metrics, structured logging
    - Read: references/extra/monitoring-observability.md
    - Practice: Add RED metrics to your service
  
  Week 4: Scalability
    - CQRS, Event Sourcing, Saga
    - Read: references/extra/system-design-reference.md
    - Practice: Design event-driven system
"""

MONTH_2_LEADERSHIP = """
  Week 1: Technical Strategy
    - OKRs, technical roadmaps
    - Read: references/principal-engineer-handbook.md
    - Practice: Write a technical strategy doc
  
  Week 2: Mentoring
    - SBI feedback model
    - Practice: Mentor a junior engineer
    - Practice: Give a tech talk
  
  Week 3: Influence
    - RFC process, design docs
    - Practice: Write an RFC for architecture change
    - Practice: Get buy-in from 3 teams
  
  Week 4: Culture
    - Blameless postmortems, on-call
    - Practice: Run a postmortem
    - Practice: Organize a game day
"""

MONTH_3_DEPTH = """
  Week 1: Multi-language
    - Pick Go or Rust
    - Read: references/languages/go-patterns.md
    - Practice: Rewrite small service in new language
  
  Week 2: Infrastructure
    - Kubernetes patterns
    - Read: references/infra/kubernetes-patterns.md
    - Practice: Debug production k8s issue
  
  Week 3: Infrastructure (cont.)
    - Kafka deep dive
    - Read: references/infra/kafka-patterns.md
    - Practice: Set up Kafka consumer with DLQ
  
  Week 4: Integration
    - Full CI/CD pipeline
    - Read: references/extra/cd-deployment-patterns.md
    - Practice: Automate your team's deploy process
"""
```

## 3. Self-Assessment Rubric

```python
"""Rate yourself: 1 (novice) to 5 (expert)."""

ASSESSMENT_AREAS = """
  System Design:
    [ ] 1: Can design CRUD APIs
    [ ] 2: Can design with caching, CDN, async processing
    [ ] 3: Can design distributed systems (10M+ users)
    [ ] 4: Can design globally distributed systems
    [ ] 5: Can design systems that don't exist yet
  
  Production Excellence:
    [ ] 1: Can deploy and monitor a service
    [ ] 2: Can handle on-call and incidents
    [ ] 3: Can improve reliability (SLOs, error budgets)
    [ ] 4: Can design reliability programs across teams
    [ ] 5: Can change industry practices
  
  Technical Leadership:
    [ ] 1: Can review code for bugs
    [ ] 2: Can mentor a junior engineer
    [ ] 3: Can influence team technical decisions
    [ ] 4: Can influence across multiple teams
    [ ] 5: Can set technical direction for the org
  
  Coding:
    [ ] 1: Can write working code
    [ ] 2: Can write testable, maintainable code
    [ ] 3: Can optimize for performance
    [ ] 4: Can design systems that enable team productivity
    [ ] 5: Can create frameworks that codify best practices
"""

# Target for Principal: 4+ in all areas
```

## 4. Books & References

```python
"""Essential reading for Principal Engineer."""

BOOKS = [
    {
        "title": "Designing Data-Intensive Applications (DDIA)",
        "author": "Martin Kleppmann",
        "relevance": "10/10 — must read for distributed systems",
        "chapters": {
            "1-4": "Storage and retrieval (LSM, B-Trees, columnar)",
            "5-9": "Replication, partitioning, transactions",
            "10-12": "Batch/stream processing, consistency",
        },
    },
    {
        "title": "Site Reliability Engineering (SRE Book)",
        "author": "Google",
        "relevance": "9/10 — production mindset",
        "chapters": {
            "1-5": "SRE fundamentals, SLOs, error budgets",
            "6-13": "Monitoring, on-call, incident response",
            "14-20": "Capacity planning, change management",
        },
    },
    {
        "title": "System Design Interview",
        "author": "Alex Xu",
        "relevance": "8/10 — interview prep + real patterns",
    },
    {
        "title": "Staff Engineer",
        "author": "Will Larson",
        "relevance": "9/10 — leadership beyond senior",
    },
    {
        "title": "The Manager's Path",
        "author": "Camille Fournier",
        "relevance": "7/10 — management and leadership",
    },
    {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "relevance": "8/10 — architecture fundamentals",
    },
]
```

## 5. Interview Preparation

```python
"""Principal Engineer interview preparation."""

INTERVIEW_FOCUS = """
  System Design (40% of interview weight):
    - Design Uber/WhatsApp/Netflix (scale, trade-offs)
    - Design payment system (consistency, idempotency)
    - Design real-time analytics pipeline (streaming, batch)
    - Design distributed database (replication, consistency)
    Focus: Trade-offs, not just components
  
  Behavioral (30%):
    - Conflict resolution: "Tell me about a time..."
    - Technical leadership: "How did you influence..."
    - Failure: "Tell me about a mistake..."
    - Impact: "What was your biggest achievement..."
    Focus: STAR-R (Situation, Task, Action, Result, Reflection)
  
  Coding (20%):
    - Medium-hard LeetCode (system design > algorithms)
    - Clean, production-quality code
    - Consider edge cases, error handling
    - Think aloud about trade-offs
    Focus: Quality over speed
  
  Experience Deep Dive (10%):
    - Past system designs and their outcomes
    - What would you do differently?
    - How do you stay current?
    Focus: Authenticity and depth
"""
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
