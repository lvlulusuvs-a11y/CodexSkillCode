# Cloud Architecture Patterns

**Architecting for AWS/GCP/Azure at Big Tech scale.**

---

## 1. Multi-Region Architecture

```python
"""Multi-region deployment patterns."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RegionStrategy(Enum):
    ACTIVE_ACTIVE = "active_active"     # All regions serve traffic
    ACTIVE_PASSIVE = "active_passive"   # One active, others standby
    ACTIVE_READ = "active_read"         # Write to primary, read from all


@dataclass
class MultiRegionConfig:
    strategy: RegionStrategy
    primary_region: str = "us-east-1"
    secondary_regions: list[str] = None
    failover_automation: bool = True
    
    # RTO (Recovery Time Objective) and RPO (Recovery Point Objective)
    rto_seconds: int = 300     # 5 minutes
    rpo_seconds: int = 60      # 1 minute of data loss


# Database replication strategies:
DB_REPLICATION = """
  Active-Passive:
    - Primary: us-east-1 (write)
    - Read replicas: eu-west-1, ap-southeast-1 (read-only)
    - Failover: Promote read replica to primary
    - RTO: 1-5 minutes, RPO: < 1 second

  Active-Active:
    - Multi-master replication
    - Conflict resolution: last-write-wins, CRDTs
    - Requires: DynamoDB Global Tables, CockroachDB
    - RTO: < 1 minute, RPO: < 1 second

  Application-level replication:
    - Write to local DB + async replication
    - Kafka for cross-region event shipping
    - Higher latency, more control
"""

# DNS routing:
DNS_ROUTING = """
  Latency-based: Route to lowest latency region
  Geo-based: Route based on user location
  Weighted: Distribute traffic across regions
  
  Failover:
    Health check → detect region failure → update DNS → traffic redirects
    TTL: 60 seconds for fast failover
"""
```

## 2. Serverless Architecture

```python
"""Serverless patterns for event-driven systems."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Lambda + SQS for async processing:
LAMBDA_SQS_PATTERN = """
  API Gateway → SQS → Lambda → DynamoDB
  
  Benefits:
    - No cold start for queue processing
    - Built-in retry + DLQ
    - Auto-scaling (Lambda scales with queue depth)
    - Cost-effective for variable workloads
"""


@dataclass
class LambdaConfig:
    """Production Lambda configuration."""
    memory: int = 1024        # MB
    timeout: int = 30         # seconds
    reserved_concurrency: int = 100
    provisioned_concurrency: int = 10  # For critical functions
    vpc: bool = True          # Attach to VPC for DB access
    ephemeral_storage: int = 512  # MB
    arm_architecture: bool = True  # Graviton = 20% cheaper


# Step Functions for orchestration:
STEP_FUNCTIONS_PATTERN = """
  AWS Step Functions → Lambda sequence
  
  Use cases:
    - Order processing pipeline
    - ETL workflows
    - Approval flows
    - Multi-step data processing
  
  Features:
    - Retry with backoff
    - Error handling with fallback
    - Parallel execution
    - Human approval steps
"""


# Lambda best practices:
LAMBDA_BEST_PRACTICES = """
  Performance:
    - Initialize clients outside handler
    - Use connection pooling (RDS Proxy for DB)
    - Warm-up with CloudWatch Events
    - Use Lambda Power Tuning for optimal memory
  
  Cost:
    - Right-size memory (more memory = more CPU)
    - Avoid VPC unless necessary (NAT Gateway costs)
    - Use reserved concurrency for critical paths
    - Monitor with Lambda Insights
  
  Security:
    - Least privilege IAM (specific resource ARNs)
    - Encrypt environment variables
    - Use Secrets Manager for credentials
    - Enable VPC for database access
"""
```

## 3. Microservices Communication

```python
"""Microservices communication patterns."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


COMMUNICATION_PATTERNS = {
    "sync_rest": {
        "use_case": "CRUD APIs, simple queries",
        "pros": "Simple, familiar, debuggable",
        "cons": "Coupling, cascading failures",
        "recommended": "For internal admin APIs only",
    },
    "sync_grpc": {
        "use_case": "High-performance internal services",
        "pros": "Fast, typed contracts, streaming",
        "cons": "Harder to debug, tooling maturity",
        "recommended": "For latency-critical paths",
    },
    "async_messaging": {
        "use_case": "Event-driven, decoupled services",
        "pros": "Loose coupling, buffered, replayable",
        "cons": "Eventually consistent, harder to trace",
        "recommended": "Default for service-to-service",
    },
}


@dataclass
class ServiceDiscovery:
    """Service discovery patterns."""
    
    # Options:
    DNS = "Round-robin DNS (simple, no health checks)"
    L7_PROXY = "Service mesh (Envoy/Istio — health-aware, retry, metrics)"
    CONSUL = "Consul/etcd — service registry with health checks"
    K8S_DNS = "Kubernetes DNS — built-in, basic"


@dataclass
class API Gateway:
    """API Gateway responsibilities."""
    
    FEATURES = [
        "Authentication (JWT, OAuth)",
        "Rate limiting (per client)",
        "Request transformation",
        "Circuit breaking",
        "TLS termination",
        "Caching (responses)",
        "Access logging",
        "Canary routing",
    ]
```

## 4. Observability at Scale

```python
"""Observability stack for Big Tech."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ObservabilityStack:
    """Production observability tooling."""
    
    # Metrics
    metrics_system = "Prometheus + Thanos"
    metrics_retention = "30 days high-res, 1 year downsampled"
    metrics_cardinality = "< 1M series per service"
    
    # Logging
    logging_system = "Elasticsearch / Loki"
    logging_volume = "1-10 TB/day per service"
    logging_retention = "7 days hot, 30 days warm, 1 year cold"
    
    # Tracing
    tracing_system = "OpenTelemetry + Jaeger / Datadog"
    tracing_sample_rate = "1% (production), 100% (dev)"
    tracing_retention = "14 days"
    
    # Alerting
    alerting = "Prometheus AlertManager + PagerDuty"
    alert_on = "SLO violations, not every spike"
    silence_rules = "During maintenance windows"


# Key dashboards every service needs:
SERVICE_DASHBOARD = """
  Service Dashboard:
    Row 1: RED metrics (Rate, Errors, Duration)
      - Request rate (rps)
      - Error rate (%)
      - Latency (p50, p95, p99, p99.9)
    
    Row 2: Resource usage
      - CPU utilization (%)
      - Memory usage (GB)
      - Network I/O (MB/s)
      - Disk I/O (IOPS)
    
    Row 3: Dependencies
      - Database connections
      - Cache hit ratio
      - Queue depth
      - External API latency
    
    Row 4: Business metrics
      - Active users
      - Orders/transactions
      - Conversion rate
      - Revenue
"""
```

## 5. Cost Optimization at Scale

```python
"""Cloud cost optimization strategies."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CloudCostOptimization:
    """Cost-saving strategies that actually work."""
    
    # Compute
    compute_strategies = {
        "rightsizing": "30-50% savings (match instance to workload)",
        "reserved_instances": "40-60% savings (1-3 year commitment)",
        "spot_instances": "60-90% savings (stateless workloads)",
        "graviton": "20-30% savings (ARM-based processors)",
        "auto_scaling": "20-40% savings (scale down when idle)",
    }
    
    # Storage
    storage_strategies = {
        "s3_lifecycle": "40-60% savings (move to colder tiers)",
        "gp2_to_gp3": "20% savings (better performance, lower cost)",
        "ebs_snapshots": "Clean up orphaned snapshots",
        "data_compression": "50-80% reduction (columnar + compression)",
        "object_expiration": "Delete stale objects automatically",
    }
    
    # Network
    network_strategies = {
        "cloudfront": "Reduce data transfer costs (CDN edge)",
        "private_link": "Avoid NAT gateway costs",
        "vpc_peering": "vs transit gateway — cost comparison",
        "data_transfer": "Keep data in same region/AZ",
    }


# Monthly cost breakdown example:
MONTHLY_COST_BREAKDOWN = """
  Service: MyApp (Production)
  
  Compute (EC2/EKS): $45,000 (60%)
    - App instances: $25,000
    - Database: $12,000
    - Cache: $8,000
  
  Storage (S3/EBS): $12,000 (16%)
    - S3 standard: $5,000
    - S3 glacier: $2,000
    - EBS volumes: $3,000
    - Snapshots: $2,000
  
  Network: $8,000 (11%)
    - Data transfer: $5,000
    - NAT Gateway: $2,000
    - Load balancer: $1,000
  
  Other: $10,000 (13%)
  
  Total: $75,000/month
  
  Optimization potential: 30-40% ($25-30K savings)
"""
```

## 6. Disaster Recovery

```python
"""Disaster recovery planning."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DisasterLevel(Enum):
    AZ_FAILURE = "Availability Zone failure"
    REGION_FAILURE = "Entire region failure"
    DATA_CORRUPTION = "Data corruption / accidental deletion"
    SECURITY_BREACH = "Security incident"


@dataclass
class DRPlan:
    """Disaster recovery plan."""
    
    # Backup strategy
    backup = {
        "database": "Continuous WAL archiving + daily snapshots",
        "files": "Cross-region replication (S3 CRR)",
        "config": "Infrastructure as Code (Terraform state)",
        "secrets": "AWS Secrets Manager cross-region replication",
    }
    
    # Recovery procedures
    recovery = {
        "az_failure": "Auto — multi-AZ deployment",
        "region_failure": "Manual — promote DR region, update DNS",
        "data_corruption": "PITR (Point-in-Time Recovery) to last good state",
        "security_breach": "Isolate, rotate credentials, restore from clean backup",
    }
    
    # Testing schedule
    testing = {
        "backup_restore": "Monthly automated test",
        "dr_region": "Quarterly full DR drill",
        "security_incident": "Bi-annual tabletop exercise",
    }
```

## 7. Networking Patterns

```python
"""VPC and networking architecture."""
from __future__ import annotations


VPC_DESIGN = """
  /16 VPC (65,536 IPs)
  ├── Public subnets (/24): Load balancers, NAT gateways
  ├── Private subnets (/20): Application instances
  ├── Database subnets (/22): RDS, ElastiCache, Kafka
  └── Isolated subnets (/22): Internal tools
  
  Each tier in 3 AZs (us-east-1a, b, c)
  
  Security:
    - Security Groups: Stateful, per-service
    - NACLs: Stateless, subnet-level (rarely needed)
    - Network ACLs: Block known bad IPs at edge
"""

NETWORK_SECURITY = """
  Defense in depth:
    Layer 1: AWS WAF (Web Application Firewall) — SQLi, XSS, DDoS
    Layer 2: CloudFront + Origin Access Identity
    Layer 3: ALB (Application Load Balancer) — TLS termination
    Layer 4: Security Groups — service-to-service access
    Layer 5: Network Policies (k8s) — pod-to-pod access
    Layer 6: IAM — resource-based policies
    
  Zero Trust:
    - No implicit trust between services
    - mTLS for all service-to-service communication
    - Every request authenticated and authorized
    - Continuous verification, never trust
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

## Extended Cloud Architecture Patterns

### Service Mesh (Istio/Linkerd)

```python
"""Service mesh patterns for microservices."""
from __future__ import annotations


SERVICE_MESH_PATTERNS = """
  Service mesh provides:
  
  1. Traffic Management
     - Canary releases (weight-based routing)
     - Blue-green deployments
     - Circuit breaking
     - Retry + timeout
     - Fault injection (chaos)
  
  2. Security
     - mTLS between all services
     - Service-to-service auth
     - Certificate rotation
  
  3. Observability
     - Metrics (HTTP, gRPC, TCP)
     - Distributed tracing
     - Access logs
  
  4. Resilience
     - Timeouts
     - Retries
     - Circuit breakers
     - Rate limiting
  
  When to use:
    - > 20 microservices
    - Multiple protocols (HTTP, gRPC, TCP)
    - Security requirements (mTLS)
    - Multi-team ownership
  
  When NOT to use:
    - < 10 services (too complex)
    - Simple request-response patterns
    - Single team ownership
    - No security requirements
"""


### Kubernetes Custom Controllers

K8S_CONTROLLER = """
  Custom controllers extend Kubernetes for your use case:
  
  Examples:
    - Database controller (manage Postgres clusters)
    - Backup controller (schedule and verify backups)
    - Config controller (validate and propagate configs)
    - Migration controller (run DB migrations on deploy)
  
  Pattern:
    1. Watch for custom resources (CRD)
    2. Reconcile desired state
    3. Update status
    4. Handle errors and retries
"""


### Cloud Cost Optimization

COST_OPTIMIZATION = """
  Cost Optimization Framework:
  
  1. Right-sizing (30-50% savings)
     - Match instance type to workload
     - Use VPA recommendations
     - Downsize over-provisioned resources
  
  2. Reserved Instances / Savings Plans (40-60%)
     - 1-year commitment for baseline
     - 3-year for stable workloads
     - Convertible for flexibility
  
  3. Spot Instances (60-90%)
     - For stateless, fault-tolerant workloads
     - Batch processing, CI/CD, testing
     - Use Spot Instances with fallback
  
  4. Storage Optimization (40-60%)
     - Lifecycle policies for S3
     - Delete orphaned EBS volumes
     - Use appropriate storage tiers
  
  5. Network Optimization (20-30%)
     - Data transfer between services in same AZ
     - Use CloudFront for egress
     - NAT Gateway vs VPC endpoints
  
  6. Serverless (pay-per-use)
     - Lambda for variable workloads
     - DynamoDB for predictable performance
     - Fargate if container needed
"""
