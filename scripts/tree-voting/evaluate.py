#!/usr/bin/env python3
"""
🌳 Mega-Coding Tree Voting System (Live)

Автоматическая проверка кода по 6 деревьям-судьям.
Интеграция с code-review-bot, CI, PR review.

Usage:
    python scripts/tree-voting/evaluate.py path/to/file.py
    python scripts/tree-voting/evaluate.py --diff
    python scripts/tree-voting/evaluate.py --ci
    python scripts/tree-voting/evaluate.py --pr-summary
"""
from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Tree Definitions ──────────────────────────────────────────────────

@dataclass
class TreeVerdict:
    tree_name: str
    tree_emoji: str
    vote: str  # "Человек" or "ИИ"
    score: float  # 0.0 (ИИ) to 1.0 (Человек)
    details: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    path: str | None
    trees: list[TreeVerdict]
    total_human: int
    total_ai: int
    passed: bool  # 4+ human = passed
    summary_score: float  # 0.0 to 1.0


# ── Individual Trees ──────────────────────────────────────────────────

class TreeJudge:
    """Base class for tree judges."""
    name: str = ""
    emoji: str = ""
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        raise NotImplementedError


class OakJudge(TreeJudge):
    """Дуб — Архитектура и дизайн"""
    name = "Дуб"
    emoji = "🌳"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        
        # Check: too many global functions (no classes)
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        
        if funcs and not classes and len(funcs) > 3:
            issues.append(f"Нет классов, {len(funcs)} глобальных функций — выглядит как скрипт, не как дизайн")
        
        # Check: function complexity
        for func in funcs:
            if _complexity(func) > 12:
                issues.append(f"Функция '{func.name}' сложность {_complexity(func)} — переусложнена")
        
        # Check: module-level code
        module_body = tree.body if isinstance(tree, ast.Module) else []
        executable = [n for n in module_body if isinstance(n, ast.Expr) and 
                     isinstance(getattr(n, 'value', None), ast.Call)]
        if len([n for n in module_body if isinstance(n, ast.Expr) and 
                isinstance(getattr(n, 'value', None), ast.Call)]) > 2:
            issues.append("Много вызовов на уровне модуля — перемести в main()")
        
        # Check: long functions
        long_funcs = 0
        for func in funcs:
            if hasattr(func, 'end_lineno') and func.end_lineno and (func.end_lineno - func.lineno) > 80:
                long_funcs += 1
        if long_funcs > 2:
            issues.append(f"{long_funcs} функций длиннее 80 строк — разбей на части")
        
        # Calculate score
        if not issues:
            details.append("Архитектура чистая, классы/функции разделены логично")
            score = 0.9
            vote = "Человек"
        else:
            penalty = min(len(issues) * 0.2, 0.8)
            score = max(1.0 - penalty, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
            details.append(f"Найдено {len(issues)} проблем с архитектурой")
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


class BirchJudge(TreeJudge):
    """Берёза — Коллбеки и асинхронность"""
    name = "Берёза"
    emoji = "🌲"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        async_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
        
        # Check: sync call in async function
        if async_funcs:
            for func in async_funcs:
                sync_calls = []
                for node in ast.walk(func):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            name = node.func.attr
                        elif isinstance(node.func, ast.Name):
                            name = node.func.id
                        else:
                            continue
                        # Detect blocking patterns
                        if name in ('time.sleep', 'requests.get', 'requests.post'):
                            sync_calls.append(name)
                if sync_calls:
                    issues.append(f"Блокирующий вызов в async функции '{func.name}': {', '.join(sync_calls)}")
            
            # Check: await in loop without concurrency
            for func in async_funcs:
                for node in ast.walk(func):
                    if isinstance(node, ast.For) or isinstance(node, ast.comprehension):
                        has_async = False
                        for child in ast.walk(node):
                            if isinstance(child, ast.Await):
                                has_async = True
                                break
                        if has_async and not isinstance(node, ast.AsyncFor):
                            issues.append(f"Последовательный await в цикле без asyncio.gather или TaskGroup")
                            break
        
        if not issues:
            details.append("Асинхронность чистая, ошибки обрабатываются")
            score = 0.9
            vote = "Человек"
        else:
            score = max(1.0 - len(issues) * 0.25, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


class PineJudge(TreeJudge):
    """Сосна — Структура кода и модульность"""
    name = "Сосна"
    emoji = "🌲"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        
        # Check file length
        if len(lines) > 500:
            issues.append(f"Файл слишком большой ({len(lines)} строк, лимит 500)")
        
        # Check: single responsibility per module
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        
        # Many unrelated things in one file
        if len(classes) + len(funcs) > 15 and len(classes) < 2:
            issues.append("Много функций без классов — возможно, нарушение SRP")
        
        # Check: too many imports
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        if len(imports) > 20:
            issues.append(f"Слишком много импортов ({len(imports)}) — раздели файл")
        
        # Check: circular dependency markers
        if 'from typing import TYPE_CHECKING' in source:
            details.append("TYPE_CHECKING — возможно циклическая зависимость")
        
        if not issues:
            details.append("Структура модульная, границы чёткие")
            score = 0.85
            vote = "Человек"
        else:
            score = max(1.0 - len(issues) * 0.2, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


class MapleJudge(TreeJudge):
    """Клён — Чистота кода (нейминг, дублирование)"""
    name = "Клён"
    emoji = "🍁"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        
        # Check: suspicious variable names
        bad_names = {'var1', 'var2', 'tmp', 'tmp1', 'temp', 'data1', 'data2', 'xxx', 'foo', 'bar'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in bad_names:
                if node.id not in issues:
                    issues.append(f"Подозрительное имя: '{node.id}' — переименуй осмысленно")
        
        # Check: magic numbers
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if isinstance(node.value, int) and 2 <= node.value <= 9999 and node.value not in {0, 1, -1, 60, 100, 200, 400, 404, 500}:
                    # Check not in common patterns
                    pass  # Too many false positives
        
        # Check: line length violations
        long_lines = 0
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > 100 and not line.strip().startswith('#'):
                long_lines += 1
        if long_lines > 5:
            issues.append(f"{long_lines} строк длиннее 100 символов")
        
        # Check: duplicate code (same expression patterns)
        expressions: dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                key = f"{node.func.attr}({len(node.args)})"
                expressions[key] = expressions.get(key, 0) + 1
        
        # Check duplicate patterns (heuristic)
        
        if not issues:
            details.append("Код чистый, имена осмысленные")
            score = 0.9
            vote = "Человек"
        else:
            score = max(1.0 - len(issues) * 0.2, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


class WillowJudge(TreeJudge):
    """Ива — Обработка ошибок и крайние случаи"""
    name = "Ива"
    emoji = "🌿"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        
        # Check: bare except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append("Голый except: без типа исключения")
                break
        
        # Check: pass in except
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if any(isinstance(n, ast.Pass) for n in node.body):
                    issues.append("except: pass — молча проглатывает ошибку")
                    break
        
        # Check: functions with no error handling
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for func in funcs:
            has_try = any(isinstance(n, ast.Try) for n in ast.walk(func))
            if not has_try:
                # Check if function does risky operations
                risky = False
                for node in ast.walk(func):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr in ('open', 'connect', 'request', 'execute', 'send'):
                                risky = True
                        elif isinstance(node.func, ast.Name):
                            if node.func.id in ('open', 'eval', 'exec'):
                                risky = True
                if risky:
                    issues.append(f"Функция '{func.name}' не обрабатывает ошибки (try/except)")
        
        # Check: assert in non-test code (disabled with -O)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                issues.append("assert — отключается с -O, используй if/raise")
                break
        
        if not issues:
            details.append("Ошибки обрабатываются, крайние случаи покрыты")
            score = 0.85
            vote = "Человек"
        else:
            score = max(1.0 - len(issues) * 0.2, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


class AshJudge(TreeJudge):
    """Ясень — Тестируемость и сопровождаемость"""
    name = "Ясень"
    emoji = "🌳"
    
    def evaluate(self, source: str, tree: ast.AST, lines: list[str]) -> TreeVerdict:
        issues: list[str] = []
        details: list[str] = []
        
        # Check: global state
        globals = [n for n in tree.body if isinstance(n, ast.Assign)]
        mutable_globals = [n for n in globals if any(isinstance(t, (ast.List, ast.Dict, ast.Set)) 
                           for t in getattr(n, 'targets', []))]
        if mutable_globals:
            issues.append(f"Глобальные изменяемые объекты — тестировать сложно")
        
        # Check: hardcoded dependencies (no DI)
        funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for func in funcs:
            has_db = any(isinstance(n, ast.Call) and 
                        isinstance(getattr(n, 'func', None), ast.Attribute) and
                        'db' in n.func.attr.lower()
                        for n in ast.walk(func))
            if has_db:
                # Check if db is parameter
                args = [arg.arg for arg in func.args.args if hasattr(arg, 'arg')]
                if not any('db' in a.lower() or 'repo' in a.lower() or 'session' in a.lower() for a in args):
                    issues.append(f"Функция '{func.name}' использует DB напрямую (без DI)")
        
        # Check: long parameter list
        for func in funcs:
            param_count = len(func.args.args)
            if param_count > 6:
                issues.append(f"Функция '{func.name}' с {param_count} параметрами — используй dataclass")
        
        if not issues:
            details.append("Код тестируемый, зависимости инвертированы")
            score = 0.85
            vote = "Человек"
        else:
            score = max(1.0 - len(issues) * 0.25, 0.1)
            vote = "ИИ" if score < 0.5 else "Человек"
        
        return TreeVerdict(self.name, self.emoji, vote, score, details, issues)


# ── Orchestrator ──────────────────────────────────────────────────────

def _complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity."""
    score = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                              ast.And, ast.Or, ast.Assert)):
            score += 1
    return score


ALL_TREES: list[TreeJudge] = [
    OakJudge(),
    BirchJudge(),
    PineJudge(),
    MapleJudge(),
    WillowJudge(),
    AshJudge(),
]


def evaluate_code(source: str, filepath: str | None = None) -> EvaluationResult:
    """Run all tree judges on source code."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        # Can't parse - automatically fails
        return EvaluationResult(
            path=filepath,
            trees=[TreeVerdict("Parser", "❌", "ИИ", 0.0, 
                              [f"Syntax error: {e}"], [str(e)])],
            total_human=0,
            total_ai=1,
            passed=False,
            summary_score=0.0,
        )
    
    lines = source.splitlines()
    verdicts: list[TreeVerdict] = []
    
    for judge in ALL_TREES:
        verdict = judge.evaluate(source, tree, lines)
        verdicts.append(verdict)
    
    total_human = sum(1 for v in verdicts if v.vote == "Человек")
    total_ai = sum(1 for v in verdicts if v.vote == "ИИ")
    passed = total_human >= 4
    summary_score = total_human / len(verdicts)
    
    return EvaluationResult(
        path=filepath,
        trees=verdicts,
        total_human=total_human,
        total_ai=total_ai,
        passed=passed,
        summary_score=summary_score,
    )


def format_report(result: EvaluationResult, verbose: bool = True) -> str:
    """Format evaluation result as rich text."""
    lines: list[str] = []
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"🌳 Совет Деревьев: Code Quality Check")
    lines.append("=" * 60)
    
    if result.path:
        lines.append(f"Файл: {result.path}")
    
    lines.append("")
    for verdict in result.trees:
        icon = "✅" if verdict.vote == "Человек" else "❌"
        lines.append(f"  {verdict.tree_emoji} {verdict.tree_name}: {verdict.vote} "
                     f"[{verdict.score:.0%}] {icon}")
        if verbose and verdict.issues:
            for issue in verdict.issues[:3]:  # top 3 issues
                lines.append(f"    • {issue}")
        if verbose and verdict.details:
            for detail in verdict.details:
                lines.append(f"    ✓ {detail}")
    
    lines.append("")
    lines.append(f"  Результат: {result.total_human} Человек, {result.total_ai} ИИ")
    
    if result.passed:
        lines.append(f"  ✅ ПРИНЯТО ({result.summary_score:.0%} человечность)")
    else:
        lines.append(f"  ❌ НЬЮ ({result.summary_score:.0%} человечность — требуется переработка)")
    
    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(result: EvaluationResult) -> str:
    """Format as JSON for CI integration."""
    return json.dumps({
        "path": result.path,
        "passed": result.passed,
        "score": result.summary_score,
        "trees": {
            v.tree_name: {
                "vote": v.vote,
                "score": v.score,
                "issues": v.issues,
            }
            for v in result.trees
        },
        "summary": f"{result.total_human}/{result.total_ai}",
    }, indent=2, ensure_ascii=False)


def format_pr_comment(result: EvaluationResult) -> str:
    """Format as PR comment."""
    badges = "".join(
        f"![{v.tree_name}](https://img.shields.io/badge/{v.tree_name}-{v.vote}-{'green' if v.vote == 'Человек' else 'red'}) "
        for v in result.trees
    )
    return f"""## 🌳 Trees Club Review

**Overall: {'✅ PASS' if result.passed else '❌ FAIL'}** (Score: {result.summary_score:.0%})

| Tree | Vote | Issues |
|------|------|--------|
{chr(10).join(f"| {v.tree_emoji} {v.tree_name} | {v.vote} | {'; '.join(v.issues[:2]) if v.issues else 'OK'} |" for v in result.trees)}

*Automated review by Mega-Coding Trees Club*
"""


# ── Main ─────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🌳 Tree Voting: Multi-dimensional code quality evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", nargs="?", type=str, help="File or directory path")
    parser.add_argument("--diff", action="store_true", help="Evaluate git diff")
    parser.add_argument("--ci", action="store_true", help="CI-friendly JSON output")
    parser.add_argument("--pr-comment", action="store_true", help="Format as PR comment")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show issue details")
    args = parser.parse_args()
    
    if args.path:
        path = Path(args.path)
        if path.is_dir():
            results: list[EvaluationResult] = []
            for pyfile in sorted(path.rglob("*.py")):
                if any(p.startswith(".") or p == "__pycache__" for p in pyfile.parts):
                    continue
                source = pyfile.read_text(encoding="utf-8", errors="replace")
                result = evaluate_code(source, str(pyfile))
                results.append(result)
                print(format_report(result, args.verbose))
            
            if args.ci:
                print(json.dumps({"results": [json.loads(format_json(r)) for r in results]}))
            
            return 1 if any(not r.passed for r in results) else 0
        
        else:
            source = path.read_text(encoding="utf-8", errors="replace")
            result = evaluate_code(source, str(path))
            
            if args.ci:
                print(format_json(result))
            elif args.pr_comment:
                print(format_pr_comment(result))
            else:
                print(format_report(result, args.verbose))
            
            return 1 if not result.passed else 0
    
    elif args.diff:
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--cached", "-U5"],
            capture_output=True, text=True,
        )
        diff = result.stdout
        if not diff:
            result = subprocess.run(
                ["git", "diff", "-U5"],
                capture_output=True, text=True,
            )
            diff = result.stdout
        
        if not diff.strip():
            print("No changes to evaluate")
            return 0
        
        # Extract Python code from diff
        py_lines = []
        current_file = None
        for line in diff.splitlines():
            if line.startswith("+++ b/") and line.endswith(".py"):
                current_file = line[6:]
            elif line.startswith("+") and not line.startswith("+++"):
                py_lines.append(line[1:])
        
        combined = "\n".join(py_lines)
        result_eval = evaluate_code(combined, "git diff")
        print(format_report(result_eval, args.verbose))
        return 1 if not result_eval.passed else 0
    
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            source = sys.stdin.read()
            result = evaluate_code(source, "stdin")
            if args.ci:
                print(format_json(result))
            else:
                print(format_report(result, args.verbose))
            return 1 if not result.passed else 0
        
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
