# Code Review Checklist

## Общее
- [ ] Код читаемый и понятный
- [ ] Нет дублирования (DRY)
- [ ] Нет dead code
- [ ] Нет TODO/FIXME без issue

## Безопасность
- [ ] Нет инъекций (SQL, command, XSS)
- [ ] Нет хардкоженных секретов
- [ ] Валидация входных данных
- [ ] Зависимости проверены

## Тесты
- [ ] Тесты покрывают новую логику
- [ ] Крайние случаи обработаны
- [ ] Нет сломанных тестов
- [ ] Тесты не зависят друг от друга

## Производительность
- [ ] Нет O(n²) где можно O(n)
- [ ] Ненужные запросы/вычисления
- [ ] Кэширование где уместно
- [ ] Асинхронность для I/O

## Документация
- [ ] README обновлён если нужно
- [ ] Docstrings для публичного API
- [ ] Примеры использования
- [ ] CHANGELOG / release notes

# Extended Review Checklist

## Deep Dive Checks

### Memory & Performance
- [ ] No unbounded data structures (list/dict/set growing infinitely)
- [ ] No N+1 database queries
- [ ] Async functions use asyncio.gather/TaskGroup for concurrent operations
- [ ] Timeouts on all external calls (database, cache, API)
- [ ] Connection pool configured correctly

### Security
- [ ] No hardcoded secrets or tokens
- [ ] Input validation on all API endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention in any user-facing output
- [ ] Rate limiting on public endpoints
- [ ] Authentication/authorization on all endpoints

### Production Readiness
- [ ] Graceful shutdown implemented
- [ ] Health check endpoints (/health/live, /health/ready)
- [ ] Structured logging (JSON format)
- [ ] Metrics for key operations (RED metrics)
- [ ] Feature flags for new functionality
- [ ] Circuit breakers for external dependencies
- [ ] Retry with exponential backoff for transient failures

### Code Quality
- [ ] Type hints on all public functions
- [ ] Average complexity < 5, maximum < 15
- [ ] Functions < 50 lines
- [ ] No dead code or commented-out code
- [ ] Tests for new functionality (unit + integration)
- [ ] Tests cover error paths and edge cases
- [ ] Documentation updated (README, API docs, CHANGELOG)

## Principal Engineer Review

When reviewing as Principal Engineer, focus on:
1. **Strategic fit** — Does this align with our architecture?
2. **Trade-offs** — Are they documented and conscious?
3. **Future-proofing** — Will this work in 6 months?
4. **Simplicity** — Is there a simpler solution?
5. **Observability** — Can we debug this in production?
6. **Security** — Have all attack vectors been considered?
7. **Cost** — What's the operational cost?
