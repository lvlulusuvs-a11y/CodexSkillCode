#!/usr/bin/env python3
"""Автоматизированный код-ревью: анализ изменений в git diff.

Usage:
    git diff main..feature | python scripts/code-review-bot.py
    python scripts/code-review-bot.py --path src/myfile.py
    python scripts/code-review-bot.py --commit HEAD~1
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# ── Issues ─────────────────────────────────────
class ReviewIssue:
    def __init__(self, line: int, severity: str, code: str, message: str, suggestion: str | None = None):
        self.line = line
        self.severity = severity
        self.code = code
        self.message = message
        self.suggestion = suggestion
    
    def __str__(self) -> str:
        sev_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}
        result = f"  {sev_icon.get(self.severity, '⚪')} [{self.severity.upper()}] L{self.line}: {self.message}"
        if self.suggestion:
            result += f"\n    💡 {self.suggestion}"
        return result


# ── Checkers ───────────────────────────────────
def check_print_in_production(code: str, tree: ast.AST) -> list[ReviewIssue]:
    """Find print() calls that should be logger."""
    issues: list[ReviewIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'print':
            issues.append(ReviewIssue(
                line=node.lineno,
                severity="warning",
                code="PRINT",
                message="print() в production коде. Используй logger.",
                suggestion='Заменить на logger.info(...) или logger.debug(...)',
            ))
    return issues


def check_bare_except(code: str, tree: ast.AST) -> list[ReviewIssue]:
    """Find bare except: clauses."""
    issues: list[ReviewIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(ReviewIssue(
                line=node.lineno,
                severity="error",
                code="EXCEPT",
                message="Голый except: без типа исключения.",
                suggestion="Укажи конкретное исключение: except ValueError: или except Exception as e:",
            ))
    return issues


def check_todo_fixme(code: str, lines: list[str]) -> list[ReviewIssue]:
    """Find TODO/FIXME in code."""
    issues: list[ReviewIssue] = []
    for i, line in enumerate(lines, 1):
        if re.search(r'(TODO|FIXME|HACK|XXX|BUG)\b', line, re.IGNORECASE):
            if line.strip().startswith("#"):
                issues.append(ReviewIssue(
                    line=i,
                    severity="info",
                    code="TODO",
                    message=line.strip(),
                    suggestion="TODO/FIXME должны быть в issue tracker, не в коде",
                ))
    return issues


def check_magic_numbers(code: str, lines: list[str], tree: ast.AST) -> list[ReviewIssue]:
    """Check for magic numbers (not in config)."""
    MAGIC_WHITELIST = {0, 1, -1, 100, 60, 24, 3600, 86400, 1024, 404, 500, 200, 201, 301, 302}
    issues: list[ReviewIssue] = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and abs(node.value) >= 2:
            if node.value not in MAGIC_WHITELIST:
                parent = getattr(node, 'parent', None)
                # Skip if in a dataclass field, decorator, or docstring
                if any(isinstance(p, (ast.FunctionDef, ast.ClassDef, ast.Module)) and 
                       isinstance(p, ast.Expr) for p in _get_parents(tree, node)):
                    continue
                issues.append(ReviewIssue(
                    line=node.lineno,
                    severity="info",
                    code="MAGIC",
                    message=f"Магическое число {node.value}",
                    suggestion=f"Вынеси в константу с понятным именем",
                ))
    return issues


def _get_parents(tree: ast.AST, node: ast.AST) -> list[ast.AST]:
    """Get parent chain of a node."""
    parents = []
    for n in ast.walk(tree):
        for child in ast.iter_child_nodes(n):
            if child is node:
                parents.append(n)
    return parents


def check_long_function(lines: list[str], tree: ast.AST) -> list[ReviewIssue]:
    """Check function length."""
    issues: list[ReviewIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (node.end_lineno or 0) - (node.lineno or 0) + 1
            if length > 60:
                issues.append(ReviewIssue(
                    line=node.lineno,
                    severity="warning",
                    code="LONG",
                    message=f"Функция '{node.name}' слишком длинная: {length} строк (лимит 60)",
                    suggestion="Разбей на несколько функций по SRP",
                ))
    return issues


def check_import_order(lines: list[str]) -> list[ReviewIssue]:
    """Basic import order check."""
    issues: list[ReviewIssue] = []
    stdlib_imports = {"os", "sys", "re", "json", "math", "pathlib", "typing", 
                      "collections", "datetime", "functools", "itertools", "abc", 
                      "enum", "dataclasses", "logging", "asyncio", "hashlib", "uuid"}
    
    last_group = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            # Определяем группу: 1=stdlib, 2=third-party, 3=local
            pkg = stripped.split()[1].split(".")[0]
            if pkg in stdlib_imports or pkg.startswith("_"):
                group = 1
            elif "." in pkg or pkg in {"pytest", "fastapi", "sqlalchemy", "aiogram", "pydantic"}:
                group = 2
            else:
                group = 3
            
            if group < last_group:
                issues.append(ReviewIssue(
                    line=i,
                    severity="info",
                    code="IMPORT",
                    message=f"Неправильный порядок импортов: {stripped}",
                    suggestion="Порядок: stdlib → third-party → local",
                ))
            last_group = group
    return issues


def check_mutable_defaults(tree: ast.AST) -> list[ReviewIssue]:
    """Check for mutable default arguments."""
    issues: list[ReviewIssue] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append(ReviewIssue(
                        line=default.lineno,
                        severity="error",
                        code="MUTABLE",
                        message=f"Мутабельный default argument в '{node.name}'",
                        suggestion="Заменить на None и инициализировать внутри: if arg is None: arg = []",
                    ))
    return issues


def run_all_checks(code: str) -> list[ReviewIssue]:
    """Run all code review checks."""
    issues: list[ReviewIssue] = []
    lines = code.splitlines()
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append(ReviewIssue(line=e.lineno or 0, severity="error", code="SYNTAX",
                                  message=f"Syntax error: {e.msg}"))
        return issues
    
    # Set parent references
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore
    
    issues.extend(check_print_in_production(code, tree))
    issues.extend(check_bare_except(code, tree))
    issues.extend(check_todo_fixme(code, lines))
    issues.extend(check_magic_numbers(code, lines, tree))
    issues.extend(check_long_function(lines, tree))
    issues.extend(check_import_order(lines))
    issues.extend(check_mutable_defaults(tree))
    
    return issues


# ── Main ───────────────────────────────────────
def review_file(path: Path) -> int:
    """Review a single file."""
    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Error reading {path}: {e}")
        return 1
    
    issues = run_all_checks(code)
    
    print(f"\n{'='*60}")
    print(f"🔍 Review: {path}")
    print(f"{'='*60}")
    
    if not issues:
        print("✅ No issues found")
        return 0
    
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]
    
    if errors:
        print(f"\n🔴 ERRORS ({len(errors)}):")
        for i in errors: print(i)
    if warnings:
        print(f"\n🟡 WARNINGS ({len(warnings)}):")
        for i in warnings: print(i)
    if infos:
        print(f"\n🔵 INFO ({len(infos)}):")
        for i in infos: print(i)
    
    print(f"\n📊 Total: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} infos")
    return 1 if errors else 0


def review_git_diff() -> int:
    """Review staged changes from git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "-U5"],
            capture_output=True, text=True, check=True,
        )
        diff = result.stdout
    except subprocess.CalledProcessError:
        try:
            result = subprocess.run(
                ["git", "diff", "-U5"],
                capture_output=True, text=True, check=True,
            )
            diff = result.stdout
        except subprocess.CalledProcessError:
            print("❌ Not in a git repository or no changes", file=sys.stderr)
            return 1
    
    if not diff.strip():
        print("No changes to review")
        return 0
    
    # Extract added/changed lines
    issues: list[ReviewIssue] = []
    current_file: str | None = None
    current_lines: list[tuple[int, str]] = []
    
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
            current_lines = []
        elif line.startswith("@@") and current_file:
            # Check current file
            if current_lines:
                code = "\n".join(l for _, l in current_lines)
                file_issues = run_all_checks(code)
                for i in file_issues:
                    i.message = f"[{current_file}] {i.message}"
                issues.extend(file_issues)
            current_lines = []
        elif line.startswith("+") and not line.startswith("+++"):
            current_lines.append((len(current_lines), line[1:]))
    
    # Check last file
    if current_lines:
        code = "\n".join(l for _, l in current_lines)
        file_issues = run_all_checks(code)
        for i in file_issues:
            i.message = f"[{current_file}] {i.message}"
        issues.extend(file_issues)
    
    print(f"\n{'='*60}")
    print(f"🔍 Git Diff Review")
    print(f"{'='*60}")
    
    if not issues:
        print("✅ No issues found in diff")
        return 0
    
    for i in issues:
        print(i)
    
    return 1 if any(i.severity == "error" for i in issues) else 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Automated code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--path", "-p", type=Path, help="Path to file or directory")
    parser.add_argument("--commit", "-c", help="Review a specific commit")
    parser.add_argument("--diff", "-d", action="store_true", help="Review git diff")
    
    args = parser.parse_args(argv)
    
    if args.path:
        path = args.path
        if path.is_dir():
            exit_code = 0
            for pyfile in sorted(path.rglob("*.py")):
                if "migrations" not in str(pyfile):
                    exit_code += review_file(pyfile)
            sys.exit(exit_code)
        else:
            sys.exit(review_file(path))
    elif args.commit:
        # Save diff to temp and review
        result = subprocess.run(
            ["git", "diff", f"{args.commit}~1..{args.commit}", "-U5"],
            capture_output=True, text=True,
        )
        print(result.stdout)
        sys.exit(review_git_diff())
    elif args.diff:
        sys.exit(review_git_diff())
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            code = sys.stdin.read()
            issues = run_all_checks(code)
            for i in issues:
                print(i)
            sys.exit(1 if any(i.severity == "error" for i in issues) else 0)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
