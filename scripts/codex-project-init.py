#!/usr/bin/env python3
"""Генератор проектов. Создаёт готовую структуру за секунду.

Usage:
    python scripts/codex-project-init.py --type fastapi --name myapp
    python scripts/codex-project-init.py --type bot --name mybot
    python scripts/codex-project-init.py --type cli --name mytool
    python scripts/codex-project-init.py --type lib --name mylib
    python scripts/codex-project-init.py --type all  # список типов
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent.parent
TEMPLATES = BASE / "templates"
ASSETS = BASE / "assets"

# ── Project types and their configs ────────────
PROJECT_TYPES: dict[str, dict[str, Any]] = {
    "fastapi": {
        "description": "FastAPI async REST API",
        "dirs": ["src", "tests", "migrations"],
        "files": {
            "main.py": TEMPLATES / "fastapi" / "main.py",
            "requirements.txt": TEMPLATES / "fastapi" / "requirements.txt",
            ".env.example": TEMPLATES / "fastapi" / ".env.example",
            "README.md": None,
            "Dockerfile": None,
            ".gitignore": None,
        },
        "extra_cmds": [
            ["python", "-m", "venv", ".venv"],
        ],
    },
    "bot": {
        "description": "Aiogram 3 Telegram bot",
        "dirs": ["src", "tests"],
        "files": {
            "bot.py": TEMPLATES / "bot" / "main.py",
            "requirements.txt": TEMPLATES / "bot" / "requirements.txt",
            ".env.example": TEMPLATES / "bot" / ".env.example",
            "README.md": None,
        },
        "extra_cmds": [],
    },
    "cli": {
        "description": "CLI tool (argparse)",
        "dirs": ["src", "tests"],
        "files": {
            "cli.py": TEMPLATES / "cli" / "main.py",
            "requirements.txt": TEMplates / "cli" / "requirements.txt",
            "README.md": None,
        },
        "extra_cmds": [],
    },
    "lib": {
        "description": "Python library",
        "dirs": ["src/mylib", "tests"],
        "files": {
            "src/mylib/__init__.py": None,
            "src/mylib/core.py": TEMPLATES / "lib" / "main.py",
            "setup.py": TEMPLATES / "lib" / "setup.py",
            "README.md": None,
        },
        "extra_cmds": [],
    },
}


def create_project(project_type: str, name: str, output_dir: Path | None = None,
                   force: bool = False) -> int:
    """Create a new project from template."""
    config = PROJECT_TYPES.get(project_type)
    if not config:
        print(f"❌ Unknown project type: {project_type}", file=sys.stderr)
        return 1
    
    target = (output_dir or Path.cwd()) / name
    if target.exists():
        if not force:
            print(f"❌ Directory already exists: {target}", file=sys.stderr)
            print("   Use --force to overwrite")
            return 1
        shutil.rmtree(target)
    
    # Create directories
    for d in config["dirs"]:
        (target / d).mkdir(parents=True, exist_ok=True)
    print(f"  📁 Created directories: {', '.join(config['dirs'])}")
    
    # Create files
    for dest_name, src_path in config["files"].items():
        dest = target / dest_name
        if src_path and src_path.exists():
            shutil.copy2(src_path, dest)
            print(f"  📄 Copied: {dest_name}")
        else:
            # Create empty or default content
            content = _default_content(dest_name, name, project_type)
            dest.write_text(content)
            print(f"  📄 Created: {dest_name}")
    
    # Run extra commands
    for cmd in config.get("extra_cmds", []):
        try:
            subprocess.run(cmd, cwd=target, check=False)
        except Exception as e:
            print(f"  ⚠️  Command failed: {' '.join(cmd)}: {e}")
    
    print(f"\n✅ Created {project_type} project at: {target}")
    print(f"   cd {target}")
    return 0


def _default_content(filename: str, name: str, ptype: str) -> str:
    """Generate default content for files without template."""
    if filename == "README.md":
        return f"# {name}\n\n{PROJECT_TYPES[ptype]['description']} project.\n\n## Install\n\n...\n\n## Usage\n\n...\n"
    if filename == "Dockerfile":
        return (
            f"FROM python:3.12-slim\n\n"
            f"WORKDIR /app\n"
            f"COPY requirements.txt .\n"
            f"RUN pip install --no-cache-dir -r requirements.txt\n"
            f"COPY . .\n\n"
            f"CMD [\"python\", \"main.py\"]\n"
        )
    if filename == ".gitignore":
        return (
            "__pycache__/\n*.pyc\n*.pyo\n.env\n.venv/\nvenv/\n"
            "*.egg-info/\ndist/\nbuild/\n.pytest_cache/\n.ruff_cache/\n"
            ".mypy_cache/\n.mypy_cache/\n*.so\n.DS_Store\n"
        )
    if filename.endswith("__init__.py"):
        return f"\"\"\"{name} package.\"\"\"\nfrom __future__ import annotations\n\n__version__ = \"0.1.0\"\n"
    return ""


def list_types() -> None:
    """List available project types."""
    print("Available project types:\n")
    for name, config in sorted(PROJECT_TYPES.items()):
        print(f"  {name:<12} {config['description']}")
    print()

def list_templates() -> int:
    """List all templates with sizes."""
    print("Templates available:\n")
    for tdir in sorted(TEMPLATES.iterdir()):
        if tdir.is_dir():
            size = sum(f.stat().st_size for f in tdir.rglob("*") if f.is_file())
            files = [f.name for f in tdir.iterdir() if f.is_file()]
            print(f"  {tdir.name:<12} ({size:>6} bytes) {', '.join(files)}")
    print()
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate project from mega-coding templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--type", "-t", choices=list(PROJECT_TYPES) + ["all"], 
                        default="fastapi", help="Project type")
    parser.add_argument("--name", "-n", default="myapp", help="Project name")
    parser.add_argument("--dir", "-d", type=Path, default=None, help="Output directory")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")
    parser.add_argument("--list", "-l", action="store_true", help="List templates")
    
    args = parser.parse_args(argv)
    
    if args.list:
        list_templates()
        return
    
    if args.type == "all":
        list_types()
        return
    
    sys.exit(create_project(args.type, args.name, args.dir, args.force))


if __name__ == "__main__":
    main()
