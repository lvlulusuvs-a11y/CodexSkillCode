# ADR 008: Use Sentry for Error Tracking

Status: Accepted

## Context

We need real-time error tracking and alerting.
Spreadsheet monitoring is not acceptable.

## Decision

Use Sentry for production error tracking.

## Rationale

1. Real-time error aggregation
2. Stack traces with context (request, user, environment)
3. Performance monitoring (tracing)
4. Release tracking (which version introduced the error)
5. Integrations (Slack, PagerDuty, JIRA)
6. Self-hosted or cloud option
7. Free tier for small teams

## Integration

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of requests traced
    environment=os.environ.get("APP_ENV", "development"),
    release=VERSION,
)

## What Sentry Catches

1. Unhandled exceptions
2. Logged errors
3. Performance issues
4. Slow database queries
5. Third-party API failures
6. Queue processing failures


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.
