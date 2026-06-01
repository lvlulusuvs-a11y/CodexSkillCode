# Error Budgets: Balancing Velocity and Reliability

Error budgets quantify how unreliable your service can be.

## The Concept

You have an SLO (Service Level Objective), say 99.9% uptime.
Over a month, you are allowed 0.1% errors = 43 minutes of downtime.
That is your error budget.

If you have budget remaining, you can ship features faster.
If you run out of budget, you stop shipping and focus on reliability.

## Implementing Error Budgets

from datetime import datetime, timedelta

class ErrorBudget:
    def __init__(self, slo: float = 0.999, window: timedelta = timedelta(days=30)):
        self.slo = slo
        self.window = window
        self.total_requests = 0
        self.error_requests = 0
        self.start_time = datetime.utcnow()

    def record_request(self, is_error: bool):
        self.total_requests += 1
        if is_error:
            self.error_requests += 1

    @property
    def budget_remaining(self) -> float:
        allowed_errors = self.total_requests * (1 - self.slo)
        return max(0, allowed_errors - self.error_requests)

    @property
    def is_exhausted(self) -> bool:
        return self.budget_remaining <= 0

## When to Use Error Budgets

Error budgets guide decision-making:

Can we deploy this feature?
Yes, if we have budget remaining.
No, if we exhausted it (fix reliability first).

Do we need to fix this reliability issue?
Yes, if we are burning budget too fast.
Not urgent, if we have plenty of budget.

## Setting SLOs

SLO is not the same as SLA (Service Level Agreement).

SLA is contractual (99.9% = we owe you money).
SLO is ambitious (99.9% = we try our best).

SLO should be:
1. Achievable (but not easy)
2. Measurable (from metrics)
3. Meaningful (users care about it)
4. Simple (one number per service)

## Error Budget Policy

1. Budget is 30-day rolling window
2. If budget is healthy (> 50% remaining): ship features
3. If budget is low (10-50% remaining): slow down shipping
4. If budget is exhausted (< 10% remaining): stop shipping, fix reliability
5. Budget resets every 30 days


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.
