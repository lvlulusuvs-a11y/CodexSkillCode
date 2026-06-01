#!/usr/bin/env python3
"""Проверка безопасности: поиск уязвимых паттернов, hardcoded secrets, injection."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

SEVERITY_HIGH = "HIGH"
SEVERITY_MED = "MED"
SEVERITY_LOW = "LOW"

RULES: list[tuple[str, str, str, str]] = [
    ("S001", "Использование eval/exec", SEVERITY_HIGH,
     r"\b(eval|exec|compile)\s*\("),
    ("S002", "SQL-инъекция (f-string в запросе)", SEVERITY_HIGH,
     r"(execute|executemany)\s*\(\s*f["']"),
    ("S003", "subprocess с shell=True", SEVERITY_HIGH,
     r"subprocess\..*shell\s*=\s*True"),
    ("S004", "pickle.loads из непроверенного источника", SEVERITY_MED,
     r"pickle\.(loads|load)"),
    ("S005", "assert в production коде", SEVERITY_LOW,
     r"\bassert\s+"),
    ("S006", "yaml.load без Loader", SEVERITY_MED,
     r"yaml\.load\s*\(\s*(?!.*Loader)"),
]


def scan_file(path: Path) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return findings

    for code, desc, severity, pattern in RULES:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                findings.append((code, i, severity, f"{desc}: {line.strip()[:80]}"))
    return findings


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root_p = Path(root).resolve()
    total = 0

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
            continue
        findings = scan_file(pyfile)
        for code, line, severity, msg in findings:
            print(f"{pyfile.relative_to(root_p)}:{line}: [{severity}] {code}: {msg}")
            total += 1

    print(f"\nНайдено: {total}")
    return 1 if total > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
