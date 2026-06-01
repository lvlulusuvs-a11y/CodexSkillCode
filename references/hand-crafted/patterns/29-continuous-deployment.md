# Continuous Deployment: Ship Every Change

Continuous deployment means every commit goes to production automatically.
It is the pinnacle of DevOps maturity.

## Prerequisites

Before you can deploy continuously, you need:

1. Automated tests that are fast (< 10 min) and reliable
2. Feature flags to disable broken features
3. Database migrations that dont require downtime
4. Monitoring that detects problems within seconds
5. Rollback mechanism that works instantly

## Deployment Pipeline

1. Developer pushes code
2. CI runs lint, type check, unit tests (3 min)
3. CI runs integration tests (5 min)
4. Build Docker image (2 min)
5. Deploy to staging (1 min)
6. Smoke tests on staging (2 min)
7. Deploy to production (gradual)
8. Monitor for 10 minutes

Total: ~25 minutes from push to production.

## Gradual Rollout

Deploy in stages:

Stage 1: 1% of traffic (2 min)
Stage 2: 10% of traffic (2 min)
Stage 3: 50% of traffic (2 min)
Stage 4: 100% of traffic (2 min)

At each stage, monitor:
- Error rate (< baseline + 0.1%)
- Latency (< baseline + 10%)
- Business metrics (revenue, conversion)

If any metric degrades, rollback immediately.

## Canary Deployments

Use Istio or similar for traffic splitting:

apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  hosts:
  - my-service
  http:
  - match:
    - headers:
        x-canary: "true"
    route:
    - destination:
        host: my-service-canary
        weight: 100
  - route:
    - destination:
        host: my-service-stable
        weight: 90
    - destination:
        host: my-service-canary
        weight: 10

## Rollback Strategy

Rollback is not a failure. Rollback is the safety net.

1. Keep the previous version deployed
2. Switch traffic back on metrics degradation
3. Investigate the failure
4. Fix and redeploy

git revert HEAD
git push
# CI/CD automatically builds and deploys

## Key Metrics for CD

- Deployment frequency (how often do you deploy?)
- Lead time (how long from commit to production?)
- Change failure rate (what % of deployments fail?)
- Time to restore (how long to recover from failure?)

Elite performers: multiple deploys per day, < 1 hour lead time,
< 5% failure rate, < 1 hour restore time.


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
