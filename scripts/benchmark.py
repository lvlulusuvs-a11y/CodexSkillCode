#!/usr/bin/env python3
"""Простой бенчмарк для замера времени выполнения функций."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


def measure(name: str = "", iterations: int = 1000) -> Callable:
    """Декоратор для замера времени."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            label = name or func.__name__
            start = time.perf_counter()
            result = None
            for _ in range(iterations):
                result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            avg = elapsed / iterations * 1_000_000
            print(f"  {label}: {elapsed:.4f}s всего, {avg:.2f}µs в среднем "
                  f"({iterations} итераций)")
            return result
        return wrapper
    return decorator


def compare(funcs: list[tuple[str, Callable]], *args: Any, **kwargs: Any) -> None:
    """Сравнить несколько функций."""
    iterations = kwargs.pop("iterations", 10000)
    print(f"Сравнение ({iterations} итераций):")
    results: list[tuple[str, float]] = []

    for name, func in funcs:
        start = time.perf_counter()
        for _ in range(iterations):
            func(*args, **{k: v for k, v in kwargs.items() if k != "iterations"})
        elapsed = time.perf_counter() - start
        results.append((name, elapsed))

    results.sort(key=lambda x: x[1])
    fastest = results[0][1]

    for name, elapsed in results:
        ratio = elapsed / fastest if fastest > 0 else 1
        print(f"  {name}: {elapsed:.4f}s (x{ratio:.2f})")

    print(f"\n  🏆 Быстрейший: {results[0][0]}")
EOF

cat > /root/.shared-skills/mega-coding/scripts/setup-dev.sh << 'BASH'
#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Установка dev-окружения mega-coding..."

# Python
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# pre-commit
pip install pre-commit
pre-commit install

# Git hooks
if [ -d scripts/git-hooks ]; then
    cp scripts/git-hooks/* .git/hooks/
    chmod +x .git/hooks/*
fi

echo "✅ Готово"
BASH
chmod +x /root/.shared-skills/mega-coding/scripts/setup-dev.sh

cat > /root/.shared-skills/mega-coding/scripts/git-hooks/pre-commit << 'BASH'
#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Pre-commit: mega-coding check..."

# staged .py файлы
staged=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
if [ -z "$staged" ]; then
    exit 0
fi

# линтинг
for f in $staged; do
    if [ -f "$f" ]; then
        python3 -c "
import ast
try:
    with open('$f') as fh:
        ast.parse(fh.read())
    print(f'  ✅ $f')
except SyntaxError as e:
    print(f'  ❌ $f: {e}')
    exit(1)
" || exit 1
    fi
done

echo "✅ Pre-commit check passed"
BASH
chmod +x /root/.shared-skills/mega-coding/scripts/git-hooks/pre-commit
echo "scripts batch 2 done"
