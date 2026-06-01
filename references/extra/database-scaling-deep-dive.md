# Database Scaling: Deep Dive

**От одной PostgreSQL до глобально распределённых БД. Реальные стратегии scaling'а.**

---

## 1. Scaling PostgreSQL

### Read Replicas

```python
"""Read replica setup for PostgreSQL."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random


@dataclass
class DatabaseRouter:
    """Route queries to appropriate database node.
    
    Writes → Primary (single node)
    Reads → Replicas (multiple nodes, load balanced)
    Critical reads → Primary (strong consistency)
    """
    
    primary: Any  # Async SQLAlchemy engine
    replicas: list[Any]  # List of read-only engines
    
    async def write(self, query: str, *params) -> Any:
        """All writes go to primary."""
        async with self.primary.begin() as conn:
            return await conn.execute(query, params)
    
    async def read(self, query: str, *params, 
                   strong_consistency: bool = False) -> Any:
        """Read from primary or replica."""
        if strong_consistency:
            engine = self.primary
        else:
            engine = random.choice(self.replicas)
        
        async with engine.connect() as conn:
            return await conn.execute(query, params)
    
    @property
    def replica_count(self) -> int:
        return len(self.replicas)


# Architecture:
# Primary (writer) → WAL → Replica 1 (read-only)
#                       → Replica 2 (read-only)
#                       → Replica 3 (analytics)
# 
# Failover: Promote replica → update application config
# RTO: 30-120 seconds (manual) or 5 seconds (auto with Patroni)


### Connection Pooling with PgBouncer

PG_BOUNCER_CONFIG = """
  [databases]
  mydb = host=localhost port=5432 dbname=mydb
  
  [pgbouncer]
  listen_addr = 0.0.0.0
  listen_port = 6432
  auth_type = trust
  
  # Pool settings
  pool_mode = transaction        # Best for most apps
  default_pool_size = 50         # Connections to PostgreSQL
  max_client_conn = 500          # Connections from apps
  reserve_pool_size = 10         # Reserved for emergencies
  reserve_pool_timeout = 3       # Seconds before using reserve
  
  # Timeouts
  server_idle_timeout = 300      # Close idle connections
  client_idle_timeout = 600      # Disconnect idle clients
  query_timeout = 30             # Kill long queries
  query_wait_timeout = 10        # Time waiting for connection
"""
```

### Sharding

```python
"""Application-level sharding strategies."""
from __future__ import annotations

import hashlib


class ConsistentHashShard:
    """Distribute data across shards consistently."""
    
    def __init__(self, shards: list[str], replicas: int = 100):
        self._shards = shards
        self._ring = self._build_ring(replicas)
    
    def _build_ring(self, replicas: int) -> dict[int, str]:
        """Create consistent hash ring with virtual nodes."""
        ring = {}
        for shard in self._shards:
            for i in range(replicas):
                key = hashlib.md5(f"{shard}:{i}".encode()).hexdigest()
                hash_val = int(key[:8], 16)
                ring[hash_val] = shard
        return dict(sorted(ring.items()))
    
    def get_shard(self, key: str) -> str:
        """Get shard for key (deterministic)."""
        hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
        for ring_key in self._ring:
            if hash_val <= ring_key:
                return self._ring[ring_key]
        return self._ring[next(iter(self._ring))]
    
    def add_shard(self, shard: str) -> None:
        """Add shard (only affects 1/N of keys)."""
        self._shards.append(shard)
        self._ring = self._build_ring(100)
    
    def remove_shard(self, shard: str) -> None:
        """Remove shard (only affects 1/N of keys)."""
        self._shards.remove(shard)
        self._ring = self._build_ring(100)
```

## 2. Query Optimization

### Indexing Strategy

```python
"""Complete indexing strategy for PostgreSQL."""
from __future__ import annotations


INDEX_RULES = """
  1. Index WHERE clauses, JOIN columns, ORDER BY columns
  2. Multi-column indexes: most selective column first
  3. Covering indexes: INCLUDE columns to avoid heap lookups
  4. Partial indexes: index WHERE status = 'active' 
  5. Unique indexes: for uniqueness enforcement
  6. BRIN indexes for time-series (much smaller than B-tree)
  7. GIN indexes for JSONB and full-text search
  8. GiST indexes for geospatial data
  
  Example indexes:
    CREATE INDEX idx_orders_user_status 
      ON orders(user_id, status) 
      WHERE status IN ('pending', 'processing');
    
    CREATE INDEX idx_orders_created_at 
      ON orders(created_at DESC) 
      INCLUDE (total, status);
    
    CREATE INDEX idx_products_search 
      ON products USING GIN(to_tsvector('english', name));
"""


# Query analysis tools:
QUERY_ANALYSIS = """
  EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT * FROM orders WHERE user_id = 42;
  
  Key metrics:
    - Sequential scan vs Index scan
    - Number of rows examined vs returned
    - Buffer hits vs reads
    - Actual time vs estimated time
  
  Warning signs:
    - Sequential scan on large table
    - Nested Loop with many rows
    - Sort without index
    - Hash Aggregate with large memory
    - "Rows Removed by Filter" >> "Rows" (bad index)
"""
```

### N+1 Query Detection

```python
"""N+1 query detection and prevention."""
from __future__ import annotations


N_PLUS_ONE_DETECTION = """
  Symptoms:
    - API response time grows linearly with results
    - Database CPU spikes with simple queries
    - Hundreds of identical queries in slow query log
  
  Detection:
    # pg_stat_statements shows repeated queries:
    SELECT query, calls, total_time 
    FROM pg_stat_statements 
    WHERE query LIKE '%WHERE user_id = %'
    ORDER BY calls DESC;
  
  Fix:
    - Eager loading (JOIN)
    - Batch loading (IN clause)
    - DataLoader pattern
"""
```

## 3. NoSQL Scaling

### DynamoDB / Cassandra Patterns

```python
"""NoSQL data modeling for scale."""
from __future__ import annotations


# DynamoDB single-table design:
DYNAMODB_SINGLE_TABLE = """
  Single Table Design Principles:
    1. One table per application
    2. Access patterns determine schema
    3. Sort key for time-series and sorting
    4. GSI for alternative access patterns
    5. Composite keys for hierarchical data
  
  Example (e-commerce):
    PK              SK                    Attributes
    USER#123        PROFILE               name, email, address
    USER#123        ORDER#2024-01-15#A1   total, status, items
    USER#123        ORDER#2024-01-20#B2   total, status, items
    ORDER#A1        ITEM#P101             product, quantity, price
    ORDER#A1        ITEM#P205             product, quantity, price
    PRODUCT#P101    META                  name, category, price
"""


@dataclass
class DynamoDBQueryPatterns:
    """Common DynamoDB query patterns."""
    
    # Get user by ID
    GET_USER = """
    SELECT * FROM table 
    WHERE PK = 'USER#123' AND SK = 'PROFILE'
    """
    
    # Get user orders (sorted by date)
    GET_USER_ORDERS = """
    SELECT * FROM table 
    WHERE PK = 'USER#123' 
    AND SK BETWEEN 'ORDER#2024-01-01' AND 'ORDER#2024-12-31'
    ORDER BY SK DESC
    """
    
    # Get order items
    GET_ORDER_ITEMS = """
    SELECT * FROM table 
    WHERE PK = 'ORDER#A1' 
    AND SK BEGINS_WITH 'ITEM#'
    """
```

## 4. Migration Strategies

### Zero-Downtime Migration

```python
"""Zero-downtime database migration patterns."""
from __future__ import annotations


ZERO_DOWNTIME_MIGRATION = """
  Phase 1 (Expand):
    - Add new columns as NULLABLE
    - Add new indexes (CONCURRENTLY to avoid locks)
    - Both old and new code work
  
  Phase 2 (Migrate):
    - Backfill data in batches
    - Deploy code that writes to both old and new
    - Monitor for issues
  
  Phase 3 (Contract):
    - Remove old columns
    - Make new columns NOT NULL
    - Remove old code paths
  
  Example:
    # Phase 1
    ALTER TABLE users ADD COLUMN email_new VARCHAR(255);
    CREATE INDEX CONCURRENTLY idx_users_email_new ON users(email_new);
    
    # Phase 2
    -- Backfill in batches
    UPDATE users SET email_new = email WHERE id BETWEEN 0 AND 10000;
    
    # Phase 3
    ALTER TABLE users DROP COLUMN email;
    ALTER TABLE users RENAME COLUMN email_new TO email;
    ALTER TABLE users ALTER COLUMN email SET NOT NULL;
"""
```

## 5. Backup & Recovery

```python
"""Production backup strategy."""
from __future__ import annotations


BACKUP_STRATEGY = """
  Full backup: Weekly (Sunday 02:00)
  Incremental: Daily (every 6 hours)
  WAL archiving: Continuous (every 5 minutes)
  
  Retention:
    Daily: 7 days
    Weekly: 4 weeks
    Monthly: 12 months
  
  Storage:
    Primary: S3/Cloud Storage (cross-region)
    Secondary: Glacier after 30 days
  
  Recovery testing:
    - Automated restore test: Monthly
    - Full DR drill: Quarterly
    - Point-in-time recovery test: Monthly
  
  RPO: 5 minutes (WAL shipping)
  RTO: 2 hours (full restore from S3)
"""


@dataclass
class BackupVerification:
    """Verify backups are restorable."""
    
    async def test_restore(self, backup_id: str) -> bool:
        """Test restore of backup to staging environment."""
        try:
            # 1. Provision staging DB
            # 2. Restore from backup
            # 3. Run integrity checks
            # 4. Compare row counts with production
            # 5. Tear down staging
            return True
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            await self._alert(f"Backup {backup_id} is corrupted!")
            return False
```


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
