#!/usr/bin/env python3
"""
📊 Mega-Coding Quality Metrics & Feedback System

Измеряет качество кода в числах и показывает динамику (diff-анализ).

Usage:
    python metrics/quality-metrics.py path/to/src/
    python metrics/quality-metrics.py --diff HEAD~1..HEAD
    python metrics/quality-metrics.py --history
    python metrics/quality-metrics.py --dashboard
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any


# ── Metrics ──────────────────────────────────────────────────────────

@dataclass
class QualityMetrics:
    """All quality metrics for a codebase."""
    # Volume
    total_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    
    # Complexity
    avg_function_length: float = 0.0
    max_function_length: int = 0
    avg_complexity: float = 0.0
    max_complexity: int = 0
    high_complexity_count: int = 0  # > 10
    
    # Quality
    type_hit_ratio: float = 0.0  # functions with type hints / total
    docstring_ratio: float = 0.0
    long_line_count: int = 0
    magic_number_count: int = 0
    bare_except_count: int = 0
    todo_count: int = 0
    print_count: int = 0
    
    # Maintainability
    global_function_count: int = 0
    avg_params_count: float = 0.0
    deep_nesting_count: int = 0  # nesting > 4
    
    # Test coverage (from other tools)
    test_line_ratio: float = 0.0  # test lines / source lines
    
    # Health score (composite)
    health_score: float = 0.0
    
    # Security
    security_issues: int = 0
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0.0


class MetricsCollector:
    """Collect quality metrics from Python source code."""
    
    def __init__(self, path: str = "."):
        self.path = Path(path)
    
    def collect(self) -> QualityMetrics:
        """Run all metrics collection."""
        start = time.time()
        
        metrics = QualityMetrics()
        
        if self.path.is_file():
            files = [self.path]
        else:
            files = list(self.path.rglob("*.py"))
        
        # Filter out hidden dirs and __pycache__
        files = [f for f in files 
                 if not any(p.startswith(".") or p == "__pycache__" 
                           for p in f.relative_to(self.path).parts)]
        
        metrics.total_files = len(files)
        
        all_func_lengths: list[int] = []
        all_complexities: list[float] = []
        all_params: list[int] = []
        typed_funcs = 0
        documented_funcs = 0
        total_funcs = 0
        
        for pyfile in files:
            try:
                source = pyfile.read_text(encoding="utf-8")
            except Exception:
                continue
            
            lines = source.splitlines()
            metrics.total_lines += len(lines)
            
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            
            # Count classes
            metrics.total_classes += sum(
                1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)
            )
            
            # Analyze functions
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                
                total_funcs += 1
                func_len = (node.end_lineno - node.lineno + 1) if node.end_lineno else 0
                all_func_lengths.append(func_len)
                
                if func_len > metrics.max_function_length:
                    metrics.max_function_length = func_len
                
                # Complexity
                cmp = self._complexity(node)
                all_complexities.append(cmp)
                if cmp > metrics.max_complexity:
                    metrics.max_complexity = cmp
                if cmp > 10:
                    metrics.high_complexity_count += 1
                
                # Nesting
                nd = self._nesting_depth(node)
                if nd > 4:
                    metrics.deep_nesting_count += 1
                
                # Params
                param_count = len(node.args.args)
                all_params.append(param_count)
                
                # Type hints
                has_returns = node.returns is not None
                has_args_types = any(
                    arg.annotation is not None for arg in node.args.args
                    if hasattr(arg, 'annotation')
                )
                if has_returns or has_args_types:
                    typed_funcs += 1
                
                # Check if global (module-level)
                is_global = True
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        for child in parent.body:
                            if child is node:
                                is_global = False
                                break
                if is_global:
                    metrics.global_function_count += 1
            
            metrics.total_functions = total_funcs
            
            # Docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if (node.body and 
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant) and
                        isinstance(node.body[0].value.value, str)):
                        documented_funcs += 1
            
            # Check for patterns
            for i, line in enumerate(lines, 1):
                # Magic numbers
                for match in re.finditer(r"(?<!\w)(\d{3,5})(?!\w)", line):
                    num = int(match.group(1))
                    if num not in {0, 1, -1, 100, 200, 400, 404, 500, 86400, 1024}:
                        metrics.magic_number_count += 1
                        break
                
                # Long lines
                if len(line.rstrip()) > 100:
                    metrics.long_line_count += 1
                
                # TODO
                if re.search(r"#\s*(TODO|FIXME|HACK|XXX)", line):
                    metrics.todo_count += 1
                
                # print
                if re.search(r"\bprint\s*\(", line):
                    metrics.print_count += 1
            
            # Security
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ('eval', 'exec'):
                            metrics.security_issues += 1
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr == 'shell' and 'subprocess' in source:
                            metrics.security_issues += 1
                        elif node.func.attr in ('loads', 'load') and 'pickle' in source:
                            metrics.security_issues += 1
            
            # Bare except
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    metrics.bare_except_count += 1
        
        # Aggregates
        if all_func_lengths:
            metrics.avg_function_length = sum(all_func_lengths) / len(all_func_lengths)
        if all_complexities:
            metrics.avg_complexity = sum(all_complexities) / len(all_complexities)
        if all_params:
            metrics.avg_params_count = sum(all_params) / len(all_params)
        
        # Ratios
        if total_funcs > 0:
            metrics.type_hit_ratio = typed_funcs / total_funcs
            metrics.docstring_ratio = documented_funcs / total_funcs
        
        # Health score (weighted)
        score = 100.0
        
        # Penalties
        if metrics.avg_complexity > 5:
            score -= (metrics.avg_complexity - 5) * 3
        if metrics.avg_function_length > 30:
            score -= (metrics.avg_function_length - 30) * 0.5
        if metrics.max_complexity > 15:
            score -= 5
        if metrics.bare_except_count > 0:
            score -= metrics.bare_except_count * 3
        if metrics.print_count > 0:
            score -= metrics.print_count * 2
        if metrics.todo_count > 5:
            score -= (metrics.todo_count - 5)
        if metrics.type_hit_ratio < 0.5:
            score -= (0.5 - metrics.type_hit_ratio) * 20
        if metrics.docstring_ratio < 0.3:
            score -= (0.3 - metrics.docstring_ratio) * 15
        if metrics.long_line_count > 10:
            score -= (metrics.long_line_count - 10) * 0.5
        if metrics.security_issues > 0:
            score -= metrics.security_issues * 10
        if metrics.deep_nesting_count > 3:
            score -= (metrics.deep_nesting_count - 3) * 2
        
        metrics.health_score = max(0, min(100, score))
        
        # Test lines ratio
        test_files = [f for f in files if f.name.startswith("test_") or "/test_" in str(f)]
        test_lines = sum(len(f.read_text().splitlines()) for f in test_files 
                        if f.exists())
        if metrics.total_lines > 0:
            metrics.test_line_ratio = test_lines / metrics.total_lines
        
        metrics.duration_ms = (time.time() - start) * 1000
        
        return metrics
    
    def _complexity(self, node: ast.AST) -> int:
        score = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                  ast.And, ast.Or, ast.Assert)):
                score += 1
            elif isinstance(child, ast.BoolOp):
                score += len(child.values) - 1
        return score
    
    def _nesting_depth(self, node: ast.AST) -> int:
        max_depth = 0
        def walk(n: ast.AST, depth: int):
            nonlocal max_depth
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                              ast.For, ast.While, ast.If, ast.Try, ast.With)):
                depth += 1
                max_depth = max(max_depth, depth)
            for child in ast.iter_child_nodes(n):
                walk(child, depth)
        walk(node, 0)
        return max_depth


# ── Diff Analysis ────────────────────────────────────────────────────

@dataclass
class MetricsDiff:
    """Difference between two metric snapshots."""
    fields: dict[str, tuple[float, float, float]]  # name: (before, after, delta)
    health_change: float = 0.0
    total_delta: float = 0.0
    improved: list[str] = field(default_factory=list)
    regressed: list[str] = field(default_factory=list)


def compare_metrics(before: QualityMetrics, after: QualityMetrics) -> MetricsDiff:
    """Compare two metric snapshots."""
    diff = MetricsDiff()
    tracked = ["avg_complexity", "avg_function_length", "type_hit_ratio",
               "docstring_ratio", "high_complexity_count", "bare_except_count",
               "print_count", "todo_count", "long_line_count", "security_issues"]
    
    for field_name in tracked:
        before_val = getattr(before, field_name, 0)
        after_val = getattr(after, field_name, 0)
        if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
            delta = after_val - before_val
            diff.fields[field_name] = (before_val, after_val, delta)
            
            # Determine improvement or regression
            # (lower is better for most, higher is better for ratios)
            better_lower = field_name not in ["type_hit_ratio", "docstring_ratio", "health_score"]
            
            if better_lower:
                if delta < 0:
                    diff.improved.append(field_name)
                elif delta > 0:
                    diff.regressed.append(field_name)
            else:
                if delta > 0:
                    diff.improved.append(field_name)
                elif delta < 0:
                    diff.regressed.append(field_name)
    
    diff.health_change = after.health_score - before.health_score
    diff.total_delta = after.health_score - before.health_score
    
    return diff


# ── Reporting ────────────────────────────────────────────────────────

def format_metrics(m: QualityMetrics, verbose: bool = True) -> str:
    """Format metrics as readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("📊 Quality Metrics Report")
    lines.append("=" * 60)
    lines.append(f"Generated: {m.timestamp}")
    lines.append("")
    
    # Score
    score_color = "🟢" if m.health_score >= 80 else "🟡" if m.health_score >= 50 else "🔴"
    lines.append(f"📈 Health Score: {score_color} {m.health_score:.1f}/100")
    lines.append("")
    
    # Volume
    lines.append("📐 Volume:")
    lines.append(f"  Files: {m.total_files}")
    lines.append(f"  Lines: {m.total_lines}")
    lines.append(f"  Functions: {m.total_functions}")
    lines.append(f"  Classes: {m.total_classes}")
    lines.append("")
    
    # Complexity
    lines.append("🔍 Complexity:")
    lines.append(f"  Avg function length: {m.avg_function_length:.1f} lines")
    lines.append(f"  Max function length: {m.max_function_length} lines")
    lines.append(f"  Avg complexity: {m.avg_complexity:.1f}")
    lines.append(f"  Max complexity: {m.max_complexity}")
    lines.append(f"  High complexity (>{10}): {m.high_complexity_count}")
    lines.append(f"  Deep nesting (>{4}): {m.deep_nesting_count}")
    lines.append("")
    
    # Quality
    lines.append("⭐ Quality:")
    lines.append(f"  Type hints: {m.type_hit_ratio:.0%}")
    lines.append(f"  Docstrings: {m.docstring_ratio:.0%}")
    lines.append(f"  Long lines: {m.long_line_count}")
    lines.append(f"  Magic numbers: {m.magic_number_count}")
    lines.append(f"  Bare except: {m.bare_except_count}")
    lines.append(f"  Print statements: {m.print_count}")
    lines.append(f"  TODOs: {m.todo_count}")
    lines.append(f"  Security issues: {m.security_issues}")
    lines.append("")
    
    # Maintainability
    lines.append("🛠️ Maintainability:")
    lines.append(f"  Avg params: {m.avg_params_count:.1f}")
    lines.append(f"  Global functions: {m.global_function_count}")
    lines.append(f"  Test/source ratio: {m.test_line_ratio:.1%}")
    lines.append("")
    
    lines.append(f"Collected in {m.duration_ms:.0f}ms")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_diff(diff: MetricsDiff) -> str:
    """Format diff report."""
    lines = []
    lines.append("=" * 60)
    lines.append("📊 Quality Diff Analysis")
    lines.append("=" * 60)
    lines.append("")
    
    if diff.health_change > 0:
        lines.append(f"📈 Health Score: +{diff.health_change:.1f} 🟢")
    elif diff.health_change < 0:
        lines.append(f"📉 Health Score: {diff.health_change:.1f} 🔴")
    else:
        lines.append(f"➡️ Health Score: unchanged")
    lines.append("")
    
    if diff.improved:
        lines.append("✅ Improved:")
        for name in diff.improved:
            b, a, d = diff.fields[name]
            arrow = "↓" if d < 0 else "↑"
            lines.append(f"  {arrow} {name}: {b:.2f} → {a:.2f} ({d:+.2f})")
    
    if diff.regressed:
        lines.append("")
        lines.append("❌ Regressed:")
        for name in diff.regressed:
            b, a, d = diff.fields[name]
            arrow = "↑" if d > 0 else "↓"
            lines.append(f"  {arrow} {name}: {b:.2f} → {a:.2f} ({d:+.2f})")
    
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(m: QualityMetrics) -> str:
    """JSON output for CI."""
    return json.dumps(asdict(m), indent=2, ensure_ascii=False)


# ── Snapshot persistence ─────────────────────────────────────────────

SNAPSHOT_DIR = Path.home() / ".mega-coding" / "metrics"


def save_snapshot(metrics: QualityMetrics, label: str = "current") -> Path:
    """Save metrics snapshot to disk."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{label}.json"
    path.write_text(json.dumps(asdict(metrics), indent=2, ensure_ascii=False))
    return path


def load_snapshot(label: str = "current") -> QualityMetrics | None:
    """Load metrics snapshot from disk."""
    path = SNAPSHOT_DIR / f"{label}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return QualityMetrics(**data)


def load_history() -> list[tuple[str, QualityMetrics]]:
    """Load all historical snapshots."""
    if not SNAPSHOT_DIR.exists():
        return []
    results = []
    for f in sorted(SNAPSHOT_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        results.append((f.stem, QualityMetrics(**data)))
    return results


# ── Main ─────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    
    parser = argparse.ArgumentParser(
        description="📊 Quality Metrics & Feedback System",
    )
    parser.add_argument("path", nargs="?", default=".", help="File or directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--diff", type=str, help="Compare with snapshot label")
    parser.add_argument("--history", action="store_true", help="Show history")
    parser.add_argument("--save", type=str, default=None, help="Save snapshot as label")
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard")
    args = parser.parse_args()
    
    collector = MetricsCollector(args.path)
    metrics = collector.collect()
    
    # Save if requested
    if args.save:
        save_snapshot(metrics, args.save)
        print(f"✅ Snapshot saved: {SNAPSHOT_DIR / args.save}.json")
    
    # Diff analysis
    if args.diff:
        before = load_snapshot(args.diff)
        if before:
            diff = compare_metrics(before, metrics)
            if args.json:
                print(json.dumps({
                    "health_change": diff.health_change,
                    "improved": diff.improved,
                    "regressed": diff.regressed,
                    "details": {k: {"before": b, "after": a, "delta": d} 
                               for k, (b, a, d) in diff.fields.items()},
                }, indent=2))
            else:
                print(format_diff(diff))
        else:
            print(f"❌ Snapshot '{args.diff}' not found")
            return 1
    
    # History
    if args.history:
        history = load_history()
        if not history:
            print("No history available")
        else:
            print("📈 Quality History:")
            for label, m in history[-10:]:
                print(f"  {label}: {m.health_score:.1f}")
    
    # Dashboard
    if args.dashboard:
        history = load_history()
        if history:
            scores = [m.health_score for _, m in history]
            avg = sum(scores) / len(scores)
            trend = scores[-1] - scores[0] if len(scores) > 1 else 0
            print("📊 Mega-Coding Dashboard")
            print("=" * 40)
            print(f"Current score: {metrics.health_score:.1f}")
            print(f"Average: {avg:.1f}")
            print(f"Trend: {'📈' if trend > 0 else '📉'} {trend:+.1f}")
            print(f"Checks: {len(history)}")
    
    # Output
    if args.json:
        print(format_json(metrics))
    else:
        print(format_metrics(metrics))
    
    return 1 if metrics.health_score < 50 else 0


if __name__ == "__main__":
    sys.exit(main())
