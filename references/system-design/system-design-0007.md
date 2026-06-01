# Design: Netflix

## Metadata
- **ID**: MC-SYS-0007
- **Версия**: 1.0
- **Создан**: 2026-05-31
- **Уровень**: Principal Engineer

- **Category**: System Design
- **Scale**: Mid-size
- **Users**: 10M

---

## Требования

В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий. Principal Engineer обязан не просто знать API, а разбираться в механизмах, обеспечивающих работу системы. Это позволяет принимать взвешенные архитектурные решения, предсказывать поведение системы под нагрузкой и эффективно дебажить production-инциденты.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

Надёжность системы определяется не средним временем безотказной работы, а средним временем восстановления. Инвестиции в observability, автоматизацию runbook'ов и chaos engineering окупаются быстрее, чем попытки построить идеально отказоустойчивую систему с первого раза.

Code review — не бюрократическая процедура, а инструмент передачи знаний и повышения качества. Каждый review должен фокусироваться на архитектуре, безопасности, обработке ошибок и тестируемости. Стилистические замечания лучше автоматизировать через линтеры и форматтеры.

### Functional

1. При проектировании распределённых систем ключевым навыком является умение работать с компромиссами. Каждое решение имеет
2. В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий
3. Эффективная отладка production-инцидентов требует системного подхода. Необходимо иметь ментальную модель всей системы: о
4. Управление техническим долгом — одна из ключевых компетенций Principal Engineer. Долг неизбежен, но им можно и нужно упр

### Non-functional

1. Availability: 99.99%
2. Latency p99 < 500ms
3. Consistency: Causal
4. Durability: 99.9999%

## High-level Design

Data-intensive приложения требуют особого подхода к проектированию. Паттерны обработки данных, модели согласованности и стратегии партиционирования — фундамент, на котором строится вся система. Ошибки на этом уровне стоят дороже всего.

Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

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

Code review — не бюрократическая процедура, а инструмент передачи знаний и повышения качества. Каждый review должен фокусироваться на архитектуре, безопасности, обработке ошибок и тестируемости. Стилистические замечания лучше автоматизировать через линтеры и форматтеры.

Производительность начинается с измеримости. Невозможно оптимизировать то, что не измеряется. Каждый сервис должен иметь SLO и дашборд, отображающий ключевые метрики. Без этого разговоры о производительности остаются гаданием на кофейной гуще.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

Observability — это не про инструменты, а про культуру. Хорошая observability позволяет ответить на любой вопрос о системе без необходимости деплоить новый код. Это требует инвестиций в структурированные логи, распределённую трассировку и бизнес-метрики.

Управление техническим долгом — одна из ключевых компетенций Principal Engineer. Долг неизбежен, но им можно и нужно управлять. Важно иметь видимость долга, оценивать его стоимость и сознательно принимать решения о его погашении или отсрочке.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

Надёжность системы определяется не средним временем безотказной работы, а средним временем восстановления. Инвестиции в observability, автоматизацию runbook'ов и chaos engineering окупаются быстрее, чем попытки построить идеально отказоустойчивую систему с первого раза.

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

Event-driven архитектура мощна, но сложна. Идемпотентность обработчиков, exactly-once семантика, ordering гарантии — ключевые вызовы. Saga паттерн для транзакций через несколько сервисов требует тщательного проектирования компенсирующих действий.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

Безопасность должна быть заложена в архитектуру на этапе проектирования, а не добавлена потом. Security review — обязательная часть архитектурного процесса. Принцип наименьших привилегий, defense in depth и zero-trust должны быть стандартом, а не исключением.

Database schema design — это искусство предсказывать будущие запросы. Нормализация для consistency, денормализация для производительности, partitioning для масштабирования. Хорошая схема живёт годами, плохая — переписывается каждый месяц.

Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, minimal base images — минимальные требования для production. Каждая зависимость — это потенциальный вектор атаки.

Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, minimal base images — минимальные требования для production. Каждая зависимость — это потенциальный вектор атаки.

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

Микросервисы — это не цель, а средство. Переход к микросервисам должен быть обоснован бизнес-потребностями, а не модой. Для многих проектов хорошо написанный монолит с чёткими модульными границами — лучшее решение.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

Управление техническим долгом — одна из ключевых компетенций Principal Engineer. Долг неизбежен, но им можно и нужно управлять. Важно иметь видимость долга, оценивать его стоимость и сознательно принимать решения о его погашении или отсрочке.

Масштабирование систем — это всегда серия компромиссов. Горизонтальное масштабирование даёт эластичность, но добавляет сложность согласования состояния. Вертикальное масштабирование проще, но имеет физические пределы. Выбор стратегии зависит от профиля нагрузки, требований к консистентности и бюджета.

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

### Partitioning
Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

### Replication
Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, minimal base images — минимальные требования для production. Каждая зависимость — это потенциальный вектор атаки.

### Consistency
В контексте современных высоконагруженных систем критически важно понимать внутреннее устройство используемых технологий. Principal Engineer обязан не просто знать API, а разбираться в механизмах, обеспечивающих работу системы. Это позволяет принимать взвешенные архитектурные решения, предсказывать поведение системы под нагрузкой и эффективно дебажить production-инциденты.

Эффективная отладка production-инцидентов требует системного подхода. Необходимо иметь ментальную модель всей системы: от запроса пользователя до записи в базу данных. Каждый сбой — это возможность улучшить мониторинг, алертинг и документацию runbook'ов.

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

Архитектурная эволюция — естественный процесс. Не существует идеальной архитектуры, есть архитектура, подходящая для текущего контекста. Задача инженера — проектировать с запасом, но без избыточности, и вовремя распознавать момент, когда архитектуру нужно менять.

Опыт показывает, что большинство проблем в production возникают не из-за отсутствия знаний, а из-за недостаточного понимания границ применимости технологий. Principal Engineer должен чётко осознавать, где заканчивается зона ответственности инструмента и начинается необходимость кастомного решения или обходного манёвра.

Code review — не бюрократическая процедура, а инструмент передачи знаний и повышения качества. Каждый review должен фокусироваться на архитектуре, безопасности, обработке ошибок и тестируемости. Стилистические замечания лучше автоматизировать через линтеры и форматтеры.

Безопасность supply chain — растущая угроза. Software Bill of Materials, signature verification, dependency scanning, minimal base images — минимальные требования для production. Каждая зависимость — это потенциальный вектор атаки.

Caching — это всегда баланс между свежестью данных и производительностью. Инвалидация кеша — одна из сложнейших проблем в computer science. Подход cache-aside, write-through, write-behind — каждый имеет свою нишу применения.

Code review — не бюрократическая процедура, а инструмент передачи знаний и повышения качества. Каждый review должен фокусироваться на архитектуре, безопасности, обработке ошибок и тестируемости. Стилистические замечания лучше автоматизировать через линтеры и форматтеры.

Event-driven архитектура мощна, но сложна. Идемпотентность обработчиков, exactly-once семантика, ordering гарантии — ключевые вызовы. Saga паттерн для транзакций через несколько сервисов требует тщательного проектирования компенсирующих действий.

Resilience-паттерны должны быть встроены в архитектуру изначально. Circuit breaker, bulkhead, retry с exponential backoff, timeout — минимальный джентльменский набор. Chaos engineering помогает проверить, что эти паттерны действительно работают.

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
