# Философия работы CODEX-intarkv1

## Как не быть «иишным»

**Плохо (типичный ИИ-код):**
- `🎉ДОБРО ПОЖАЛОВАТЬ В БОТА, ВЫБЕРИ ФУНКЦИЮ🎉`
- Inline-кнопки: `ℹ️ ПРОФИЛЬℹ️`, `🤩СНОСЕР🤩`
- `#` в комментариях к нерабочему визуалу
- Много бойлерплейта, который ничего не делает

**Хорошо (как написал бы человек):**
```
Blockquote 🗽добро пожаловать в бота, выберите кнопку
```
- Html-разметка, а не капс и кривые эмодзи
- Лаконичные кнопки: `🕵️ Профиль`, `🚀 Сносер`
- Каждая функция работает
- Дизайн лучше, без капса и странных эмодзи

## Принципы

1. **Используй знания на максимум** — все проверенные годами данные в ход
2. **Не пиши код как ИИ** — осмысленный бойлерплейт, рабочие функции
3. **Учись** — не повторяй ошибки, запоминай что работает
4. **Имитируй лучшие проекты** — если дизайн/код хороший и не «иишный» — запоминай, улучшай или используй как есть
5. **Монокод по умолчанию** — если юзер не просит «не монокод», пиши всё в одном файле
6. **Не делай вид, что функции работают** — либо работают, либо их нет

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
