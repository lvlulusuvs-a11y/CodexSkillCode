# 📘 The Principal Engineer Handbook

**Как мыслить, проектировать и работать на уровне Principal Engineer в Big Tech.**

---

## Часть 1: Мышление Principal Engineer

### 1.1 Что отличает Principal от Senior

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

**Principal Engineer — это не Senior++, это другая профессия.**

### 1.2 Стратегическое мышление

**Trade-off Canvas** — инструмент принятия решений:

```
Проблема:                   [описание]
Варианты:                   [A, B, C]
Критерии оценки:
  - Скорость реализации     [1-5]
  - Масштабируемость        [1-5]
  - Cost of delay           [1-5]
  - Технический долг        [1-5]
  - Организационный риск    [1-5]
Лучший вариант:             [выбор]
Почему:                     [аргументация]
Что не выбираем:            [отложенные решения]
```

**Правило 80/20:** 20% архитектурных решений определяют 80% стоимости системы.  
Найди эти 20% и потрать 80% времени на их обдумывание.

### 1.3 Bias for Action vs Analysis Paralysis

Principal Engineer должен уметь принимать решения с неполной информацией.

**Decision Matrix:**

| Информация есть | Решения обратимы | Решения необратимы |
|----------------|-----------------|-------------------|
| **Достаточно** | Делегируй | Принимай |
| **Недостаточно** | Экспериментируй | Анализируй |

**Если решение обратимо и у тебя достаточно информации — просто прими его.**  
Не жди идеальных данных.

### 1.4 Managing Technical Debt

```python
class TechnicalDebtTracker:
    """
    Систематический подход к техническому долгу.
    Не элиминация — управление.
    """
    
    def __init__(self):
        self.items: list[DebtItem] = []
    
    def register(self, description: str, impact: str, 
                 cost_to_fix: int, risk: str):
        self.items.append(DebtItem(
            description=description,
            impact=impact,
            cost_to_fix=cost_to_fix,  # story points
            risk=risk,  # LOW/MED/HIGH/CRITICAL
            created=datetime.now(),
        ))
    
    def prioritize(self) -> list[DebtItem]:
        """RICE prioritization."""
        def score(item: DebtItem) -> float:
            reach = item.impact_scope
            impact = item.risk_score()
            confidence = item.confidence
            effort = max(item.cost_to_fix, 1)
            return (reach * impact * confidence) / effort
        return sorted(self.items, key=score, reverse=True)
```

**Правила управления долгом:**
1. Долг неизбежен — вопрос в управлении, не элиминации
2. 20% долга вызывает 80% проблем — найди эти 20%
3. Долг с процентной ставкой (растёт) — гаси первым
4. Долг без процентов — может подождать

---

## Часть 2: Архитектура на уровне Big Tech

### 2.1 System Design Interview: Framework

```
1. Understand requirements (5 min)
   - Functional: что система делает
   - Non-functional: SLA, scalability, consistency
   - Constraints: budget, team, timeline

2. High-level design (10 min)
   - Components, data flow, APIs
   - Лучше нарисовать на доске

3. Deep dive (15 min)
   - Выбери 1-2 сложных компонента
   - Discuss trade-offs
   - Data model, storage, caching

4. Scaling & bottlenecks (10 min)
   - Где узкие места?
   - Как масштабировать?
   - Cost analysis

5. Wrap-up (5 min)
   - Что ещё можно улучшить?
   - Alternative approaches
```

### 2.2 Real-World Architecture Patterns

#### CQRS (Command Query Responsibility Segregation)

```python
# Команды — мутация данных
class CreateOrderCommand:
    def execute(self, input: CreateOrderInput) -> OrderId:
        async with db.transaction():
            order = Order.create(input)
            event = OrderCreatedEvent(order.id, order.total)
            event_bus.publish(event)
        return order.id

# Запросы — чтение данных (отдельная модель)
class OrderQuery:
    def get_order_summary(self, user_id: str) -> OrderSummaryDTO:
        # Читает из read-optimized store (denormalized)
        return self.read_db.fetch_one(
            "SELECT * FROM order_summary WHERE user_id = ?",
            [user_id]
        )
```

**Когда нужен:**  
- Разные модели чтения и записи  
- Высокая нагрузка на чтение  
- Командная и query-части масштабируются независимо  
- Event sourcing  

**Когда не нужен:**  
- CRUD с простой бизнес-логикой  
- Маленькие проекты  
- Нет проблем с производительностью

#### Event Sourcing

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Account:
    id: str
    version: int = 0
    events: List[Event] = field(default_factory=list)
    
    def apply(self, event: Event) -> None:
        match event:
            case AccountCreated(initial_balance=bal):
                self.balance = bal
            case MoneyDeposited(amount=a):
                self.balance += a
            case MoneyWithdrawn(amount=a):
                self.balance -= a
        self.version += 1
    
    def process(self, command: Command) -> List[Event]:
        match command:
            case DepositMoney(amount=a):
                return [MoneyDeposited(self.id, a)]
            case WithdrawMoney(amount=a):
                if self.balance < a:
                    raise InsufficientFunds(self.id, self.balance, a)
                return [MoneyWithdrawn(self.id, a)]

# Восстановление состояния из событий:
def rebuild_account(events: List[Event]) -> Account:
    account = Account(id=events[0].account_id)
    for event in events:
        account.apply(event)
    return account
```

**Battle Scar:** Без Event Sourcing аудит транзакций был невозможен — могли только сказать текущий баланс, но не историю изменений. С Event Sourcing — полная история, replay для отладки.

#### Saga Pattern (Distributed Transactions)

```python
# Orchestration-based saga
class OrderSaga:
    """Saga для создания заказа в распределённой системе."""
    
    async def execute(self, order_data: OrderData):
        try:
            # Шаг 1: Зарезервировать товар
            reservation = await inventory_service.reserve(order_data.items)
            
            # Шаг 2: Списать деньги
            payment = await payment_service.charge(
                order_data.user_id, order_data.total
            )
            
            # Шаг 3: Создать заказ
            order = await order_service.create(
                order_data, reservation.id, payment.id
            )
            
            # Шаг 4: Отправить уведомление
            await notification_service.send_confirmation(
                order_data.user_id, order.id
            )
            
            return order
            
        except InventoryError:
            # Rollback: ничего не делаем, товар не зарезервирован
            raise OrderFailed("Товар недоступен")
            
        except PaymentError:
            # Rollback: отменить резервацию
            await inventory_service.cancel_reservation(reservation.id)
            raise OrderFailed("Ошибка оплаты")
        
        except Exception:
            # Rollback: отменить всё
            await inventory_service.cancel_reservation(reservation.id)
            await payment_service.refund(payment.id)
            raise OrderFailed("Внутренняя ошибка")
```

---

## Часть 3: Работа с людьми и процессами

### 3.1 Code Review как Principal

**Что Principal проверяет в первую очередь:**

1. **Правильная ли задача решается?** (независимо от кода)
2. **Компромиссы осознаны?** (что не сделано и почему)
3. **Безопасность и мониторинг?** (как debug-ить в проде)
4. **Сопровождаемость?** (сможет ли junior понять через год)
5. **Тесты на правильном уровне?** (не unit вместо integration)

### 3.2 Mentoring: Как растить сеньоров

**Принцип «Уровень поддержки»:**

```
Junior:  "Сделай X, вот пример"
Middle:  "Нужно сделать Y, вот спецификация"
Senior:  "Вот проблема Z, предложи решение"
Staff:   "Вот область A, исследуй и предложи стратегию"
```

**Feedback Framework (SBI):**  
- **S**ituation: "На ревью PR #123..."  
- **B**ehavior: "...я заметил, что ты не добавил тесты на edge case"  
- **I**mpact: "...это может привести к багу при пустом запросе"

### 3.3 Technical Decision Records (TDR)

```markdown
# TDR-001: Выбор базы данных для системы заказов

## Статус
Принято (2024-03-15)

## Контекст
Нужна БД для системы заказов с требованиями:
- 100K orders/day
- ACID транзакции
- История изменений
- Геораспределённость

## Рассмотренные варианты
1. PostgreSQL + Logical Replication
2. CockroachDB
3. YugabyteDB

## Решение
PostgreSQL + Logical Replication

## Обоснование
- Команда уже знает PostgreSQL
- Logical Replication для geo-distribution
- Ниже TCO

## Последствия
+ Proven technology
- Ручное управление репликацией
- Нет auto-sharding

## Ссылки
- ADR-002: Репликация
```

---

## Часть 4: Production Excellence

### 4.1 Service Level Objectives (SLO)

**Как определить SLO для нового сервиса:**

```python
SLO_DEFINITION = {
    "service": "Order API",
    "tier": "T1 (critical)",
    "objectives": {
        "availability": {
            "target": "99.99%",
            "window": "30 дней",
            "measurement": "HTTP 200-499 / total * 100",
        },
        "latency_p99": {
            "target": "200ms",
            "window": "5 минут",
            "measurement": "p99 of request duration",
        },
        "error_rate": {
            "target": "< 0.1%",
            "window": "10 минут",
            "measurement": "HTTP 500 / total * 100",
        },
    },
    "error_budget": {
        "monthly": "4.38 минут downtime",
        "policy": "Если budget исчерпан — freeze фич",
    },
}
```

**Battle Scar:** SLO без error budget = бесполезная бумажка. Только когда мы начали фризить фичи при исчерпании бюджета, команды начали seriously относиться к надёжности.

### 4.2 Incident Response

**IR Playbook:**

```
1. DETECT (0-1 min)
   - Alert: pagerduty/prometheus
   - Severity: SEV1/S EV2/SEV3
   
2. TRIAGE (1-5 min)
   - Что сломалось?
   - Кого будить?
   - Есть ли workaround?

3. MITIGATE (5-30 min)
   - Rollback
   - Feature flag off
   - Traffic redirect
   - Scale up

4. RESOLVE (30 min - N hours)
   - Root cause
   - Fix
   - Deploy

5. FOLLOW-UP (24-48 hours)
   - Postmortem (blameless!)
   - Action items
   - Monitoring improvements
```

### 4.3 Blameless Postmortem

**Шаблон postmortem:**

```markdown
## Postmortem: [Название]

**Дата:** 2024-03-15
**Длительность:** 47 минут
**Влияние:** 0.5% запросов падало с 500
**Severity:** SEV2

### Хронология
14:23 — Alert: error rate > 1%
14:25 — Triage: DB connection pool exhausted
14:28 — Mitigation: увеличили pool с 20 до 100
14:35 — Confirmed: ошибки ушли
14:50 — Root cause: connection leak в миграции

### Root Cause
Новый код не закрывал соединения при ошибке

### Action Items
- [ ] Добавить pool_pre_ping=True DONE
- [ ] Мониторинг pool utilisation P0
- [ ] Code review check для connection leak P1

### Lessons
- Миграции должны проходить load test
- Pool utilisation метрика — обязательна
```

---

## Часть 5: Big Tech Engineering Culture

### 5.1 OKRs для инженеров

```
Objective:
  Повысить надёжность платёжной системы

Key Results:
  KR1: Увеличить uptime с 99.9% до 99.99%
  KR2: Снизить MTTR с 45 мин до 15 мин
  KR3: Достичь 0 SEV1 инцидентов за квартал
  KR4: Провести 3 game days (chaos engineering)
  
Initiatives:
  I1: Внедрить circuit breaker во все внешние вызовы
  I2: Автоматизировать rollback (1 click)
  I3: Добавить синтетический мониторинг
  I4: Провести postmortem по каждому SEV2+
```

### 5.2 Scaling Yourself

**Как Principal Engineer влияет на > 1 команду:**

1. **RFC (Request for Comments)** — документы на архитектуру, которые читает вся организация
2. **Office hours** — 2 часа в неделю, любой инженер может задать вопрос
3. **Internal talks** — делиться опытом, учить паттернам
4. **Code reviews** — ревью ключевых изменений во всех командах
5. **Mentoring** — растить Staff+ инженеров

**Time allocation (typical):**

```
Coding/Architecture:    30%
Code Review:            20%
Mentoring/1:1:          20%
Design Docs:            15%
Meetings/Strategy:      15%
```

### 5.3 Инструменты влияния (без authority)

```
Consequence         Strategy
──────────────────────────────────────────
"Это не моя зона"  → Show the problem, offer help
"Так не принято"   → Propose small experiment, measure
"Нет времени"      → Show cost of NOT doing it
"Рискованно"       → De-risk with gradual rollout
"Всегда так было"  → Challenge assumptions respectfully
"Менеджмент не даст" → Build data-driven case
```

---

## Часть 6: Техническая стратегия

### 6.1 Platform Thinking

**Platform vs Product mindset:**

```
Product Mindset                Platform Mindset
──────────────────────────────────────────────────
"Я напишу этот модуль"         "Я создам API для других модулей"
"Мне нужно X"                  "Нашей платформе нужно X"
"Оптимизирую свой сервис"      "Оптимизирую экосистему"
"Вот решение"                  "Вот framework решений"
```

**Platform Principles:**
1. **Platform сначала для себя** — если ты не используешь свою платформу, её не будут использовать другие
2. **Simplify, don't abstract** — абстракция скрывает сложность, упрощение убирает её
3. **Stable interfaces, evolving implementations** — API не меняется, implementation может
4. **Default-on** — если фита безопасна, включи её по умолчанию
5. **Observability is a feature** — без observability platform бесполезна

### 6.2 Build vs Buy vs Open Source

**Decision framework:**

```
Вопрос 1: Это core business?
  Да → Build
  Нет → Вопрос 2

Вопрос 2: Есть成熟 open source?
  Да → Вопрос 3
  Нет → Buy

Вопрос 3: Open source meets 80% requirements?
  Да → Use + contribute
  Нет → Buy or custom build
```

**Примеры:**
- Система рекомендаций → Build (core business)
- Logging → Open Source (ELK/Grafana Loki)
- Auth → Buy (Auth0)/Open Source (Keycloak)
- Payment processing → Buy (Stripe/Adyen)

### 6.3 Migration Strategy

**Strangler Fig Pattern — золотой стандарт миграций:**

```python
# 1. Создать новый сервис
# 2. Поставить маршрутизатор перед старым
# 3. Постепенно переключать трафик
# 4. Удалить старый сервис

class MigrationRouter:
    """Router for gradual migration."""
    
    def __init__(self, old_service, new_service, migration_pct=0):
        self.old = old_service
        self.new = new_service
        self.migration_pct = migration_pct
    
    async def route(self, request):
        if self._should_migrate(request):
            try:
                result = await self.new.handle(request)
                self._record_success("new")
                return result
            except Exception:
                # Fallback to old service
                self._record_failure("new")
                return await self.old.handle(request)
        else:
            return await self.old.handle(request)
    
    def _should_migrate(self, request):
        # Consistent routing based on user_id
        return hash(request.user_id) % 100 < self.migration_pct
    
    def increase_migration(self, pct):
        self.migration_pct = min(pct, 100)
```

**Battle Scar:** Одна миграция 200 сервисов с Monolith на Microservices (2 года):  
- M0-M3: Strangler Fig на read path  
- M3-M6: Write path migration  
- M6-M12: Feature parity  
- M12-M18: Decompose  
- M18-M24: Monolith decommission  
- Результат: 0 downtime, 0 data loss

---

## Часть 7: On-Call Excellence

### 7.1 Что должно быть в runbook

```markdown
# Runbook: Order Service

## Dashboards
- Grafana: Order Service Overview
- Datadog: order.service.*

## Alerts
- High Error Rate (>1% 5min) — P0
- High Latency (>500ms p99) — P1
- Low Pool Utilisation (k8s) — P2

## Common Issues

### Error "connection refused" to database
1. Check DB status: `kubectl exec -it postgres-0 -- pg_isready`
2. Check network policy
3. Restart if needed: `kubectl rollout restart deployment/postgres`

### Kafka consumer lag > 1000
1. Check consumer health
2. Check upstream dependencies
3. Increase partitions if needed
```

### 7.2 Chaos Engineering

**Principles:**
1. Start with production (not staging)
2. Automate everything
3. Blast radius control
4. Steady-state hypothesis

**Примеры Game Day:**

```
Game Day 1: Random pod kill (k8s chaos)
  - Hypothesis: Service survives pod failure with < 1% errors
  - Result: Всё ок

Game Day 2: Database failover
  - Hypothesis: Read replica promotion takes < 30s
  - Result: Потребовалось 2 минуты — улучшили настройки

Game Day 3: 5x traffic spike
  - Hypothesis: Autoscaling handles within 3 minutes
  - Result: Алерты не сработали — добавили early warning
```

---

## Часть 8: Principal Engineer Interview Prep

### 8.1 System Design: Common Questions

| Тема | Что проверяют |
|------|--------------|
| Design URL shortener | Hash function, storage, caching, redirect |
| Design chat system | WebSocket, presence, history, scaling |
| Design payment system | Idempotency, consistency, fraud detection |
| Design recommendation engine | Data pipeline, ML infra, feature store |
| Design rate limiter | Algorithm (token bucket), distributed, sliding window |
| Design distributed queue | Partitioning, ordering, exactly-once semantics |
| Design monitoring system | Metric collection, storage, alerting, dashboard |
| Design CDN | Caching strategies, edge computing, origin shield |

### 8.2 Behavioral Questions: STAR-R

```
S - Situation: Контекст (что, где, когда)
T - Task: Задача (что нужно было сделать)
A - Action: Действия (что конкретно делал)
R - Result: Результат (метрики, цифры)
R - Reflection: Чему научился, что бы сделал иначе

Пример:
S: В прошлой компании сервис заказов падал раз в неделю
T: Нужно было повысить uptime с 99.8% до 99.99%
A: Внедрил circuit breaker, retry with backoff, graceful degradation
R: Uptime вырос до 99.99%, инциденты сократились с 4/мес до 0
R: Понял, что надежность — это культура, а не инструменты. 
   Теперь начинаю с SLO и error budget, а не с инструментов.
```

### 8.3 Leadership Principles (FAANG-style)

| Принцип | Как демонстрировать |
|---------|-------------------|
| Customer Obsession | "Я начал с пользовательского сценария и работал назад" |
| Ownership | "Это не моя зона, но я взял инициативу" |
| Invent and Simplify | "Упростил систему с 5 шагов до 2, сохранив функциональность" |
| Deliver Results | "Увеличил throughput в 10 раз за счёт кэширования" |
| Are Right, A Lot | "Я ошибался в оценке, признал и перестроил план" |
| Learn and Be Curious | "Изучил новую технологию, чтобы решить проблему" |
| Think Big | "Спроектировал систему на 10x будущий рост" |
| Dive Deep | "Нашёл баг на уровне протокола TCP" |

---

## 🏆 Заключение

Principal Engineer — это не титул, а ответственность:

- **За качество** — код, который не стыдно показать
- **За людей** — которых растишь и которым создаёшь условия
- **За бизнес** — технические решения, которые приносят ценность
- **За будущее** — архитектуру, которая выдержит следующие 5 лет

```
Быть Principal — значит:
- Говорить "нет" чаще, чем "да"
- Знать, когда нарушить правило
- Строить систему, которая работает без тебя
- Думать в годах, но действовать сегодня
```

---

*С любовью — команда @intarktelegram*


---

## Part 9: Big Tech Interview Preparation

### 9.1 System Design Interview Questions

```python
"""Complete system design interview preparation."""

SYSTEM_DESIGN_QUESTIONS = {
    "design_url_shortener": {
        "difficulty": "Easy-Medium",
        "focus": ["Hashing", "Caching", "Redirects", "Analytics"],
        "key_tradeoffs": [
            "Key length vs collision probability",
            "In-memory cache vs distributed cache",
            "301 vs 302 redirects",
        ],
    },
    "design_chat_system": {
        "difficulty": "Medium",
        "focus": ["WebSockets", "Persistence", "Push notifications", "Multi-device"],
        "key_tradeoffs": [
            "Polling vs WebSocket vs SSE",
            "Message ordering guarantees",
            "Online/offline detection accuracy",
        ],
    },
    "design_payment_system": {
        "difficulty": "Hard",
        "focus": ["Idempotency", "Consistency", "Saga", "Reconciliation"],
        "key_tradeoffs": [
            "Strong vs eventual consistency",
            "Dual-write to multiple providers",
            "Batch vs real-time reconciliation",
        ],
    },
    "design_ride_sharing": {
        "difficulty": "Hard",
        "focus": ["Geospatial", "Real-time matching", "Pricing", "ETA"],
        "key_tradeoffs": [
            "QuadTree vs Geohash for location",
            "Push vs polling for driver location",
            "Dynamic vs static pricing",
        ],
    },
    "design_news_feed": {
        "difficulty": "Medium",
        "focus": ["Fan-out", "Ranking", "Caching", "Personalization"],
        "key_tradeoffs": [
            "Push (fan-out on write) vs Pull (fan-out on read)",
            "Global vs per-user ranking",
            "Real-time vs batch generation",
        ],
    },
}


# Template for system design:
"""
1. Requirements (5 mins)
   - Functional: What the system does
   - Non-functional: Scale, latency, availability, consistency
   - Out of scope: What we explicitly won't do

2. Estimation (5 mins)
   - DAU, QPS, storage, bandwidth
   - Justify numbers with simple calculations

3. Data Model (5 mins)
   - Schema, storage choice (SQL vs NoSQL)
   - Justify with access patterns

4. High-Level Design (10 mins)
   - Components and data flow
   - API design (REST or RPC)

5. Deep Dive (15 mins)
   - Pick 1-2 interesting components
   - Discuss trade-offs in detail
   - Justify each decision

6. Scaling & Bottlenecks (10 mins)
   - Where will it break?
   - How to scale each component?
   - Cost analysis
"""
```

### 9.2 Behavioral Questions

```python
"""STAR-R answers for behavioral questions."""
from __future__ import annotations


BEHAVIORAL_EXAMPLES = {
    "conflict_resolution": {
        "question": "Tell me about a time you disagreed with a technical decision",
        "star": """
            S: Team wanted to rewrite the entire monolith in Go
            T: I believed incremental migration was safer
            A: Proposed strangler fig pattern, built prototype showing 3-month timeline
            R: Team agreed, migration took 4 months with zero downtime
            R: Learned to always bring data, not opinions
        """,
    },
    "technical_leadership": {
        "question": "Describe a time you influenced others without authority",
        "star": """
            S: 5 teams using different CI/CD tools
            T: Standardize on GitHub Actions for consistency
            A: Built reference implementation, documented benefits, offered migration support
            R: 4/5 teams migrated in 2 months, reducing deploy time by 60%
            R: Building relationships and showing value is more effective than mandates
        """,
    },
    "failure": {
        "question": "Tell me about a time something went wrong",
        "star": """
            S: Deployed database migration without proper testing
            T: Migration caused 15-minute outage
            A: Rolled back immediately, fixed migration, added automated testing
            R: No similar incidents in 2 years, improved deploy process
            R: Always have a rollback plan before any deploy
        """,
    },
    "biggest_achievement": {
        "question": "What's your biggest technical achievement?",
        "star": """
            S: Legacy system processing 50K orders/day, frequent outages
            T: Redesign for 500K orders/day with 99.99% uptime
            A: Event-driven architecture, Kafka, CQRS, circuit breakers
            R: 10x throughput, 99.99% uptime, $2M annual cost savings
            R: Architecture is about trade-offs, not perfection
        """,
    },
}
```

## Part 10: Engineering Strategy Documents

### Technical Strategy Template

```markdown
# Technical Strategy: [Title]

## Current State
[Where we are now]

## Desired State  
[Where we want to be in 12 months]

## Gaps
[What's blocking us from getting there]

## Strategic Pillars
1. [Pillar 1: e.g., "Improve Reliability"]
   - Initiative 1.1
   - Initiative 1.2
   - Key Result: [Measurable outcome]

2. [Pillar 2: e.g., "Accelerate Development"]
   - Initiative 2.1
   - Initiative 2.2
   - Key Result: [Measurable outcome]

## Risks & Mitigations
- Risk 1 → Mitigation 1
- Risk 2 → Mitigation 2

## Resource Requirements
- Headcount: [Number]
- Infrastructure: [Budget]
- Timeline: [Quarters]

## Success Metrics
- Metric 1: [Target]
- Metric 2: [Target]
```

### RFC (Request for Comments) Template

```markdown
# RFC: [Title]

## Status
[Proposed | Accepted | Rejected | Superseded]

## Summary
[One paragraph summary]

## Motivation
[Why this change is needed]

## Design
[Technical design proposal]

## Alternatives Considered
[Other options and why they weren't chosen]

## Trade-offs
[What we gain, what we lose]

## Migration Plan
[How to get from current to desired state]

## Rollback Plan
[How to undo if things go wrong]

## Open Questions
[What's still undecided]

## References
[Links to relevant docs, PRDs, ADRs]
```
