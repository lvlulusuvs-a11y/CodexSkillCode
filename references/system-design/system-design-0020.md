# Design: Video streaming

## Metadata
- **ID**: MC-SYS-0020
- **Версия**: 1.0
- **Создан**: 2026-05-31
- **Уровень**: Principal Engineer

- **Category**: System Design
- **Scale**: Hyperscale
- **Users**: 100M+

---

## Требования

Event-driven архитектура мощна, но сложна. Идемпотентность обработчиков, exactly-once семантика, ordering гарантии — ключевые вызовы. Saga паттерн для транзакций через несколько сервисов требует тщательного проектирования компенсирующих действий.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

При проектировании распределённых систем ключевым навыком является умение работать с компромиссами. Каждое решение имеет свою цену: сложность, latency, стоимость инфраструктуры, время поддержки. Задача инженера — найти оптимальный баланс для конкретного бизнес-контекста, а не слепо следовать best practices.

### Functional

1. Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для тек
2. Масштабирование систем — это всегда серия компромиссов. Горизонтальное масштабирование даёт эластичность, но добавляет с
3. Data-intensive приложения требуют особого подхода к проектированию. Паттерны обработки данных, модели согласованности и 
4. Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, mi

### Non-functional

1. Availability: 99.9%
2. Latency p99 < 500ms
3. Consistency: Eventual
4. Durability: 99.9999%

## High-level Design

Data-intensive приложения требуют особого подхода к проектированию. Паттерны обработки данных, модели согласованности и стратегии партиционирования — фундамент, на котором строится вся система. Ошибки на этом уровне стоят дороже всего.

API design — это контракт на годы. Хороший API интуитивно понятен, консистентен и трудно используется неправильно. Версионирование, error handling, pagination, rate limiting — must have для любого публичного API.

Observability — это не про инструменты, а про культуру. Хорошая observability позволяет ответить на любой вопрос о системе без необходимости деплоить новый код. Это требует инвестиций в структурированные логи, распределённую трассировку и бизнес-метрики.

Масштабирование систем — это всегда серия компромиссов. Горизонтальное масштабирование даёт эластичность, но добавляет сложность согласования состояния. Вертикальное масштабирование проще, но имеет физические пределы. Выбор стратегии зависит от профиля нагрузки, требований к консистентности и бюджета.

Масштабирование систем — это всегда серия компромиссов. Горизонтальное масштабирование даёт эластичность, но добавляет сложность согласования состояния. Вертикальное масштабирование проще, но имеет физические пределы. Выбор стратегии зависит от профиля нагрузки, требований к консистентности и бюджета.

| Компонент | Назначение | Масштабирование | Критичность |
|-----------|------------|-----------------|-------------|
| Load Balancer | Распределение трафика | Active/Passive | High |
| API Gateway | Маршрутизация, аутентификация | Горизонтальное | High |
| Service Mesh | Связь между сервисами | Sidecar per pod | Medium |
| Message Queue | Асинхронная коммуникация | Cluster partitioning | High |
| Cache Layer | Ускорение чтения | Redis Cluster | Medium |
| Database | Хранение состояния | Master/Replica | Critical |
| CDN | Доставка контента | Edge nodes | Low |
| Monitoring | Observability | Aggregator | Medium |

## Data Model

В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий. Principal Engineer обязан не просто знать API, а разбираться в механизмах, обеспечивающих работу системы. Это позволяет принимать взвешенные архитектурные решения, предсказывать поведение системы под нагрузкой и эффективно дебажить production-инциденты.

В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий. Principal Engineer обязан не просто знать API, а разбираться в механизмах, обеспечивающих работу системы. Это позволяет принимать взвешенные архитектурные решения, предсказывать поведение системы под нагрузкой и эффективно дебажить production-инциденты.

Производительность начинается с измеримости. Невозможно оптимизировать то, что не измеряется. Каждый сервис должен иметь SLO и дашборд, отображающий ключевые метрики. Без этого разговоры о производительности остаются гаданием на кофейной гуще.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

```python
import asyncio
import random
import time
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    """Result type with error handling."""
    value: Optional[T] = None
    error: Optional[Exception] = None
    latency_ms: float = 0.0

    @property
    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error:
            raise self.error
        assert self.value is not None
        return self.value

class CircuitBreaker:
    def __init__(self, threshold: int = 5, timeout: float = 30.0):
        self.threshold = threshold
        self.timeout = timeout
        self._failures = 0
        self._state = "closed"
        self._last_failure = 0.0

    async def call(self, func, *args, **kwargs):
        if self._state == "open":
            if time.monotonic() - self._last_failure > self.timeout:
                self._state = "half-open"
            else:
                raise Exception("Circuit breaker open")
        try:
            result = await func(*args, **kwargs)
            if self._state == "half-open":
                self._state = "closed"
                self._failures = 0
            return result
        except Exception as exc:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.threshold:
                self._state = "open"
            raise exc

async def with_retry(func, max_retries=3, backoff=1.0, max_backoff=60.0):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as exc:
            if attempt == max_retries:
                raise
            delay = min(backoff * (2 ** attempt), max_backoff)
            delay += random.uniform(0, delay * 0.1)
            print(f"Retry {attempt + 1}/{max_retries} after {delay:.2f}s: {exc}")
            await asyncio.sleep(delay)
```

## API Design

Производительность начинается с измеримости. Невозможно оптимизировать то, что не измеряется. Каждый сервис должен иметь SLO и дашборд, отображающий ключевые метрики. Без этого разговоры о производительности остаются гаданием на кофейной гуще.

Data-intensive приложения требуют особого подхода к проектированию. Паттерны обработки данных, модели согласованности и стратегии партиционирования — фундамент, на котором строится вся система. Ошибки на этом уровне стоят дороже всего.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

Надёжность системы определяется не средним временем безотказной работы, а средним временем восстановления. Инвестиции в observability, автоматизацию runbook'ов и chaos engineering окупаются быстрее, чем попытки построить идеально отказоустойчивую систему с первого раза.

Микросервисы — это не цель, а средство. Переход к микросервисам должен быть обоснован бизнес-потребностями, а не модой. Для многих проектов хорошо написанный монолит с чёткими модульными границами — лучшее решение.

Эффективная отладка production-инцидентов требует системного подхода. Необходимо иметь ментальную модель всей системы: от запроса пользователя до записи в базу данных. Каждый сбой — это возможность улучшить мониторинг, алертинг и документацию runbook'ов.

```typescript
interface RetryConfig {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  jitter: boolean;
}

class CircuitBreaker {
  private failures = 0;
  private state: "closed" | "open" | "half-open" = "closed";
  private lastFailure = 0;

  constructor(
    private threshold = 5,
    private timeoutMs = 30000
  ) {}

  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === "open") {
      if (Date.now() - this.lastFailure > this.timeoutMs) {
        this.state = "half-open";
      } else {
        throw new Error("Circuit breaker open");
      }
    }
    try {
      const result = await fn();
      if (this.state === "half-open") {
        this.state = "closed";
        this.failures = 0;
      }
      return result;
    } catch (err) {
      this.failures++;
      this.lastFailure = Date.now();
      if (this.failures >= this.threshold) {
        this.state = "open";
      }
      throw err;
    }
  }
}

async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt === config.maxRetries) throw err;
      const delay = Math.min(
        config.baseDelayMs * 2 ** attempt,
        config.maxDelayMs
      );
      const jitter = config.jitter ? delay * 0.1 * (Math.random() * 2 - 1) : 0;
      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
    }
  }
  throw new Error("Unreachable");
}
```

## Deep Dive

Event-driven архитектура мощна, но сложна. Идемпотентность обработчиков, exactly-once семантика, ordering гарантии — ключевые вызовы. Saga паттерн для транзакций через несколько сервисов требует тщательного проектирования компенсирующих действий.

Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

Эффективная отладка production-инцидентов требует системного подхода. Необходимо иметь ментальную модель всей системы: от запроса пользователя до записи в базу данных. Каждый сбой — это возможность улучшить мониторинг, алертинг и документацию runbook'ов.

Event-driven архитектура мощна, но сложна. Идемпотентность обработчиков, exactly-once семантика, ordering гарантии — ключевые вызовы. Saga паттерн для транзакций через несколько сервисов требует тщательного проектирования компенсирующих действий.

### Partitioning
Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, minimal base images — минимальные требования для production. Каждая зависимость — это потенциальный вектор атаки.

Производительность начинается с измеримости. Невозможно оптимизировать то, что не измеряется. Каждый сервис должен иметь SLO и дашборд, отображающий ключевые метрики. Без этого разговоры о производительности остаются гаданием на кофейной гуще.

### Replication
Управление техническим долгом — одна из ключевых компетенций Principal Engineer. Долг неизбежен, но им можно и нужно управлять. Важно иметь видимость долга, оценивать его стоимость и сознательно принимать решения о его погашении или отсрочке.

Observability — это не про инструменты, а про культуру. Хорошая observability позволяет ответить на любой вопрос о системе без необходимости деплоить новый код. Это требует инвестиций в структурированные логи, распределённую трассировку и бизнес-метрики.

### Consistency
Управление техническим долгом — одна из ключевых компетенций Principal Engineer. Долг неизбежен, но им можно и нужно управлять. Важно иметь видимость долга, оценивать его стоимость и сознательно принимать решения о его погашении или отсрочке.

Масштабирование систем — это всегда серия компромиссов. Горизонтальное масштабирование даёт эластичность, но добавляет сложность согласования состояния. Вертикальное масштабирование проще, но имеет физические пределы. Выбор стратегии зависит от профиля нагрузки, требований к консистентности и бюджета.

В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий. Principal Engineer обязан не просто знать API, а разбираться в механизмах, обеспечивающих работу системы. Это позволяет принимать взвешенные архитектурные решения, предсказывать поведение системы под нагрузкой и эффективно дебажить production-инциденты.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

## Trade-offs

| Критерий | Вариант A | Вариант B | Вариант C |
|----------|-----------|-----------|-----------|
| Производительность | Высокая | Средняя | Низкая |
| Надёжность | 99.99% | 99.95% | 99.9% |
| Сложность | Низкая | Средняя | Высокая |
| Стоимость | $ | $$$ | $$ |
| Масштабируемость | Горизонтальная | Вертикальная | Гибридная |
| Time to Market | 2 недели | 1 месяц | 3 месяца |
| Поддержка | Встроенная | Community | Enterprise |

## Monitoring

Микросервисы — это не цель, а средство. Переход к микросервисам должен быть обоснован бизнес-потребностями, а не модой. Для многих проектов хорошо написанный монолит с чёткими модульными границами — лучшее решение.

Эффективная отладка production-инцидентов требует системного подхода. Необходимо иметь ментальную модель всей системы: от запроса пользователя до записи в базу данных. Каждый сбой — это возможность улучшить мониторинг, алертинг и документацию runbook'ов.

Data-intensive приложения требуют особого подхода к проектированию. Паттерны обработки данных, модели согласованности и стратегии партиционирования — фундамент, на котором строится вся система. Ошибки на этом уровне стоят дороже всего.

Производительность начинается с измеримости. Невозможно оптимизировать то, что не измеряется. Каждый сервис должен иметь SLO и дашборд, отображающий ключевые метрики. Без этого разговоры о производительности остаются гаданием на кофейной гуще.

```yaml
version: "3.8"
services:
  app:
    image: mega-service:latest
    environment:
      LOG_LEVEL: "INFO"
      METRICS_ENABLED: "true"
      TRACING_ENABLED: "true"
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2"
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    depends_on:
      - postgres
      - redis
      - kafka

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mega
      POSTGRES_USER: mega
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 8G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G

  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
    deploy:
      replicas: 3

volumes:
  pgdata:
  redisdata:
```
