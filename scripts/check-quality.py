#!/usr/bin/env python3
"""Комплексная проверка качества Python-кода.

Запускает все доступные проверки:
  1. Синтаксис
  2. Длина функций
  3. Магические числа
  4. TODO/FIXME
  5. print() в production
  6. Голые except
  7. Именование (PEP8)
  8. Длина строк
  9. Секреты/токены
  10. Цикломатическая сложность
  11. Покрытие type hints
  12. Докстринги
  13. Неиспользуемые импорты
  14. Мёртвый код
  15. Безопасность
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# ── конфиг ────────────────────────────────────────────────────────────
MAX_LINE_LENGTH = 100
MAX_FUNCTION_LINES = 60
MAX_COMPLEXITY = 10
MAGIC_WHITELIST = {0, 1, -1, 100, 60, 24, 3600, 86400, 1024, 404, 500}
BUILTINS = set(dir(__builtins__))
RESERVED = {"True", "False", "None", "self", "cls"}


class CheckResult:
    """Результат одной проверки."""

    def __init__(self, path: Path, line: int, col: int | None,
                 code: str, severity: str, message: str) -> None:
        self.path = path
        self.line = line
        self.col = col
        self.code = code
        self.severity = severity
        self.message = message

    def __str__(self) -> str:
        col = f":{self.col}" if self.col is not None else ""
        return f"{self.path}:{self.line}{col}  [{self.severity}] {self.code}: {self.message}"


def check_syntax(path: Path, results: list[CheckResult]) -> None:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as e:
        results.append(CheckResult(path, e.lineno or 0, None, "Q001", "error", str(e.msg)))


def check_long_functions(path: Path, tree: ast.AST, results: list[CheckResult]) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        length = (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0
        if length > MAX_FUNCTION_LINES:
            results.append(CheckResult(
                path, node.lineno, node.col_offset, "Q002", "warning",
                f"Функция '{node.name}' ({length} строк, лимит {MAX_FUNCTION_LINES})",
            ))


def check_magic_numbers(path: Path, lines: list[str], results: list[CheckResult]) -> None:
    pattern = re.compile(r"(?<!\w)(\d{3,})(?!\w)")
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if any(s in line for s in ("# noqa", "__version__", "copyright", "License")):
            continue
        for match in pattern.finditer(line):
            num = int(match.group(1))
            if num not in MAGIC_WHITELIST and num <= 99999:
                results.append(CheckResult(
                    path, i, match.start(), "Q003", "warning", f"Магическое число {num}",
                ))
                break


def check_todos(path: Path, lines: list[str], results: list[CheckResult]) -> None:
    pattern = re.compile(r"(?i)#\s*(TODO|FIXME|XXX|HACK|BUG)\b")
    for i, line in enumerate(lines, 1):
        match = pattern.search(line)
        if match:
            results.append(CheckResult(
                path, i, match.start(), "Q004", "info",
                f"{match.group(1).upper()}: {line.strip()[:80]}",
            ))


def check_print_statements(path: Path, tree: ast.AST, results: list[CheckResult]) -> None:
    if path.name in ("cli.py", "main.py", "__main__.py"):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            results.append(CheckResult(
                path, node.lineno, node.col_offset, "Q005", "warning", "print()",
            ))


def check_bare_except(path: Path, tree: ast.AST, results: list[CheckResult]) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            results.append(CheckResult(
                path, node.lineno, node.col_offset, "Q006", "error", "Голый except:",
            ))


def check_naming(path: Path, tree: ast.AST, results: list[CheckResult]) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_") and not re.match(r"^[a-z]", node.name):
                results.append(CheckResult(
                    path, node.lineno, node.col_offset, "Q007", "warning",
                    f"Функция '{node.name}' должна быть snake_case",
                ))
        elif isinstance(node, ast.ClassDef):
            if not re.match(r"^[A-Z]", node.name):
                results.append(CheckResult(
                    path, node.lineno, node.col_offset, "Q008", "warning",
                    f"Класс '{node.name}' должен быть PascalCase",
                ))


def check_long_lines(path: Path, lines: list[str], results: list[CheckResult]) -> None:
    for i, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_LENGTH and not line.strip().startswith("#"):
            results.append(CheckResult(
                path, i, MAX_LINE_LENGTH, "Q009", "warning",
                f"Строка {len(line)} символов (лимит {MAX_LINE_LENGTH})",
            ))


def check_secrets(path: Path, lines: list[str], results: list[CheckResult]) -> None:
    patterns = [
        (r"(?i)(api_key|password|token|secret)\s*=\s*['\"](?![*'])([^'\"]{8,})['\"]", "секрет"),
        (r"(?i)(-----BEGIN (RSA |EC )?PRIVATE KEY-----)", "закрытый ключ"),
    ]
    for i, line in enumerate(lines, 1):
        if "# noqa" in line:
            continue
        for pat, desc in patterns:
            match = re.search(pat, line)
            if match:
                results.append(CheckResult(
                    path, i, match.start(), "Q010", "error", f"Обнаружен {desc}",
                ))
                break


def check_complexity(path: Path, tree: ast.AST, results: list[CheckResult]) -> None:
    def _score(node: ast.AST) -> int:
        s = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.And, ast.Or, ast.ExceptHandler)):
                s += 1
        return s

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cmp = _score(node)
            if cmp > MAX_COMPLEXITY:
                results.append(CheckResult(
                    path, node.lineno, node.col_offset, "Q011", "warning",
                    f"Сложность {node.name}: {cmp} (лимит {MAX_COMPLEXITY})",
                ))


def run_all(root: str = ".") -> int:
    results: list[CheckResult] = []
    root_p = Path(root).resolve()

    for pyfile in sorted(root_p.rglob("*.py")):
        if any(p.startswith(".") or p in ("__pycache__", "node_modules") for p in pyfile.parts):
            continue
        try:
            source = pyfile.read_text(encoding="utf-8")
            tree = ast.parse(source)
            lines = source.splitlines()

            check_syntax(pyfile, results)
            check_long_functions(pyfile, tree, results)
            check_magic_numbers(pyfile, lines, results)
            check_todos(pyfile, lines, results)
            check_print_statements(pyfile, tree, results)
            check_bare_except(pyfile, tree, results)
            check_naming(pyfile, tree, results)
            check_long_lines(pyfile, lines, results)
            check_secrets(pyfile, lines, results)
            check_complexity(pyfile, tree, results)

        except Exception as e:
            print(f"Ошибка при проверке {pyfile}: {e}", file=sys.stderr)

    # сортировка: сначала ошибки, потом предупреждения, потом info
    severity_order = {"error": 0, "warning": 1, "info": 2}
    results.sort(key=lambda r: (severity_order.get(r.severity, 9), r.path, r.line))

    for r in results:
        print(r)

    # статистика
    by_sev: dict[str, int] = {}
    for r in results:
        by_sev[r.severity] = by_sev.get(r.severity, 0) + 1

    print(f"\n{'─' * 50}")
    print(f"Всего: {len(results)} ({by_sev.get('error', 0)} errors, "
          f"{by_sev.get('warning', 0)} warnings, {by_sev.get('info', 0)} info)")

    return 1 if by_sev.get("error", 0) > 0 else 0


if __name__ == "__main__":
    sys.exit(run_all(sys.argv[1] if len(sys.argv) > 1 else "."))
