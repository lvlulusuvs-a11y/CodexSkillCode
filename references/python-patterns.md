# Python patterns

## Структура модуля
```python
"""Module docstring."""

from __future__ import annotations

import logging
from typing import override

logger = logging.getLogger(__name__)


class MyClass:
    """Public class."""
    ...
```

## Обработка ошибок
```python
class AppError(Exception):
    """Base exception for the app."""

class NotFoundError(AppError):
    """Resource not found."""

def get_user(user_id: int) -> User:
    if not (user := db.query(User).get(user_id)):
        raise NotFoundError(f"User {user_id} not found")
    return user
```

## Тесты с pytest
```python
import pytest
from unittest.mock import Mock

def test_something():
    result = my_func("input")
    assert result == "expected"
    assert mock_dep.call_count == 1
```

## CLI с argparse
```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    ...
```

# Mega-Coding Principal Engineer Edition
# Extended configuration and reference content

# ---------------------------------------------------------------------------
# This file is part of the Mega-Coding skill — Principal Engineer Edition.
# It provides production-grade patterns and configurations for Big Tech
# development. All tools, scripts, and references are designed to work
# together to provide maximum code quality and developer productivity.
#
# Key principles:
# - Production-first mindset
# - Observability by default
# - Resilience in all components
# - Security at every layer
# - Trade-off awareness in all decisions
# - Platform thinking over point solutions
#
# Version: 3.0.0
# Last updated: 2026-05-30
# Contact: @intarktelegram
# ---------------------------------------------------------------------------

# Key Metrics to Track:
# - Code health score (0-100)
# - Test coverage percentage
# - Average function complexity
# - Type hint coverage ratio
# - Documentation coverage
# - Security vulnerability count
# - Dead code percentage

# References:
# See references/extra/ for 60+ production patterns
# See references/languages/ for Go, TypeScript, Rust patterns
# See references/infra/ for Kubernetes and Kafka patterns
# See references/battle-scars/ for real production war stories
# See references/principal-engineer-handbook.md for full leadership guide

# Tools:
# - python scripts/mega.py — Unified CLI (lint, review, check, metrics, ci)
# - python scripts/tree-voting/evaluate.py — Trees Club code evaluation
# - python metrics/quality-metrics.py — Quality metrics & diff analysis
# - python scripts/code-review-bot.py — Automated code review
# - make ci — Full CI pipeline
