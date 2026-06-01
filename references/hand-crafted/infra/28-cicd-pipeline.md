# CI/CD Pipeline Design

A good pipeline catches errors early and deploys safely.

## Pipeline Stages

Stage 1: Lint and Format
- ruff check .
- ruff format --check .
- mypy .

Stage 2: Unit Tests
- pytest tests/unit/
- Coverage > 80%

Stage 3: Build
- Docker build
- Image tag with commit SHA

Stage 4: Integration Tests
- Docker compose up
- pytest tests/integration/

Stage 5: Security Scan
- trivy image scan
- dependency check

Stage 6: Deploy to Staging
- kubectl apply
- Smoke tests

Stage 7: Deploy to Production
- Gradual rollout (10% -> 50% -> 100%)
- Monitor errors and latency

## GitHub Actions Example

name: CI/CD
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: pip install -r requirements.txt
    - run: ruff check .
    - run: pytest --cov=src tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - run: echo "Deploying..."

## Pipeline Gates

Automatic gates:
- All tests pass
- Coverage threshold met
- No critical vulnerabilities
- Build succeeds

Manual gates:
- Production deployment approval
- Database migration approval
- Feature flag enabled

## Deployment Strategies

Rolling update: Zero downtime, gradual replacement.
Blue-green: Two identical environments, switch traffic.
Canary: Small percentage of users get new version.

## What Makes a Good Pipeline

1. Fast feedback (under 10 minutes)
2. Reliable (no flaky tests)
3. Secure (no secrets in logs)
4. Self-service (devs can deploy independently)
5. Observable (clear status and logs)


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.


## Additional Notes

Apply this concept in your project.

### Key Takeaway

Good patterns solve real problems. Bad patterns add complexity.

### Exercise

Write a test for this pattern today.
