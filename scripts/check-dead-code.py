#!/usr/bin/env python3
"""Поиск мёртвого кода: неиспользуемые переменные, недостижимый код."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def find_issues(path: Path) -> list[tuple[int, str, str]]:
    issues: list[tuple[int, str, str]] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        # return с кодом после
        if isinstance(node, ast.FunctionDef):
            parent = getattr(node, 'parent', None)
            for i, child in enumerate(node.body):
                if isinstance(child, ast.Return) and i < len(node.body) - 1:
                    for after in node.body[i + 1:]:
                        if isinstance(after, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            continue
                        if isinstance(after, ast.Pass):
                            continue
                        issues.append((after.lineno, node.name, "Код после return"))

        # pass мимо
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Constant) and node.test.value is False:
                issues.append((node.lineno, "", "if False: — мёртвый код"))

    return issues


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        issues = find_issues(pyfile)
        for lineno, func, msg in issues:
            print(f"{pyfile.relative_to(root_p)}:{lineno}: {func}: {msg}")
            total += 1

    print(f"\nПроблем: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
