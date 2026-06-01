#!/usr/bin/env python3
"""Проверка покрытия докстрингами модулей, классов, функций."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def check_file(path: Path) -> list[tuple[int, str, str]]:
    missing: list[tuple[int, str, str]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return missing

    # модуль
    if not ast.get_docstring(tree):
        missing.append((1, "module", "Нет докстринга модуля"))

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and not ast.get_docstring(node):
            missing.append((node.lineno, f"class {node.name}", "Нет докстринга класса"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            if node.name.startswith("_"):
                continue
            if not ast.get_docstring(node):
                kind = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                missing.append((node.lineno, f"{kind} {node.name}", "Нет докстринга функции"))

    return missing


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        missing = check_file(pyfile)
        for lineno, kind, msg in missing:
            print(f"{pyfile.relative_to(root_p)}:{lineno}: {kind}: {msg}")
            total += 1

    print(f"\nНет докстринга: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
