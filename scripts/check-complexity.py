#!/usr/bin/env python3
"""Анализ цикломатической сложности и вложенности функций."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

MAX_COMPLEXITY = 10
MAX_NESTING = 4


def _complexity(node: ast.AST) -> int:
    """Подсчёт цикломатической сложности."""
    score = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                               ast.And, ast.Or, ast.Assert)):
            score += 1
        elif isinstance(child, (ast.BoolOp, ast.IfExp)):
            score += len(child.values) - 1 if hasattr(child, 'values') else 1
    return score


def _nesting_depth(node: ast.AST) -> int:
    """Максимальная глубина вложенности."""
    max_depth = 0

    def walk(n: ast.AST, depth: int) -> None:
        nonlocal max_depth
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.For,
                           ast.While, ast.If, ast.Try, ast.With)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(n):
            walk(child, depth)

    walk(node, 0)
    return max_depth


def analyze(path: Path) -> list[tuple[int, str, str, int, int]]:
    issues: list[tuple[int, str, str, int, int]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cmp = _complexity(node)
        nd = _nesting_depth(node)
        flags = []
        if cmp > MAX_COMPLEXITY:
            flags.append(f"сложность {cmp}")
        if nd > MAX_NESTING:
            flags.append(f"вложенность {nd}")
        if flags:
            issues.append((node.lineno, node.name, ", ".join(flags), cmp, nd))
    return issues


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        issues = analyze(pyfile)
        for lineno, name, reason, cmp, nd in issues:
            print(f"{pyfile.relative_to(root_p)}:{lineno}: {name}: {reason}")
            total += 1

    print(f"\nФункций с превышением: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
