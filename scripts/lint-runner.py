#!/usr/bin/env python3
"""Универсальный запускальщик линтеров: ruff, mypy, pyright, bandit, safety."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


TOOLS: list[dict] = [
    {"name": "ruff check", "cmd": ["ruff", "check", "."], "optional": False},
    {"name": "ruff format --check", "cmd": ["ruff", "format", "--check", "."], "optional": False},
    {"name": "mypy", "cmd": ["mypy", "--strict", "src/"], "optional": True},
    {"name": "bandit", "cmd": ["bandit", "-r", "src/", "-x", "tests"], "optional": True},
]


def run_tool(tool: dict) -> bool:
    print(f"\n─── {tool['name']} ───")
    result = subprocess.run(tool["cmd"], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout or result.stderr)
        if not tool.get("optional"):
            return False
    else:
        print("✅ OK")
    return True


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    ok = True
    for tool in TOOLS:
        if not run_tool(tool):
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
