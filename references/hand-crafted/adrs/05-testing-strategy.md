# ADR 005: Testing Strategy

Status: Accepted

## Context

We need a testing strategy that balances speed, reliability, and coverage.

## Decision

Follow the testing trophy, not the testing pyramid.

Unit tests: 40% of effort - test business logic in isolation
Integration tests: 40% of effort - test with real dependencies
E2E tests: 10% of effort - test critical user journeys
Manual testing: 10% of effort - exploratory UAT

## Framework

pytest for unit and integration tests.
Playwright for E2E tests.
Locust for performance tests.
chaostoolkit for resilience tests.

## Test Requirements

Unit tests: < 10ms per test, 100% of business logic
Integration tests: < 1s per test, 100% of API endpoints
E2E tests: < 30s per test, critical user flows
Coverage: > 85% lines, > 80% branches

## CI Integration

1. Lint and type check (2 min)
2. Unit tests (3 min)
3. Integration tests (5 min)
4. Build Docker image (2 min)
5. E2E tests (10 min)
6. Security scan (3 min)

Total CI time target: under 25 minutes.


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
