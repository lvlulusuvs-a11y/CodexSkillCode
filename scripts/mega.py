#!/usr/bin/env python3
"""
⚡ Mega-Coding Unified CLI

Единая точка входа для всех инструментов Mega-Coding.
Замена 12 отдельных скриптов — одна команда.

Usage:
    mega lint [path]           — Полный линтинг
    mega review [path]         — Код-ревью + Trees Club
    mega check [path]          — Quality check (всё вместе)
    mega metrics [path]        — Метрики качества кода
    mega diff [commit]         — Diff-анализ
    mega init --type fastapi   — Создать проект
    mega ci                    — Полный CI pipeline
    mega version               — Версия
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPTS_DIR.parent


def run_script(name: str, args: list[str] | None = None) -> int:
    """Run a script from scripts/ directory."""
    script_path = SCRIPTS_DIR / name
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return 1
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd)
    return result.returncode


def format_time(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.1f}s"


# ── Commands ─────────────────────────────────────────────────────────

def cmd_lint(args: list[str]) -> int:
    """Run lint-runner (ruff, mypy, bandit)."""
    print("\n🔍 [LINT] Запуск линтеров...")
    return run_script("lint-runner.py", args)


def cmd_review(args: list[str]) -> int:
    """Run code review + tree voting."""
    code = 0
    
    # Part 1: code-review-bot
    print("\n🔍 [REVIEW] Статический анализ...")
    code += run_script("code-review-bot.py", ["--path"] + (args or ["."]))
    
    # Part 2: tree voting
    print("\n\n🌳 [TREES] Оценка по деревьям...")
    tree_script = SCRIPTS_DIR / "tree-voting" / "evaluate.py"
    if tree_script.exists():
        code += subprocess.run([sys.executable, str(tree_script)] + (args or ["."])).returncode
    else:
        print("⚠️  Tree voting script not found")
    
    return code


def cmd_check(args: list[str]) -> int:
    """Full quality check."""
    code = 0
    path = args[0] if args else "."
    
    print("=" * 60)
    print("⚡ Mega-Coding: Полная проверка качества")
    print("=" * 60)
    
    checks = [
        ("📐 Синтаксис", lambda: subprocess.run(
            ["python3", "-c", f"import ast; ast.parse(open('{path}').read())" 
             if Path(path).is_file() else 
             f"import os, ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('{path}/**/*.py', recursive=True) if not any(p.startswith('.') for p in f.split(os.sep))"],
            capture_output=True).returncode),
        ("🔍 Complexity", lambda: run_script("check-complexity.py", args)),
        ("📝 Docstrings", lambda: run_script("check-docstrings.py", args)),
        ("🏷️  Type Hints", lambda: run_script("check-types.py", args)),
        ("🔒 Security", lambda: run_script("security-check.py", args)),
        ("💀 Dead Code", lambda: run_script("check-dead-code.py", args)),
        ("🧹 Unused Imports", lambda: run_script("check-unused-imports.py", args)),
        ("🌳 Trees Club", lambda: subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "tree-voting" / "evaluate.py"), path]).returncode),
        ("📊 Quality Score", lambda: run_script("check-quality.py", args)),
    ]
    
    results: list[tuple[str, int]] = []
    for name, check_fn in checks:
        print(f"\n─── {name} ───")
        start = time.time()
        rc = check_fn()
        elapsed = time.time() - start
        status = "✅" if rc == 0 else "❌"
        print(f"  {status} ({format_time(elapsed)})")
        results.append((name, rc))
        code += rc
    
    print("\n" + "=" * 60)
    print("📊 Результаты:")
    passes = sum(1 for _, rc in results if rc == 0)
    total = len(results)
    print(f"  {passes}/{total} проверок пройдено")
    
    if code == 0:
        print("  ✅ Все проверки пройдены!")
    else:
        print(f"  ❌ {code} ошибок")
    
    print("=" * 60)
    return code


def cmd_metrics(args: list[str]) -> int:
    """Generate quality metrics report."""
    path = args[0] if args else "."
    print("\n📊 [METRICS] Сбор метрик качества...")
    # Use check-quality metrics
    return run_script("check-quality.py", args)


def cmd_diff(args: list[str]) -> int:
    """Analyze diff between commits."""
    commit = args[0] if args else "HEAD~1"
    print(f"\n📋 [DIFF] Анализ изменений ({commit} → HEAD)...")
    
    # Get changed Python files
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{commit}..HEAD"],
        capture_output=True, text=True,
    )
    py_files = [f for f in result.stdout.splitlines() if f.endswith('.py')]
    
    if not py_files:
        print("  Нет изменений в Python файлах")
        return 0
    
    print(f"  Изменено файлов: {len(py_files)}")
    
    # Run metrics on each
    for f in py_files:
        if Path(f).exists():
            print(f"\n  ── {f} ──")
            run_script("check-complexity.py", [f])
    
    return 0


def cmd_init(args: list[str]) -> int:
    """Create a new project from template."""
    return run_script("codex-project-init.py", args)


def cmd_ci(args: list[str]) -> int:
    """Full CI pipeline."""
    code = 0
    print("=" * 60)
    print("⚡ Mega-Coding CI Pipeline")
    print("=" * 60)
    
    steps = [
        ("🧪 Тесты", ["pytest", "-v", "--tb=short", "-x"]),
        ("🔍 Линтинг", cmd_check),
        ("📊 Качество", cmd_metrics),
    ]
    
    for name, step in steps:
        print(f"\n─── {name} ───")
        start = time.time()
        if callable(step):
            rc = step(args)
        else:
            rc = subprocess.run(step, capture_output=True).returncode
        elapsed = time.time() - start
        print(f"  {'✅' if rc == 0 else '❌'} ({format_time(elapsed)})")
        code += rc
    
    print(f"\n{'='*60}")
    print(f"CI Pipeline: {'✅ PASS' if code == 0 else '❌ FAIL'}")
    print(f"{'='*60}")
    return code


def cmd_version(args: list[str]) -> int:
    """Show version."""
    version_file = ROOT_DIR / "CHANGELOG.md"
    if version_file.exists():
        first_line = version_file.read_text().splitlines()[0] if version_file.exists() else ""
        print(f"⚡ Mega-Coding {first_line}")
    print(f"  Scripts: {len(list(SCRIPTS_DIR.glob('*.py')))} + tree-voting")
    print(f"  References: {len(list((ROOT_DIR / 'references/extra').glob('*.md')))} files")
    print(f"  Languages: Python, Go, TypeScript, Rust")
    return 0


# ── Main CLI ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="⚡ Mega-Coding: Unified Developer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # lint
    p_lint = subparsers.add_parser("lint", help="Run linters")
    p_lint.add_argument("path", nargs="?", default=".", help="File or directory")
    
    # review
    p_review = subparsers.add_parser("review", help="Code review + trees")
    p_review.add_argument("path", nargs="?", default=".", help="File or directory")
    
    # check
    p_check = subparsers.add_parser("check", help="Full quality check")
    p_check.add_argument("path", nargs="?", default=".", help="File or directory")
    
    # metrics
    p_metrics = subparsers.add_parser("metrics", help="Quality metrics")
    p_metrics.add_argument("path", nargs="?", default=".", help="File or directory")
    
    # diff
    p_diff = subparsers.add_parser("diff", help="Diff analysis")
    p_diff.add_argument("commit", nargs="?", default="HEAD~1", help="Base commit")
    
    # init
    p_init = subparsers.add_parser("init", help="Create project")
    p_init.add_argument("--type", required=True, choices=["fastapi", "cli", "bot", "lib"])
    
    # ci
    p_ci = subparsers.add_parser("ci", help="Full CI pipeline")
    
    # version
    subparsers.add_parser("version", help="Show version")
    
    args = parser.parse_args()
    
    if args.command == "lint":
        return cmd_lint([args.path] if args.path else [])
    elif args.command == "review":
        return cmd_review([args.path] if args.path else [])
    elif args.command == "check":
        return cmd_check([args.path] if args.path else [])
    elif args.command == "metrics":
        return cmd_metrics([args.path] if args.path else [])
    elif args.command == "diff":
        return cmd_diff([args.commit])
    elif args.command == "init":
        return cmd_init(["--type", args.type])
    elif args.command == "ci":
        return cmd_ci([])
    elif args.command == "version":
        return cmd_version([])
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
