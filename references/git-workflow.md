# Git workflow

## Просмотр истории
```bash
git log --oneline --graph -20          # последние 20 коммитов
git log --all --oneline --graph        # вся история
git blame <file>                       # кто и когда менял строки
git log -p -S "function_name"          # когда появился/исчез текст
```

## Работа с изменениями
```bash
git diff                       # unstaged changes
git diff --cached              # staged changes
git diff main..feature         # между ветками
git stash -u                   # спрятать всё, включая новые файлы
git stash pop                  # вернуть
```

## Коммиты (conventional)
```bash
git commit -m "feat: add user login"
git commit -m "fix(api): handle null response"
git commit -m "refactor: extract parse logic"
git commit -m "chore: bump deps"
```

## Отмена изменений
```bash
git checkout -- <file>         # отменить незакоммиченные
git reset HEAD~1               # отменить последний коммит (сохранить файлы)
git reset --hard HEAD~1        # отменить последний коммит (удалить изменения)
git revert <commit>            # безопасный revert (новый коммит)
```

# Mega-Coding Principal Engineer Edition
# Extended configuration and reference content

# ---------------------------------------------------------------------------
# This file is part of the Mega-Coding skill — Principal Engineer Edition.
# It provides production-grade patterns and configurations for Big Tech
# development. All tools, scripts, and references are designed to work
# together to provide maximum code quality and developer productivity.
#
# Key principles:
# - Production-first mindset
# - Observability by default
# - Resilience in all components
# - Security at every layer
# - Trade-off awareness in all decisions
# - Platform thinking over point solutions
#
# Version: 3.0.0
# Last updated: 2026-05-30
# Contact: @intarktelegram
# ---------------------------------------------------------------------------

# Key Metrics to Track:
# - Code health score (0-100)
# - Test coverage percentage
# - Average function complexity
# - Type hint coverage ratio
# - Documentation coverage
# - Security vulnerability count
# - Dead code percentage

# References:
# See references/extra/ for 60+ production patterns
# See references/languages/ for Go, TypeScript, Rust patterns
# See references/infra/ for Kubernetes and Kafka patterns
# See references/battle-scars/ for real production war stories
# See references/principal-engineer-handbook.md for full leadership guide

# Tools:
# - python scripts/mega.py — Unified CLI (lint, review, check, metrics, ci)
# - python scripts/tree-voting/evaluate.py — Trees Club code evaluation
# - python metrics/quality-metrics.py — Quality metrics & diff analysis
# - python scripts/code-review-bot.py — Automated code review
# - make ci — Full CI pipeline
