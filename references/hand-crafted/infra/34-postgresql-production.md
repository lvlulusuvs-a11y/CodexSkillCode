# PostgreSQL in Production

Running PostgreSQL at scale requires care.

## Connection Pooling

Use pgbouncer or built-in pooling.

pgbouncer.ini:
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
default_pool_size = 50
max_client_conn = 200
listen_port = 6432

pgbouncer pools connections at the transaction level.
This means 200 clients can share 50 database connections.

## Monitoring

Key metrics to track:

1. Connections (active, idle, waiting)
2. Transaction rate (commits, rollbacks per second)
3. Cache hit ratio (should be > 99%)
4. Index usage (unused indexes waste writes)
5. Query performance (slow queries, temp files)
6. Replication lag (critical for HA)
7. Deadlocks (should be zero)
8. Table bloat (autovacuum effectiveness)

SELECT pg_size_pretty(pg_database_size(current_database()));

## Vacuum and Analyze

Autovacuum settings:

autovacuum_vacuum_scale_factor = 0.01
autovacuum_analyze_scale_factor = 0.05
autovacuum_vacuum_threshold = 1000
autovacuum_naptime = 60

Monitor autovacuum progress:

SELECT query, state, wait_event
FROM pg_stat_activity
WHERE query ILIKE '%autovacuum%';

## Backup Strategy

1. Daily pg_dump (logical backup)
2. Continuous WAL archiving (point-in-time recovery)
3. Streaming replication (standby for failover)

pg_dump -Fc mydb > mydb.dump
pg_restore -d mydb mydb.dump

## Common Issues

1. Connection leaks (connections not returned to pool)
2. Slow queries (missing indexes)
3. Table bloat (autovacuum falling behind)
4. Replication lag (high write load)
5. Lock contention (long transactions)
6. Out of memory (work_mem too high)


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.
