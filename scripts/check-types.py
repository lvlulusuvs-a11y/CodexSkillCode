#!/usr/bin/env python3
"""Проверка покрытия type hints в Python-коде."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def _has_type_annotation(node: ast.AST) -> bool:
    if isinstance(node, ast.FunctionDef):
        if node.returns is not None:
            return True
        for arg in node.args.args + node.args.kwonlyargs + node.args.posonlyargs:
            if arg.annotation is not None:
                return True
        if node.args.vararg and node.args.vararg.annotation:
            return True
        if node.args.kwarg and node.args.kwarg.annotation:
            return True
        return False
    elif isinstance(node, ast.AsyncFunctionDef):
        return _has_type_annotation(node)
    elif isinstance(node, ast.AnnAssign):
        return node.annotation is not None
    return True


def check_file(path: Path) -> list[tuple[int, str, str]]:
    issues: list[tuple[int, str, str]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            if not _has_type_annotation(node):
                issues.append((node.lineno, f"def {node.name}", "Нет type hints"))
        elif isinstance(node, ast.ClassDef):
            for item in ast.walk(node):
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    if not _has_type_annotation(item):
                        issues.append((item.lineno, f"{node.name}.__init__", "Нет type hints"))

    return issues


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        issues = check_file(pyfile)
        for lineno, func, msg in issues:
            print(f"{pyfile.relative_to(root_p)}:{lineno}: {func}: {msg}")
            total += 1

    print(f"\nФункций без type hints: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
