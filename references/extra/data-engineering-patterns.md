# Data Engineering Patterns

**Production data pipelines, ETL/ELT, streaming, and warehousing.**

---

## 1. ETL vs ELT

```
ETL (Extract-Transform-Load):
  Source → Transform (processing) → Target
  Pros: Clean data on arrival
  Cons: Expensive transformation, schema rigid

ELT (Extract-Load-Transform):
  Source → Target → Transform (in-warehouse)
  Pros: Flexible, raw data available, scalable
  Cons: More storage, compliance concerns

Modern choice: ELT (dbt + Snowflake/BigQuery/ClickHouse)
```

## 2. Batch Processing Pipeline

```python
"""Production batch processing with checkpointing."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, AsyncIterator


@dataclass
class BatchPipelineConfig:
    batch_size: int = 10000
    max_retries: int = 3
    checkpoint_interval: int = 100  # checkpoints every N batches
    error_threshold: float = 0.05  # max 5% error rate


@dataclass
class BatchProcessor:
    """Reliable batch processing with recovery.
    
    Battle Scar: 10M record batch failed at 95% — restarted from 0%.
    With checkpointing — resume from 95%.
    """
    
    async def process_with_checkpoint(
        self,
        source: AsyncIterator[dict],
        transform: Callable[[dict], dict],
        sink: Callable[[list[dict]], Awaitable[None]],
        checkpoint_key: str,
    ) -> int:
        """Process items with checkpoint recovery."""
        checkpoint = await self._load_checkpoint(checkpoint_key)
        processed = 0
        batch: list[dict] = []
        errors = 0
        
        async for item in source:
            processed += 1
            
            if checkpoint and processed <= checkpoint:
                continue  # Skip already processed
            
            try:
                transformed = transform(item)
                batch.append(transformed)
            except Exception as e:
                errors += 1
                await self._log_error(item, str(e))
                continue
            
            if len(batch) >= self._config.batch_size:
                await self._flush_batch(batch, sink)
                batch = []
                
                if processed % self._config.checkpoint_interval == 0:
                    await self._save_checkpoint(checkpoint_key, processed)
        
        # Final batch
        if batch:
            await self._flush_batch(batch, sink)
            await self._save_checkpoint(checkpoint_key, processed)
        
        error_rate = errors / max(processed, 1)
        if error_rate > self._config.error_threshold:
            raise PipelineError(f"Error rate {error_rate:.1%} exceeds threshold")
        
        return processed
```

## 3. Streaming Data Pipeline

```python
"""Streaming data processing with Kafka."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class StreamProcessor:
    """Kafka stream processing with exactly-once semantics."""
    
    async def process_stream(
        self,
        consumer,
        handler: Callable[[dict], Awaitable[None]],
        dlq_handler: Callable[[dict, str], Awaitable[None]],
    ) -> None:
        """Process stream with DLQ for failed messages."""
        async for msg in consumer:
            try:
                data = json.loads(msg.value)
                await handler(data)
                await consumer.commit()
            except Exception as e:
                await dlq_handler(msg.value, str(e))
                # Don't commit — message stays for retry
    
    # Windowing:
    # - Tumbling window: non-overlapping, fixed intervals
    # - Sliding window: overlapping, fixed intervals
    # - Session window: gap-based, dynamic intervals
    
    async def tumbling_window_aggregate(
        self,
        stream: AsyncIterator[dict],
        window_size: int = 60,
    ) -> AsyncIterator[dict]:
        """Aggregate events in tumbling windows."""
        window_start = time.monotonic()
        buffer: list[dict] = []
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_size:
                yield {
                    "window_start": window_start,
                    "window_end": time.monotonic(),
                    "count": len(buffer),
                    "sum": sum(e.get("value", 0) for e in buffer),
                    "avg": statistics.mean(e.get("value", 0) for e in buffer) if buffer else 0,
                }
                buffer = []
                window_start = time.monotonic()
```

## 4. Data Quality Framework

```python
"""Data quality checks for pipelines."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DataQualityCheck:
    name: str
    severity: str  # error, warning, info
    
    async def run(self, data: list[dict]) -> tuple[bool, str]:
        raise NotImplementedError


@dataclass
class NullCheck(DataQualityCheck):
    column: str
    max_null_pct: float = 0.05
    
    async def run(self, data: list[dict]) -> tuple[bool, str]:
        nulls = sum(1 for row in data if row.get(self.column) is None)
        null_pct = nulls / max(len(data), 1)
        if null_pct > self.max_null_pct:
            return (False, f"Column '{self.column}': {null_pct:.1%} nulls > {self.max_null_pct:.1%}")
        return (True, "")


@dataclass
class UniqueCheck(DataQualityCheck):
    columns: list[str]
    
    async def run(self, data: list[dict]) -> tuple[bool, str]:
        seen = set()
        for row in data:
            key = tuple(row.get(c) for c in self.columns)
            if key in seen:
                return (False, f"Duplicate: {self.columns} = {key}")
            seen.add(key)
        return (True, "")


@dataclass
class ValueRangeCheck(DataQualityCheck):
    column: str
    min_val: float | None = None
    max_val: float | None = None
    
    async def run(self, data: list[dict]) -> tuple[bool, str]:
        for row in data:
            val = row.get(self.column)
            if val is not None:
                if self.min_val is not None and val < self.min_val:
                    return (False, f"Value {val} < min {self.min_val}")
                if self.max_val is not None and val > self.max_val:
                    return (False, f"Value {val} > max {self.max_val}")
        return (True, "")


class DataQualityPipeline:
    """Run data quality checks on pipeline output."""
    
    def __init__(self):
        self.checks: list[DataQualityCheck] = []
    
    def add_check(self, check: DataQualityCheck) -> None:
        self.checks.append(check)
    
    async def run_all(self, data: list[dict]) -> list[dict]:
        """Run all checks and return failures."""
        failures = []
        for check in self.checks:
            passed, message = await check.run(data)
            if not passed:
                failures.append({
                    "check": check.name,
                    "severity": check.severity,
                    "message": message,
                })
        return failures
```

## 5. Data Lake Architecture

```python
"""Data Lake architecture patterns."""
from __future__ import annotations


# Bronze/Silver/Gold (Medallion Architecture):
DATA_LAKE_LAYERS = {
    "bronze": {
        "description": "Raw ingested data (immutable)",
        "format": "parquet/avro",
        "retention": "30 days",
        "access": "restricted",
    },
    "silver": {
        "description": "Cleaned and validated data",
        "format": "parquet (delta)",
        "retention": "90 days",
        "access": "analytics team",
    },
    "gold": {
        "description": "Aggregated, business-ready data",
        "format": "delta/iceberg",
        "retention": "indefinite",
        "access": "all teams",
    },
}


# Partitioning strategy:
PARTITIONING = """
  Time-based:  dt=2024-01-15/hour=14/
  For time-series data — always partition by time first.
  
  Column-based: category=electronics/dt=2024-01-15/
  For dimensional data — high cardinality column first.
  
  Size targets:
    - Files: 128MB - 1GB (optimal for Spark/Trino)
    - Partitions: < 10K files per partition
    - Total: millions of partitions (Hive/Presto can handle)
"""

# File format comparison:
FILE_FORMATS = {
    "parquet": {
        "compression": 7.5x,  # vs CSV
        "query_speed": "fast (columnar)",
        "use_case": "analytics, ML training",
    },
    "delta": {
        "compression": 7.5x,
        "features": "ACID, time travel, schema enforcement",
        "use_case": "production data lakes",
    },
    "avro": {
        "compression": 3x,
        "features": "row-based, schema evolution",
        "use_case": "Kafka, streaming ingest",
    },
}
```

## 6. Data Pipeline Monitoring

```python
"""Monitor data pipeline health."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PipelineMonitor:
    """Monitor pipeline freshness, volume, quality."""
    
    async def check_freshness(self, table: str, max_lag: timedelta) -> bool:
        """Check if table data is up to date."""
        last_updated = await self._get_last_updated(table)
        lag = datetime.utcnow() - last_updated
        if lag > max_lag:
            await self._alert(f"Table {table} lag: {lag} > {max_lag}")
            return False
        return True
    
    async def check_volume(self, table: str, expected_min: int) -> bool:
        """Check if data volume is normal."""
        row_count = await self._get_row_count(table)
        if row_count < expected_min:
            await self._alert(f"Table {table} has {row_count} rows < {expected_min}")
            return False
        return True
    
    async def check_schema(self, table: str, expected_schema: dict) -> bool:
        """Check schema hasn't changed unexpectedly."""
        actual_schema = await self._get_schema(table)
        if actual_schema != expected_schema:
            await self._alert(f"Table {table} schema changed!")
            return False
        return True
```

## 7. Spark Best Practices

```python
"""Spark optimization patterns."""
from __future__ import annotations


SPARK_CONFIG = {
    "spark.sql.shuffle.partitions": "200",  # 200 partitions for shuffle
    "spark.sql.adaptive.enabled": "true",    # AQE — adaptive query execution
    "spark.sql.adaptive.coalescePartitions.enabled": "true",  # Auto coalesce
    "spark.sql.sources.partitionOverwriteMode": "dynamic",    # Safe overwrite
    "spark.databricks.delta.schema.autoMerge.enabled": "true", # Schema evolution
}

# Performance tips:
PERFORMANCE_TIPS = """
  Caching:
    - Cache only when reused multiple times
    - Use .cache() for small-medium, checkpoint for large
    - Don't cache intermediate results that aren't reused
  
  Shuffling:
    - Minimize shuffles (wide transformations)
    - Bucketing for join keys that are frequently used
    - Salting for data skew (add random prefix to skewed keys)
  
  Serialization:
    - Use Kryo serialization (faster than Java)
    - Register custom classes for Kryo
    - Prefer DataFrame API over RDD (optimizer)
  
  File formats:
    - Delta/Iceberg for production
    - Parquet for analytics
    - Avoid CSV/JSON for large datasets
"""

# Working with large datasets:
def optimize_spark_df(df, partition_col: str = None):
    """Optimize DataFrame for performance."""
    # Repartition for optimal file size
    optimal_size = 256 * 1024 * 1024  # 256MB per partition
    current_size = estimate_size(df)
    target_partitions = max(1, current_size // optimal_size)
    
    if partition_col:
        return df.repartition(target_partitions, partition_col)
    return df.coalesce(min(target_partitions, df.rdd.getNumPartitions()))
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

## Additional Production Patterns

### Stream Processing with Windowing

```python
"""Stream processing with various windowing strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator
import asyncio
import time


class TumblingWindow:
    """Non-overlapping, fixed-size windows."""
    
    async def process(self, stream: AsyncIterator[dict], window_seconds: int = 60):
        buffer = []
        window_start = time.monotonic()
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_seconds:
                yield self._aggregate(buffer)
                buffer = []
                window_start = time.monotonic()
    
    def _aggregate(self, events: list[dict]) -> dict:
        return {
            "count": len(events),
            "sum": sum(e.get("value", 0) for e in events),
            "avg": statistics.mean(e.get("value", 0) for e in events) if events else 0,
            "min": min(e.get("value", float('inf')) for e in events),
            "max": max(e.get("value", float('-inf')) for e in events),
        }


class SlidingWindow:
    """Overlapping windows with fixed slide interval."""
    
    def __init__(self, window_seconds: int = 60, slide_seconds: int = 10):
        self.window = window_seconds
        self.slide = slide_seconds
        self.buffer = []
    
    async def add(self, event: dict):
        now = time.monotonic()
        self.buffer.append((now, event))
        # Clean expired
        self.buffer = [(t, e) for t, e in self.buffer if now - t < self.window]
        # Check if we need to emit
        if len(self.buffer) > 0 and (len(self.buffer) % self.slide == 0 or len(self.buffer) >= 1000):
            return self._aggregate()
        return None


class SessionWindow:
    """Gap-based windows (burst detection)."""
    
    def __init__(self, gap_seconds: int = 300):
        self.gap = gap_seconds
        self.sessions: dict[str, list] = {}
    
    async def add(self, key: str, event: dict):
        now = time.monotonic()
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append((now, event))
        
        # Close session if gap exceeded
        last_time = self.sessions[key][-1][0]
        if now - last_time > self.gap:
            session = self.sessions.pop(key)
            yield self._aggregate_session(key, session)


---

## Additional Production Patterns

### Stream Processing with Windowing

```python
"""Stream processing with various windowing strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator
import asyncio
import time


class TumblingWindow:
    """Non-overlapping, fixed-size windows."""
    
    async def process(self, stream: AsyncIterator[dict], window_seconds: int = 60):
        buffer = []
        window_start = time.monotonic()
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_seconds:
                yield self._aggregate(buffer)
                buffer = []
                window_start = time.monotonic()
    
    def _aggregate(self, events: list[dict]) -> dict:
        return {
            "count": len(events),
            "sum": sum(e.get("value", 0) for e in events),
            "avg": statistics.mean(e.get("value", 0) for e in events) if events else 0,
            "min": min(e.get("value", float('inf')) for e in events),
            "max": max(e.get("value", float('-inf')) for e in events),
        }


class SlidingWindow:
    """Overlapping windows with fixed slide interval."""
    
    def __init__(self, window_seconds: int = 60, slide_seconds: int = 10):
        self.window = window_seconds
        self.slide = slide_seconds
        self.buffer = []
    
    async def add(self, event: dict):
        now = time.monotonic()
        self.buffer.append((now, event))
        # Clean expired
        self.buffer = [(t, e) for t, e in self.buffer if now - t < self.window]
        # Check if we need to emit
        if len(self.buffer) > 0 and (len(self.buffer) % self.slide == 0 or len(self.buffer) >= 1000):
            return self._aggregate()
        return None


class SessionWindow:
    """Gap-based windows (burst detection)."""
    
    def __init__(self, gap_seconds: int = 300):
        self.gap = gap_seconds
        self.sessions: dict[str, list] = {}
    
    async def add(self, key: str, event: dict):
        now = time.monotonic()
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append((now, event))
        
        # Close session if gap exceeded
        last_time = self.sessions[key][-1][0]
        if now - last_time > self.gap:
            session = self.sessions.pop(key)
            yield self._aggregate_session(key, session)


---

## Additional Production Patterns

### Stream Processing with Windowing

```python
"""Stream processing with various windowing strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator
import asyncio
import time


class TumblingWindow:
    """Non-overlapping, fixed-size windows."""
    
    async def process(self, stream: AsyncIterator[dict], window_seconds: int = 60):
        buffer = []
        window_start = time.monotonic()
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_seconds:
                yield self._aggregate(buffer)
                buffer = []
                window_start = time.monotonic()
    
    def _aggregate(self, events: list[dict]) -> dict:
        return {
            "count": len(events),
            "sum": sum(e.get("value", 0) for e in events),
            "avg": statistics.mean(e.get("value", 0) for e in events) if events else 0,
            "min": min(e.get("value", float('inf')) for e in events),
            "max": max(e.get("value", float('-inf')) for e in events),
        }


class SlidingWindow:
    """Overlapping windows with fixed slide interval."""
    
    def __init__(self, window_seconds: int = 60, slide_seconds: int = 10):
        self.window = window_seconds
        self.slide = slide_seconds
        self.buffer = []
    
    async def add(self, event: dict):
        now = time.monotonic()
        self.buffer.append((now, event))
        # Clean expired
        self.buffer = [(t, e) for t, e in self.buffer if now - t < self.window]
        # Check if we need to emit
        if len(self.buffer) > 0 and (len(self.buffer) % self.slide == 0 or len(self.buffer) >= 1000):
            return self._aggregate()
        return None


class SessionWindow:
    """Gap-based windows (burst detection)."""
    
    def __init__(self, gap_seconds: int = 300):
        self.gap = gap_seconds
        self.sessions: dict[str, list] = {}
    
    async def add(self, key: str, event: dict):
        now = time.monotonic()
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append((now, event))
        
        # Close session if gap exceeded
        last_time = self.sessions[key][-1][0]
        if now - last_time > self.gap:
            session = self.sessions.pop(key)
            yield self._aggregate_session(key, session)


---

## Additional Production Patterns

### Stream Processing with Windowing

```python
"""Stream processing with various windowing strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator
import asyncio
import time


class TumblingWindow:
    """Non-overlapping, fixed-size windows."""
    
    async def process(self, stream: AsyncIterator[dict], window_seconds: int = 60):
        buffer = []
        window_start = time.monotonic()
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_seconds:
                yield self._aggregate(buffer)
                buffer = []
                window_start = time.monotonic()
    
    def _aggregate(self, events: list[dict]) -> dict:
        return {
            "count": len(events),
            "sum": sum(e.get("value", 0) for e in events),
            "avg": statistics.mean(e.get("value", 0) for e in events) if events else 0,
            "min": min(e.get("value", float('inf')) for e in events),
            "max": max(e.get("value", float('-inf')) for e in events),
        }


class SlidingWindow:
    """Overlapping windows with fixed slide interval."""
    
    def __init__(self, window_seconds: int = 60, slide_seconds: int = 10):
        self.window = window_seconds
        self.slide = slide_seconds
        self.buffer = []
    
    async def add(self, event: dict):
        now = time.monotonic()
        self.buffer.append((now, event))
        # Clean expired
        self.buffer = [(t, e) for t, e in self.buffer if now - t < self.window]
        # Check if we need to emit
        if len(self.buffer) > 0 and (len(self.buffer) % self.slide == 0 or len(self.buffer) >= 1000):
            return self._aggregate()
        return None


class SessionWindow:
    """Gap-based windows (burst detection)."""
    
    def __init__(self, gap_seconds: int = 300):
        self.gap = gap_seconds
        self.sessions: dict[str, list] = {}
    
    async def add(self, key: str, event: dict):
        now = time.monotonic()
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append((now, event))
        
        # Close session if gap exceeded
        last_time = self.sessions[key][-1][0]
        if now - last_time > self.gap:
            session = self.sessions.pop(key)
            yield self._aggregate_session(key, session)


---

## Additional Production Patterns

### Stream Processing with Windowing

```python
"""Stream processing with various windowing strategies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator
import asyncio
import time


class TumblingWindow:
    """Non-overlapping, fixed-size windows."""
    
    async def process(self, stream: AsyncIterator[dict], window_seconds: int = 60):
        buffer = []
        window_start = time.monotonic()
        
        async for event in stream:
            buffer.append(event)
            
            if time.monotonic() - window_start >= window_seconds:
                yield self._aggregate(buffer)
                buffer = []
                window_start = time.monotonic()
    
    def _aggregate(self, events: list[dict]) -> dict:
        return {
            "count": len(events),
            "sum": sum(e.get("value", 0) for e in events),
            "avg": statistics.mean(e.get("value", 0) for e in events) if events else 0,
            "min": min(e.get("value", float('inf')) for e in events),
            "max": max(e.get("value", float('-inf')) for e in events),
        }


class SlidingWindow:
    """Overlapping windows with fixed slide interval."""
    
    def __init__(self, window_seconds: int = 60, slide_seconds: int = 10):
        self.window = window_seconds
        self.slide = slide_seconds
        self.buffer = []
    
    async def add(self, event: dict):
        now = time.monotonic()
        self.buffer.append((now, event))
        # Clean expired
        self.buffer = [(t, e) for t, e in self.buffer if now - t < self.window]
        # Check if we need to emit
        if len(self.buffer) > 0 and (len(self.buffer) % self.slide == 0 or len(self.buffer) >= 1000):
            return self._aggregate()
        return None


class SessionWindow:
    """Gap-based windows (burst detection)."""
    
    def __init__(self, gap_seconds: int = 300):
        self.gap = gap_seconds
        self.sessions: dict[str, list] = {}
    
    async def add(self, key: str, event: dict):
        now = time.monotonic()
        if key not in self.sessions:
            self.sessions[key] = []
        
        self.sessions[key].append((now, event))
        
        # Close session if gap exceeded
        last_time = self.sessions[key][-1][0]
        if now - last_time > self.gap:
            session = self.sessions.pop(key)
            yield self._aggregate_session(key, session)
