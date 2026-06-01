# ADR 007: Use Testcontainers for Integration Tests

Status: Accepted

## Context

We need real dependencies in integration tests.
Mocking databases and queues causes false positives.

## Decision

Use Testcontainers for all integration tests.

## Rationale

1. Real dependencies - PostgreSQL, Redis, Kafka in tests
2. Ephemeral - containers are created and destroyed per test run
3. Fast for local dev - containers start in seconds
4. CI-compatible - works with Docker in CI
5. Language-native - use from Python, Go, Java, etc.

## Implementation

@pytest.mark.asyncio
async def test_create_order():
    with PostgresContainer("postgres:16") as pg:
        pool = await asyncpg.create_pool(pg.get_connection_url())
        repo = PostgresOrderRepository(pool)
        service = OrderService(repo)

        order = await service.create(...)
        assert order.id is not None

## Consequences

Positive:
- Tests match production behavior
- No mocking of databases or queues
- Reproducible across environments

Negative:
- Requires Docker
- Slower than unit tests
- Resource usage in CI


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.
