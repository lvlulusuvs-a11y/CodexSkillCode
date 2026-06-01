#!/usr/bin/env python3
"""Поиск неиспользуемых импортов через AST."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def find_unused(filepath: Path) -> list[tuple[int, str]]:
    unused: list[tuple[int, str]] = []
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError:
        return unused

    imported: dict[str, tuple[int, str]] = {}
    used_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported[name] = (node.lineno, alias.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported[name] = (node.lineno, alias.name)
        elif isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            used_names.add(node.value.id if isinstance(node.value, ast.Name) else "")

    for name, (lineno, fullname) in imported.items():
        if name not in used_names and name != "__future__":
            unused.append((lineno, fullname))

    return unused


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        unused = find_unused(pyfile)
        for lineno, name in unused:
            print(f"{pyfile.relative_to(root_p)}:{lineno}: {name}")
            total += 1

    print(f"\nНеиспользуемых импортов: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
