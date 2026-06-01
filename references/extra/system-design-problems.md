# System Design Problems: Complete Solutions

**Real system design problems with complete solutions. Interview-prep + production depth.**

---

## 1. Design URL Shortener (bit.ly)

### Requirements
- Create shortened URLs
- Redirect to original URL
- Analytics (click count, referrer, geography)
- 100M URLs created/month
- 10B redirects/month

### Data Model

```sql
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_key VARCHAR(10) UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_short_key ON urls(short_key);

CREATE TABLE click_events (
    id BIGSERIAL,
    short_key VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP DEFAULT NOW(),
    referrer TEXT,
    user_agent TEXT,
    ip_address INET,
    country VARCHAR(2),
    device_type VARCHAR(20)
) PARTITION BY RANGE (clicked_at);
```

### Key Generation

```python
"""URL shortening strategies."""
from __future__ import annotations

import base64
import hashlib
import struct


def base62_encode(num: int) -> str:
    """Encode number to base62 (a-Z, 0-9)."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if num == 0:
        return chars[0]
    result = []
    while num > 0:
        result.append(chars[num % 62])
        num //= 62
    return "".join(reversed(result))


def generate_key(url: str, salt: str = "") -> str:
    """Generate 7-char key from URL.
    
    62^7 = 3.5 trillion combinations — enough for years.
    """
    hash_val = hashlib.md5(f"{url}{salt}".encode()).hexdigest()
    # Take first 8 bytes → int → base62
    num = struct.unpack(">Q", hash_val[:8].encode())[0]
    return base62_encode(num)[:7]


def check_collision(key: str, existing: set[str]) -> str:
    """Handle collision — add salt and retry."""
    salt = 0
    while key in existing:
        salt += 1
        key = generate_key(key, str(salt))
    return key
```

### Architecture

```text
Write path:
  Client → API Gateway → URL Service → PostgreSQL (urls table) → Kafka → Analytics

Read path:
  Client → CDN → Redis Cache → URL Service → PostgreSQL (cache miss fallback)

Redirect:
  301 (permanent) if no analytics needed
  302 (temporary) if tracking clicks

Cache:
  Redis: {short_key → original_url}
  TTL: 24 hours (most URLs accessed within first day)
  LRU eviction (hot URLs stay cached)
  Cache hit ratio: > 99%

Scaling:
  Writes: 100M/month = 38/sec → 1 DB instance
  Reads: 10B/month = 3800/sec → cache handles 99% → 38/sec to DB
```

## 2. Design Chat System (WhatsApp)

### Requirements
- 500M MAU
- 50B messages/day
- Real-time delivery < 100ms
- Multi-device sync
- End-to-end encryption
- Media sharing (images, video)

### Architecture

```text
Components:
  - WebSocket Gateway (connection management)
  - Message Service (routing + persistence)
  - Presence Service (online/offline)
  - Media Service (upload, CDN)
  - Notification Service (push)

Data flow:
  1. Sender → WebSocket Gateway → Message Service
  2. Message Service → Kafka (ordered per conversation)
  3. Consumer → Persist to Cassandra
  4. Consumer → WebSocket Gateway of recipients (if online)
  5. Consumer → Push Notification (if offline)
  6. Recipient → ACK → sender sees ✓✓

Storage:
  - Cassandra: messages (time-series, partition by conversation_id)
  - Redis: presence (TTL 30s), typing indicators (TTL 5s)
  - S3: media (images, videos, documents)
  - Elasticsearch: message search

Key Challenges:
  - Message ordering: sequence number per conversation_id
  - Multi-device sync: last-read-message-id
  - End-to-end encryption: Signal Protocol
  - Online/offline detection: heartbeat every 30s
```

### WebSocket Connection Manager

```python
"""WebSocket connection management at scale."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectionManager:
    """Manage millions of WebSocket connections."""
    _connections: dict[str, set[asyncio.Queue]] = field(
        default_factory=lambda: defaultdict(set)
    )
    
    async def connect(self, user_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._connections[user_id].add(queue)
        return queue
    
    async def disconnect(self, user_id: str, queue: asyncio.Queue) -> None:
        self._connections[user_id].discard(queue)
        if not self._connections[user_id]:
            del self._connections[user_id]
    
    async def send_to_user(self, user_id: str, message: dict) -> None:
        """Send message to all user's connections (multi-device)."""
        queues = self._connections.get(user_id, set())
        for queue in queues:
            await queue.put(message)
    
    async def broadcast_to_conversation(
        self, conversation_id: str, message: dict,
        user_map: dict[str, set[str]],  # conversation → users
    ) -> None:
        """Send message to all members of a conversation."""
        users = user_map.get(conversation_id, set())
        tasks = [self.send_to_user(uid, message) for uid in users]
        await asyncio.gather(*tasks)
```

### Message Persistence

```python
"""Time-series message storage with Cassandra."""
from __future__ import annotations

from dataclasses import dataclass


CREATE_MESSAGES_TABLE = """
CREATE TABLE messages_by_conversation (
    conversation_id UUID,
    message_id TIMEUUID,  -- TimeUUID for ordering
    sender_id UUID,
    message_type TEXT,  -- text, image, video, system
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMP,
    edited_at TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    PRIMARY KEY ((conversation_id), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC)
"""

CREATE_ATTACHMENT_INDEX = """
CREATE TABLE messages_by_user (
    user_id UUID,
    message_id TIMEUUID,
    conversation_id UUID,
    snippet TEXT,
    PRIMARY KEY ((user_id), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC)
"""
```

## 3. Design Payment System (Stripe-like)

### Requirements
- 10K transactions/sec
- 99.999% consistency
- Dual-write to multiple providers
- PCI-DSS compliant
- Fraud detection
- Global (multi-currency)

### State Machine

```python
"""Payment state machine."""
from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


class PaymentState(Enum):
    CREATED = auto()
    PROCESSING = auto()
    AUTHORIZED = auto()
    CAPTURED = auto()
    FAILED = auto()
    REFUNDED = auto()
    PARTIALLY_REFUNDED = auto()
    DISPUTED = auto()
    CANCELLED = auto()


VALID_TRANSITIONS = {
    PaymentState.CREATED: [PaymentState.PROCESSING, PaymentState.CANCELLED],
    PaymentState.PROCESSING: [PaymentState.AUTHORIZED, PaymentState.FAILED],
    PaymentState.AUTHORIZED: [PaymentState.CAPTURED, PaymentState.CANCELLED],
    PaymentState.CAPTURED: [PaymentState.REFUNDED, PaymentState.PARTIALLY_REFUNDED, PaymentState.DISPUTED],
    PaymentState.REFUNDED: [],
    PaymentState.FAILED: [],
    PaymentState.DISPUTED: [PaymentState.CAPTURED],  # Won dispute
    PaymentState.CANCELLED: [],
}


@dataclass
class Payment:
    id: str
    amount: int  # cents
    currency: str
    state: PaymentState
    provider: str  # stripe, adyen, etc.
    provider_payment_id: str
    idempotency_key: str
    metadata: dict
```

### Idempotency

```python
"""Idempotent payment processing."""
from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass


@dataclass
class IdempotentPaymentProcessor:
    """Process payments exactly-once using idempotency keys.
    
    Battle Scar: TCP retry caused double-payment. 
    Idempotency key: same key → same result (no charge).
    """
    
    async def process_payment(
        self,
        amount: int,
        currency: str,
        source: str,
        idempotency_key: str,
    ) -> PaymentResult:
        """Process payment idempotently."""
        # Check if already processed
        existing = await self._get_by_idempotency_key(idempotency_key)
        if existing:
            return PaymentResult(
                success=existing.state == PaymentState.CAPTURED,
                payment_id=existing.id,
                error=None if existing.state == PaymentState.CAPTURED else "payment_failed",
            )
        
        # Attempt payment through provider
        payment_id = str(uuid.uuid4())
        payment = Payment(
            id=payment_id,
            amount=amount,
            currency=currency,
            state=PaymentState.PROCESSING,
            provider="stripe",
            idempotency_key=idempotency_key,
        )
        
        await self._save_payment(payment)
        
        try:
            provider_result = await self.stripe_client.charge(
                amount=amount,
                currency=currency,
                source=source,
                idempotency_key=payment_id,
            )
            payment.state = PaymentState.CAPTURED
            payment.provider_payment_id = provider_result.id
            await self._update_payment(payment)
            return PaymentResult(success=True, payment_id=payment_id)
        except Exception as e:
            payment.state = PaymentState.FAILED
            await self._update_payment(payment)
            return PaymentResult(success=False, payment_id=payment_id, error=str(e))
```

### Reconciliation

```python
"""Daily payment reconciliation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReconciliationReport:
    """Match our records with provider records."""
    date: str
    our_payments: int
    provider_payments: int
    matched: int
    unmatched_ours: list[str]  # We have, provider doesn't
    unmatched_provider: list[str]  # Provider has, we don't
    amount_mismatches: list[tuple[str, int, int]]  # payment_id, our_amount, provider_amount
    
    @property
    def reconciliation_rate(self) -> float:
        return self.matched / max(self.our_payments, 1) * 100
```

## 4. Design Netflix-like Streaming

### Requirements
- 200M subscribers
- Petabytes of content
- Adaptive bitrate streaming
- Personalization
- Global CDN

### Video Processing Pipeline

```python
"""Video transcoding pipeline."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VideoProcessingPipeline:
    """Transcode videos to multiple bitrates."""
    
    # Supported qualities
    PROFILES = [
        {"name": "2160p", "bitrate": "16000k", "resolution": "3840x2160"},
        {"name": "1080p", "bitrate": "8000k", "resolution": "1920x1080"},
        {"name": "720p", "bitrate": "5000k", "resolution": "1280x720"},
        {"name": "480p", "bitrate": "2500k", "resolution": "854x480"},
        {"name": "360p", "bitrate": "1000k", "resolution": "640x360"},
    ]
    
    async def process_video(self, video_id: str, source_path: str) -> None:
        """Transcode and package for streaming."""
        # Step 1: Analyze source
        # Step 2: Transcode to each quality
        # Step 3: Generate HLS/DASH manifests
        # Step 4: Generate thumbnails
        # Step 5: Upload to CDN
        # Step 6: Update metadata
        pass


# CDN Caching Strategy:
# - Hot content: Edge servers (TTL: 24h)
# - Warm content: Regional cache (TTL: 7d)
# - Cold content: Origin only
# - Popularity-based pre-fetching

# Recommendation Engine:
# - Collaborative filtering: "Users who watched X also watched Y"
# - Content-based: Similar genres, actors, directors
# - Deep learning: Neural network embeddings
# - Real-time: Current trending
```

## 5. Design Distributed Database (Spanner-like)

### Requirements
- Global consistency
- Horizontal scaling
- SQL interface
- 99.999% availability

### TrueTime API (GPS + Atomic Clocks)

```python
"""TrueTime clock implementation for external consistency."""
from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TrueTime:
    """Synchronized clock using GPS + atomic clocks.
    
    Spread: 0-7ms (Spanner guarantees commit wait of spread).
    """
    gps_time: float
    atomic_time: float
    uncertainty_ms: float  # 0-7ms
    
    @property
    def earliest(self) -> float:
        return min(self.gps_time, self.atomic_time) - self.uncertainty_ms / 1000
    
    @property
    def latest(self) -> float:
        return max(self.gps_time, self.atomic_time) + self.uncertainty_ms / 1000
    
    def before(self, other: "TrueTime") -> bool:
        """Check if definitely before other."""
        return self.latest < other.earliest
```

## 6. Design Rate Limiter (Cloudflare-like)

### Distributed Rate Limiting

```python
"""Distributed rate limiter using Redis."""
from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DistributedRateLimiter:
    """Distributed rate limiter with sliding window.
    
    Can handle 1M+ rules across multiple datacenters.
    """
    
    redis: Any
    window_size: int = 60
    max_requests: int = 100
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed (atomic Lua script)."""
        lua = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local max_req = tonumber(ARGV[3])
        
        -- Clean old entries
        redis.call("ZREMRANGEBYSCORE", key, 0, now - window)
        
        -- Count current
        local count = redis.call("ZCARD", key)
        
        if count < max_req then
            redis.call("ZADD", key, now, now)
            redis.call("EXPIRE", key, window)
            return 1
        end
        
        return 0
        """
        
        result = await self.redis.eval(
            lua,
            [f"ratelimit:{key}"],
            [time.time(), self.window_size, self.max_requests]
        )
        return bool(result)
```

## 7. Design Real-Time Analytics Pipeline

### Lambda Architecture (Batch + Stream)

```python
"""Lambda architecture for analytics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Batch Layer (accurate, high latency)
class BatchProcessor:
    """Process historical data (Hourly/Daily)."""
    
    async def run_batch(self, date: str) -> None:
        # Read raw data from S3
        # Run Spark/MapReduce job
        # Write to ClickHouse/Redshift
        # Update materialized views
        pass


# Speed Layer (approximate, low latency)
class StreamProcessor:
    """Process real-time data (seconds delay)."""
    
    async def process_event(self, event: dict) -> None:
        # Kafka → Flink/Spark Streaming
        # Windowed aggregation (1min, 5min, 1h)
        # Update Redis counters
        # Push to dashboards
        pass


# Serving Layer (merged results)
class AnalyticsService:
    """Serve analytics queries."""
    
    async def get_metrics(
        self,
        metric: str,
        start_time: datetime,
        end_time: datetime,
        real_time: bool = False,
    ) -> dict[str, Any]:
        if real_time and end_time > datetime.utcnow() - timedelta(hours=1):
            # Mix batch + streaming for latest data
            batch = await self.batch_store.query(metric, start_time, end_time)
            stream = await self.stream_store.query(
                metric, 
                max(start_time, datetime.utcnow() - timedelta(hours=1)),
                end_time,
            )
            return self._merge_results(batch, stream)
        
        return await self.batch_store.query(metric, start_time, end_time)
```

## 8. Design Search Engine (Elasticsearch-like)

### Inverted Index

```python
"""Simple inverted index implementation."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
import math


@dataclass
class InvertedIndex:
    """Inverted index for full-text search."""
    _index: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    _doc_count: int = 0
    
    def add_document(self, doc_id: str, text: str) -> None:
        """Index document."""
        self._doc_count += 1
        words = set(text.lower().split())
        for word in words:
            self._index[word][doc_id] += 1
    
    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """TF-IDF based search."""
        words = query.lower().split()
        scores: dict[str, float] = defaultdict(float)
        
        for word in words:
            if word not in self._index:
                continue
            
            df = len(self._index[word])  # Document frequency
            idf = math.log(1 + (self._doc_count - df + 0.5) / (df + 0.5))
            
            for doc_id, tf in self._index[word].items():
                # BM25 score
                scores[doc_id] += idf * (tf * 1.5) / (tf + 1.5)
        
        return sorted(scores.items(), key=lambda x: -x[1])[:top_k]


# For production: Elasticsearch/Solr
# - Sharding for scale
# - Replication for HA
# - Near-real-time indexing (refresh_interval=1s)
# - Distributed search (scatter-gather)
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

## 9. Design Video Streaming Platform (YouTube/Netflix)

### Requirements
- 2B MAU (YouTube scale)
- 500 hours of video uploaded per minute
- Global streaming with < 5s startup latency
- Adaptive bitrate for varying network conditions
- Search, recommendations, comments, likes

### Video Processing Pipeline

```python
"""Video ingestion and processing pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio


VIDEO_PROCESSING_STEPS = """
  Upload → Transcode (HLS/DASH) → Thumbnails → CDN → Index
  
  1. Upload received via HTTP (resumable)
  2. Video split into chunks (10s each)
  3. Transcode to multiple bitrates (240p → 4K)
  4. Generate HLS/DASH manifests
  5. Generate thumbnails (every 5s + custom)
  6. Upload to CDN (multi-region)
  7. Index for search
  8. Extract audio → generate captions (speech-to-text)
  9. Content moderation (AI-based)
  10. Recommendation system indexing
"""


@dataclass
class TranscodingJob:
    """Video transcoding job specification."""
    video_id: str
    source_path: str
    target_profiles: list[str] = None
    
    PROFILES = {
        "2160p": {"bitrate": "16000k", "resolution": "3840x2160"},
        "1440p": {"bitrate": "12000k", "resolution": "2560x1440"},
        "1080p": {"bitrate": "8000k", "resolution": "1920x1080"},
        "720p": {"bitrate": "5000k", "resolution": "1280x720"},
        "480p": {"bitrate": "2500k", "resolution": "854x480"},
        "360p": {"bitrate": "1000k", "resolution": "640x360"},
    }


class Transcoder:
    """Distributed transcoding cluster.
    
    Architecture:
    - Job queue: RabbitMQ/Kafka
    - Workers: GPU instances (1000+)
    - Storage: S3-compatible (multi-region)
    - Scheduling: Custom based on priority and cost
    """
    
    async def process_video(self, video_id: str, source_url: str) -> str:
        """Process video through entire pipeline."""
        job_id = str(uuid.uuid4())
        
        # Step 1: Download source
        source_path = await self.download(source_url)
        
        # Step 2: Analyze source (resolution, codec, duration)
        analysis = await self.analyze(source_path)
        
        # Step 3: Create transcoding jobs
        jobs = []
        for profile_name in self._select_profiles(analysis):
            job = TranscodingJob(
                video_id=video_id,
                source_path=source_path,
                target_profiles=[profile_name],
            )
            jobs.append(job)
        
        # Step 4: Distribute to worker cluster
        results = await self.distribute_jobs(jobs)
        
        # Step 5: Generate HLS manifest
        manifest = self.generate_hls_manifest(results, analysis)
        
        # Step 6: Upload to CDN
        cdn_url = await self.upload_to_cdn(manifest, results)
        
        return cdn_url
```

### CDN Architecture

```python
"""Content delivery network for video streaming."""
from __future__ import annotations


CDN_HIERARCHY = """
  Tier 1 (Edge): 
    - 1000+ locations worldwide
    - Cache: popular content (last 24h views > 1M)
    - Cache size: 10TB per edge
  
  Tier 2 (Regional):
    - 50+ regional data centers
    - Cache: warm content (last 7d views > 100K)
    - Cache size: 100TB per region
  
  Tier 3 (Origin):
    - 3 primary data centers
    - All content
    - Storage: Petabyte scale (S3/Blob)
  
  Cache strategy:
    - Popular content: Edge (24h TTL)
    - Warm content: Regional (7d TTL)
    - Cold content: Origin only
    - Pre-fetch: Based on recommendation scores
"""
```

## 10. Design Distributed Cache (Redis Cluster)

### Sharding and Replication

```python
"""Redis cluster architecture at scale."""
from __future__ import annotations


REDIS_CLUSTER_DESIGN = """
  Sharding: 16384 hash slots
  - Keys are hashed → slot → node
  - Moves: reshard 1 slot at a time
  
  Replication: 1 master + 2 replicas per shard
  - Master: read/write
  - Replicas: read-only, failover target
  
  Sentinel: 3 nodes for high availability
  - Monitor master health
  - Auto-failover if master down
  
  Memory: 16GB per node (maxmemory)
  Eviction: allkeys-lru (most common)
  
  Cluster size: 100 nodes (50 masters + 50 replicas)
  Total memory: 800GB
  Throughput: 1M+ ops/sec
"""


@dataclass
class RedisOptimization:
    """Redis optimization patterns."""
    
    PIPELINING = """
      # Batch operations for throughput
      pipe = redis.pipeline()
      for key in keys:
          pipe.get(key)
      results = pipe.execute()
      # 10x faster than individual get
    """
    
    CACHING_PATTERNS = """
      # Cache-aside (lazy loading)
      def get_user(user_id):
          key = f"user:{user_id}"
          cached = redis.get(key)
          if cached:
              return json.loads(cached)
          user = db.get_user(user_id)
          redis.setex(key, 300, json.dumps(user))
          return user
      
      # Cache stampede protection
      # Use SET NX with TTL to let only one process compute
      
      # Write-through
      def update_user(user_id, data):
          db.update_user(user_id, data)
          redis.setex(f"user:{user_id}", 300, json.dumps(data))
    """
```

## 11. Design Monitoring System (Prometheus/Grafana)

### Metrics Collection Architecture

```python
"""Metrics pipeline at scale."""
from __future__ import annotations


MONITORING_ARCHITECTURE = """
  Collection:
    - Per-service: Prometheus client library
    - Pull model: Prometheus server scrapes /metrics endpoints
    - Push model: For batch jobs (Pushgateway)
  
  Storage:
    - Prometheus: Local TSDB (15d retention)
    - Thanos: Global view + long-term storage (S3)
    - Retention: 30d high-res, 1y downsampled
  
  Alerting:
    - Prometheus rules → AlertManager → PagerDuty/Slack
    - Alert fatigue: tune thresholds, aggregate similar alerts
    - SLO-based alerts: alert when burn rate is high
  
  Dashboards:
    - Grafana for visualization
    - Pre-built dashboards per service
    - RED metrics dashboard (Rate, Errors, Duration)
    - USE dashboard (Utilization, Saturation, Errors)
  
  Scaling:
    - 100K+ metrics series per Prometheus
    - Shard by team/service
    - Federation for global view
"""


@dataclass
class MonitoringSetup:
    """Production monitoring configuration."""
    
    SCRAPE_INTERVAL = "15s"
    EVALUATION_INTERVAL = "30s"
    
    ALERT_RULES = """
    groups:
      - name: service_health
        rules:
          - alert: HighErrorRate
            expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "High error rate ({{ $value | humanizePercentage }})"
          
          - alert: HighLatency
            expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "p99 latency {{ $value }}s"
    """
```
