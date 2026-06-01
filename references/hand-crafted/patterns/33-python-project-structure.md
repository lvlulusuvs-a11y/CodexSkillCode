# Python Project Structure: Organize for Growth

Project structure affects maintainability more than people admit.

## Standard Structure

project/
  src/
    mypackage/
      __init__.py
      models/
        __init__.py
        user.py
        order.py
      repositories/
        __init__.py
        user_repository.py
        order_repository.py
      services/
        __init__.py
        user_service.py
        order_service.py
      api/
        __init__.py
        v1/
          __init__.py
          users.py
          orders.py
      config.py
      database.py
      main.py
  tests/
    __init__.py
    conftest.py
    test_models/
    test_repositories/
    test_services/
    test_api/
  migrations/
  docs/
  scripts/
  pyproject.toml
  README.md
  Dockerfile

## Why src/ Layout

1. Prevents import confusion (pip install -e .)
2. Tests import the package, not relative paths
3. Clear separation between code and configuration
4. Package is self-contained

## Module Organization

1. One module per concept
2. Keep modules small (< 500 lines)
3. Split large modules into packages
4. Avoid circular imports (use DI to break cycles)
5. Public API is in __init__.py

## Dependencies

Make dependencies explicit:

# pyproject.toml
[project]
name = "myproject"
version = "0.1.0"
dependencies = [
    "fastapi>=0.110",
    "sqlalchemy>=2.0",
    "asyncpg>=0.29",
    "pydantic>=2.7",
    "httpx>=0.27",
    "structlog>=24.1",
]


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.


## Takeaway

Use one insight today.
