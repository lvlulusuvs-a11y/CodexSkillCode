# ADR 002: Use Redis for Caching and Rate Limiting

Status: Accepted

## Context

We need a fast, in-memory data store for:
- Session management
- API rate limiting
- Data caching (product catalog, user profiles)
- Distributed locks for race condition prevention

Requirements: sub-millisecond latency, high throughput, data persistence option.

## Decision

Use Redis 7 for caching, rate limiting, and distributed coordination.

## Rationale

1. Sub-millisecond latency for cache reads
2. Rich data structures (strings, hashes, sets, sorted sets, streams)
3. Built-in replication and clustering
4. Persistence options (RDB snapshots, AOF logs)
5. Lua scripting for atomic operations
6. Pub/Sub for lightweight messaging
7. TTL support for automatic cache invalidation
8. Mature client libraries for all languages

## Considered Alternatives

Memcached: Faster but less features (no persistence, data structures).
DragonflyDB: Newer, higher performance, but less proven in production.
KeyDB: Redis fork with multi-threading, smaller community.

## Redis Configuration

maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
requirepass ${REDIS_PASSWORD}

## Data Usage

Sessions: SESSION:{session_id} -> JSON, TTL 24h
Rate limits: RL:{ip}:{endpoint} -> Sorted Set, TTL 60s
Cache: CACHE:{key} -> JSON, TTL varies
Locks: LOCK:{resource} -> String, TTL 30s
Queues: QUEUE:{name} -> List


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.
