---
name: mega-coding
description: >
  Кодируй как Principal Engineer в Big Tech. Быстро, чисто, надёжно.
  Speed Mode для быстрого прототипирования, Principal-Level Principles
  для production-кода, 4 языка, инфраструктура, метрики, боевые истории.
  Включает скрипты, бойлерплейты, референсы и полный тулчейн качества.
---

# 🚀 Mega-Coding — Principal Engineer Edition

**Кодируй как Principal Engineer в Big Tech. Быстро, чисто, надёжно, масштабируемо.**

## ⚡ Speed Mode

### Задача → Действие → Бойлерплейт

| Ситуация | Что делать | Шаблон |
|----------|-----------|--------|
| **Новый проект** | `python scripts/mega.py init --type fastapi` | `templates/` или `assets/boilerplate-*` |
| **Новая фича** | Понять → Найти похожий паттерн → Написать тест → Код | Копировать стиль проекта |
| **Баг** | `git log -S "функция"` → `git blame` → тест → фикс | Сначала тест, потом код |
| **Рефакторинг** | Изолировать → Тесты → Маленькие шаги → `git diff` после каждого | `references/extra/refactoring-recipes.md` |
| **Оптимизация** | Профилировать (`cProfile`/`py-spy`) → Измерить → Оптимизировать узкое место | `references/extra/performance-patterns.md` |
| **Code Review** | `python scripts/mega.py review` — Trees Club | `references/extra/code-review-guide.md` |
| **Quality Check** | `python scripts/mega.py check` — полный аудит | `metrics/quality-metrics.py` |
| **CI Pipeline** | `make ci` — всё сразу | `.github/workflows/ci.yml` |

### Принцип трёх касаний
1. **Понять** — `rg`, `fd`, `git log`, `git blame` (макс 30с)
2. **Спроектировать** — 1 мысль: простота > читаемость > производительность (макс 10с)  
3. **Написать** — тест → код → прогнать тесты (макс 5 мин на функцию)

## 🧠 Principal Engineer Mindset

### От Senior к Principal

```
Senior                    Principal
──────────────────────────────────────────────
Решает проблемы           Определяет проблемы
Оптимизирует систему      Переопределяет систему
Работает в рамках         Создаёт рамки для других
Умеет хорошо писать код   Знает, какой код не надо писать
Влияет на команду         Влияет на организацию
Думает в месяцах          Думает в годах
```

### Критерии хорошего кода
1. **Работает** — решает задачу без багов
2. **Читается** — через месяц ты или другой разработчик поймёт за 5 секунд
3. **Меняется** — добавить новое поведение без переписывания всего
4. **Производителен** — достаточно быстро для задачи (не быстрее)
5. **Надёжен** — обрабатывает ошибки, retry, circuit breaker
6. **Наблюдаем** — логи, метрики, трейсы из коробки

### Что Principal знает, а Senior — нет
- **Trade-off мышление** — любое решение это компромисс, осознай его
- **Platform thinking** — создавай API и инструменты, а не решения
- **SLO-driven development** — знай свои SLO, живи по error budget
- **Cost-awareness** — каждое решение имеет стоимость (инфра, поддержка)
- **Bias for action** — принимай решения с неполной информацией
- **Organizational influence** — меняй процессы, не только код
- **Technical Debt management** — управляй долгом, не избегай его

### Когда нарушать правила
- **DRY**: нарушить, когда абстракция сложнее дублирования (правило трёх)
- **SOLID**: ISP и DIP — всегда; SRP и OCP — часто; LSP — редко, только для иерархий
- **YAGNI**: отличное правило — не писать код, который не нужен сейчас
- **Type hints**: не обязательно для внутренних функций/скриптов, обязательно для публичного API

### Пирамида решений

```
СЛОЖНОСТЬ →
  │
  ├─ Простая логика → if/elif/else, match/case, comprehension  
  ├─ Средняя → Strategy, Factory, Builder, Adapter
  ├─ Сложная → Композиция сервисов, CQRS, Event Sourcing
  └─ Очень сложная → Модули, плагины, message queue, distributed systems
```

Не усложняй: простое решение для простой задачи > "правильное" решение для воображаемой сложности.

## 🌐 Мультиязычная поддержка

| Язык | Reference | Применение |
|------|-----------|------------|
| **Python** | `references/extra/` | Backend, data, ML, инфраструктура |
| **Go** | `references/languages/go-patterns.md` | Микросервисы, CLI, high-performance |
| **TypeScript** | `references/languages/typescript-patterns.md` | Frontend, Node.js, full-stack |
| **Rust** | `references/languages/rust-patterns.md` | Systems programming, критические сервисы |

| Инфраструктура | Reference | Применение |
|----------------|-----------|------------|
| **Kubernetes** | `references/infra/kubernetes-patterns.md` | Оркестрация, деплой, скейлинг |
| **Kafka** | `references/infra/kafka-patterns.md` | Event streaming, pipelines |
| **Docker** | `assets/boilerplate-docker-compose.md` | Контейнеризация |
| **CI/CD** | `references/extra/cd-deployment-patterns.md` | Паплайны, доставка |

## 🛠 Единый тулчейн (Unified CLI)

Всё через одну команду `python scripts/mega.py`:

| Команда | Что делает |
|---------|-----------|
| `mega.py lint [path]` | Полный линтинг (ruff → mypy → bandit) |
| `mega.py review [path]` | Код-ревью + Trees Club оценка |
| `mega.py check [path]` | Quality check (всё вместе) |
| `mega.py metrics [path]` | Метрики качества кода |
| `mega.py diff [commit]` | Diff-анализ |
| `mega.py init --type fastapi\|cli\|bot\|lib` | Создать проект |
| `mega.py ci` | Полный CI pipeline |
| `mega.py version` | Версия скилла |

Или через Makefile:
```bash
make install    # Установка
make lint       # Линтинг
make check      # Проверка качества
make review     # Код-ревью + деревья
make metrics    # Метрики
make ci         # Полный CI
```

## 🌳 Совет Деревьев (Live Code Evaluation)

6 судей оценивают код и выносят вердикт. Интегрирован в `mega review`:

```bash
python scripts/tree-voting/evaluate.py src/
python scripts/tree-voting/evaluate.py --diff     # git diff
python scripts/tree-voting/evaluate.py --ci       # JSON для CI
python scripts/tree-voting/evaluate.py --pr-comment  # Формат PR
```

**Деревья:**
- 🌳 **Дуб** — Архитектура и дизайн (функции vs классы, сложность, SRP)
- 🌲 **Берёза** — Асинхронность (blocking calls, event loop, concurrency)
- 🌲 **Сосна** — Структура и модульность (imports, размер файла)
- 🍁 **Клён** — Чистота кода (нейминг, магические числа, длина строк)
- 🌿 **Ива** — Обработка ошибок (bare except, timeout, fallback)
- 🌳 **Ясень** — Тестируемость и сопровождаемость (DI, глобальное состояние)

Результат: 4+ голоса «Человек» = код принят. «НЬЮ» = требуется переработка.

## 📊 Метрики Качества (Feedback System)

```bash
python metrics/quality-metrics.py src/              # Текущие метрики
python metrics/quality-metrics.py src/ --save v2     # Сохранить снимок
python metrics/quality-metrics.py src/ --diff v1     # Сравнить с v1
python metrics/quality-metrics.py src/ --history     # История изменений
python metrics/quality-metrics.py src/ --dashboard   # Дашборд
```

Метрики: сложность, длина функций, type hints, docstrings, магические числа, bare except, TODO, print

## 🔥 Battle Scars: Production War Stories

Реальные истории из Big Tech с кодом, уроками и цифрами:
- Connection Pool: Как уронили прод в 3 часа ночи
- Parse, don't validate: Как спасли сервис от RCE
- Async vs Sync: Как payment-сервис лёг под нагрузкой
- Retry Storm: Как 3 микросервиса убили друг друга
- Memory Leak: Как 200GB RAM исчезли за ночь
- Database Deadlock: Как SELECT FOR UPDATE положил всё
- Configuration Drift: 3 окружения, 3 разных поведения
- Timeout: Как отключали сервисы в неправильном порядке

## 🏗 Production Patterns (Python, Golang, TypeScript, Rust)

См. полные reference:
- `references/extra/production-patterns.md` — Connection Pool, Circuit Breaker, Retry, Saga, Feature Flags
- `references/extra/distributed-systems-patterns.md` — Distributed Lock, Consistent Hashing, Gossip
- `references/languages/go-patterns.md` — Error handling, Worker Pool, Graceful Shutdown
- `references/languages/typescript-patterns.md` — FSM, Result Type, Branded Types
- `references/languages/rust-patterns.md` — anyhow, Tokio, Zero-Cost Abstractions

## 📦 Все ресурсы скилла

### Шаблоны и бойлерплейты
- `templates/fastapi/` — FastAPI + async SQLAlchemy + Redis
- `templates/bot/` — Telegram bot (aiogram 3)
- `templates/cli/` — CLI с argparse/click
- `templates/lib/` — Python библиотека
- `assets/boilerplate-*.md` — 18 штук

### Гайды и справочники
- `references/extra/` — 60+ глубоких reference
- `references/languages/` — Go, TypeScript, Rust
- `references/infra/` — Kubernetes, Kafka
- `references/battle-scars/` — Production war stories
- `references/principal-engineer-handbook.md` — Полный handbook

### Скрипты
| Скрипт | Описание |
|--------|----------|
| `scripts/mega.py` | **Unified CLI** — точка входа во всё |
| `scripts/tree-voting/evaluate.py` | **Trees Club** — живая оценка кода |
| `scripts/code-review-bot.py` | Автоматическое код-ревью |
| `scripts/check-quality.py` | 15 проверок качества |
| `scripts/lint-runner.py` | Ruff → mypy → bandit |
| `scripts/security-check.py` | Поиск уязвимостей |
| `scripts/benchmark.py` | Бенчмаркинг |
| `scripts/check-complexity.py` | Цикломатическая сложность |
| `scripts/check-dead-code.py` | Мёртвый код |
| `scripts/check-docstrings.py` | Докстринги |
| `scripts/check-types.py` | Type hints |
| `scripts/check-unused-imports.py` | Неиспользуемые импорты |
| `metrics/quality-metrics.py` | Метрики и diff-анализ |
| `scripts/codex-project-init.py` | Создание проектов |

### CI/CD
- `.github/workflows/ci.yml` — Тесты на 3.10-3.12
- `.github/workflows/lint.yml` — Все линтеры
- `.github/workflows/publish.yml` — Публикация на PyPI
- `Makefile` — `install`, `test`, `lint`, `format`, `check`, `review`, `metrics`, `ci`

### Чеклисты

**Перед PR (30 секунд)**
- [ ] `ruff check . && ruff format --check .`
- [ ] `python scripts/mega.py check src/`
- [ ] Новые тесты проходят
- [ ] Нет `print()`, `# TODO`, хардкода
- [ ] Type hints на публичных функциях
- [ ] `git diff` — только нужные изменения

**Код-ревью (60 секунд)**
- [ ] Понимаю что делает — да/нет
- [ ] Edge cases покрыты — да/нет
- [ ] Дублирование — да/нет
- [ ] Тесты покрывают — да/нет
- [ ] Ошибки обработаны — да/нет
- [ ] Безопасность — да/нет
- [ ] Производительность — да/нет
- [ ] Observability — да/нет

---

*С любовью — команда @intarktelegram*
