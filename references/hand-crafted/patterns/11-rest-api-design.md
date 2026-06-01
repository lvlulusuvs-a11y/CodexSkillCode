# REST API Design: What Actually Works

I have designed, consumed, and regretted dozens of REST APIs.
Here is what I have learned.

## Resource Naming

Use plural nouns. Max 2 levels of nesting. No verbs in URLs.

```
# Good
GET    /users
GET    /users/{id}
POST   /users
PATCH  /users/{id}
DELETE /users/{id}
GET    /users/{id}/orders
GET    /users/{id}/orders/{order_id}

# Bad
GET    /getUsers
POST   /createUser
DELETE /removeUser/{id}
GET    /user_list
POST   /user_creation
POST  /users/123/orders/create
```

Verbs in URLs are redundant. HTTP methods are already verbs.

## HTTP Methods Semantics

```
GET     - retrieve a resource (safe, idempotent)
POST    - create a resource (non-idempotent)
PUT     - full replace (idempotent)
PATCH   - partial update (idempotent)
DELETE  - delete (idempotent)
```

POST vs PUT: POST creates with server-generated ID. PUT creates/updates with client-provided ID.

## Status Codes

Success:
200 - GET, PATCH successful
201 - POST created
204 - DELETE successful, no body

Client Errors:
400 - bad request
401 - unauthenticated
403 - forbidden
404 - not found
409 - conflict (duplicate)
422 - validation error
429 - rate limited

Server Errors:
500 - internal error
502 - bad gateway
503 - service unavailable
504 - gateway timeout

## Error Response Format

Each error is a machine-readable JSON:

```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Email is not valid",
        "details": {
            "field": "email",
            "value": "not-an-email",
            "constraint": "format"
        },
        "request_id": "req_abc123"
    }
}
```

- code: machine-readable (client can check this)
- message: human-readable
- details: field-level errors
- request_id: for debugging

## Pagination

Always use cursor-based pagination. Never OFFSET (its slow on large datasets).

```python
# Request
GET /users?cursor=abc123&limit=20

# Response
{
    "data": [
        {"id": "user_001", "name": "Alice"},
        {"id": "user_002", "name": "Bob"}
    ],
    "paging": {
        "next_cursor": "def456",
        "has_more": true
    }
}
```

## Filtering and Sorting

```python
# Filtering
GET /orders?status=active&created_at.gte=2026-01-01

# Sorting (prefix: +asc, -desc)
GET /orders?sort=-created_at,+status

# Field selection
GET /users?fields=id,name,email
```

## Versioning

Two approaches:

```python
# URL versioning (simple, my preference)
GET /v1/users
GET /v2/users

# Header versioning (more RESTful)
GET /users
Accept: application/vnd.myapp.v2+json
```

URL versioning is simpler. Header versioning is cleaner for fine-grained control.

I use URL versioning for major versions, header for minor/canary.

## What I Avoid

- **HATEOAS** - nobody uses the links, overhead without benefit
- **GraphQL for public APIs** - too much complexity for external consumers
- **PUT for partial updates** - thats what PATCH is for
- **Nested resources deeper than 2 levels** - use query parameters instead

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |
