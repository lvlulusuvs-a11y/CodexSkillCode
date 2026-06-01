# Writing Technical Documentation

Good documentation separates professional engineering teams from amateurs.

## What to Document

1. Architecture decisions (ADRs)
2. API contracts (OpenAPI)
3. Runbooks (how to handle incidents)
4. Onboarding (how to set up dev environment)
5. Coding standards (team conventions)
6. System architecture (how things connect)

## Architecture Decision Records

ADR format:
Title: ADR-001: Use PostgreSQL
Status: Accepted | Proposed | Deprecated
Context: Why we need to make this decision
Decision: What we decided
Consequences: What this means for the project

Keep ADRs short (one page) and to the point.
They document WHY you made a decision, not just WHAT you decided.

## Runbook Format

Title: High CPU Alert on Payment Service
Severity: SEV2
Steps:
1. Check if its a traffic spike (check Grafana)
2. Check for slow queries (pg_stat_statements)
3. Check for connection pool exhaustion
4. Scale up if needed (kubectl scale)
5. If persists, restart the service
Escalation: Contact platform team if unresolved in 15 minutes

## API Documentation

Generate from code (OpenAPI/Swagger):
- FastAPI generates automatically
- Document request/response formats
- Include error codes and examples
- Add authentication details

## Code Documentation

Dont document the obvious:

BAD: # This adds two numbers
def add(a, b): return a + b

GOOD: # This function exists because the standard sum()
# doesnt handle large numbers correctly (we tested).
# See bug: ISSUE-1234
def add(a, b): return a + b

## Documentation Maintenance

1. Document as you code (not after)
2. Review docs in PRs
3. Test runbooks annually
4. Archive outdated docs
5. Keep a single source of truth


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.


## Practice

Use one insight from this.
