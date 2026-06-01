# Architecture

## mega-coding skill structure

```
mega-coding/
├── SKILL.md                 # главный файл с инструкциями
├── CHANGELOG.md             # история изменений
├── Dockerfile               # контейнер с инструментом
├── .editorconfig            # единые настройки редактора
├── .pre-commit-config.yaml  # pre-commit хуки
│
├── agents/                  # AI agent конфиги
│   └── openai.yaml
│
├── assets/                  # boilerplate-шаблоны
│   ├── boilerplate-aiogram.md
│   ├── boilerplate-fastapi.md
│   ├── boilerplate-cli.md
│   ├── boilerplate-package.md
│   └── ...
│
├── references/              # гайды и референсы
│   ├── aiogram-guides.md
│   ├── python-patterns.md
│   ├── git-workflow.md
│   ├── extra/               # дополнительные гайды
│   │   ├── security-best-practices.md
│   │   ├── testing-guide.md
│   │   ├── async-patterns.md
│   │   └── ...
│
├── templates/               # шаблоны проектов
│   ├── fastapi/
│   ├── cli/
│   ├── bot/
│   └── lib/
│
├── scripts/                 # утилиты для проверки
│   ├── check-quality.py
│   ├── lint-runner.py
│   ├── security-check.py
│   ├── check-complexity.py
│   ├── check-docstrings.py
│   ├── check-types.py
│   ├── check-unused-imports.py
│   ├── check-dead-code.py
│   ├── benchmark.py
│   ├── setup-dev.sh
│   └── git-hooks/
│       └── pre-commit
│
├── examples/                # примеры использования
│   ├── quickstart.py
│   └── advanced-usage.py
│
├── docs/                    # документация
│   └── architecture.md
│
├── rulesAI/                 # правила для ИИ
│   ├── rules.txt
│   ├── rulesai.txt
│   └── extra/
│       ├── coding-standards.md
│       └── review-checklist.md
│
└── .github/workflows/       # CI/CD
    ├── ci.yml
    ├── lint.yml
    └── publish.yml
```

## Core Principles
1. **Monolith by default** — не плоди файлы без нужды
2. **Eat your own dog food** — код соответствует своим же стандартам
3. **Auto-lint** — проверка после каждого изменения
4. **DRY, KISS, YAGNI, SOLID** — где уместно
