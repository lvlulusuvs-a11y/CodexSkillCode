# Kafka Patterns for Principal Engineers

**Apache Kafka в продакшене: не just another message queue.**

---

## 1. Kafka vs Message Queues

| Характеристика | Kafka | RabbitMQ / SQS |
|---------------|-------|----------------|
| Модель | Log-based | Queue-based |
| Retention | Хранит сообщения (срок/размер) | Удаляет после ack |
| Consumer | Pull-based | Push-based (или pull) |
| Replay | Да — offset reset | Нет |
| Ordering | Per-partition | Limited |
| Throughput | Миллионы/сек | Тысячи/сек |
| Durability | Sync replication | Depends |

**Когда Kafka:** event sourcing, stream processing, data pipeline, audit log, metrics.  
**Когда Queue:** task distribution, RPC, workload balancing.

---

## 2. Partitioning Strategy

### Key-Based Partitioning

```python
# ❌ Проблема: partition по user_id — если один user делает много операций,
#    один partition перегружен

# ✅ Хорошо: composite key
def partition_key(user_id: int, entity_type: str) -> str:
    """Распределяет нагрузку равномерно."""
    return f"{user_id % 100}:{entity_type}"

# ✅ Лучше: semantic partitioning
# Partition 0-31: заказы
# Partition 32-63: платежи
# Partition 64-95: уведомления
# Partition 96-99: всё остальное
```

**Battle Scar:** Один клиент генерировал 90% событий — partition перегружен, latency для всех остальных выросла в 10 раз. Semantic partitioning решило проблему.

### Partition Count & Replication

```python
# Правило: partitions = max(throughput_needed / 10MBps, consumers * 2)
# Replication: 3 для production (min.insync.replicas=2)

# Конфигурация для продакшена:
PARTITION_CONFIG = {
    "num.partitions": 24,        # достаточно для большинства сценариев
    "replication.factor": 3,     # отказоустойчивость
    "min.insync.replicas": 2,    # гарантия записи
    "retention.ms": 604800000,   # 7 дней
    "cleanup.policy": "delete",  # или "compact" для ключевых данных
    "compression.type": "lz4",   # snappy/zstd для текста, lz4 для бинарных
}
```

---

## 3. Producer Patterns

### Idempotent Producer

```python
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(
    bootstrap_servers="localhost:9092",
    enable_idempotence=True,       # exactly-once гарантии
    acks="all",                     # ждать все реплики
    max_in_flight_requests_per_connection=5,
    compression_type="lz4",
)

# Retry with exponential backoff
async def produce_with_retry(producer, topic, key, value, max_retries=3):
    for attempt in range(max_retries):
        try:
            await producer.send_and_wait(topic, key=key, value=value)
            return
        except KafkaError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### Transactional Producer (Exactly-Once)

```python
# Для атомарной записи в несколько партиций
async with producer.transaction():
    await producer.send("orders", value=order_data)
    await producer.send("payments", value=payment_data)
    # Либо обе записи будут, либо ни одной
```

**Battle Scar:** Без идемпотентности при сетевых ошибках producer отправлял дубликаты. Дубликаты заказов = возврат денег клиентам. Idempotent producer решил проблему за счёт `producer.id` + sequence number.

---

## 4. Consumer Patterns

### Commit Strategies

```python
# ❌ auto.commit=true — потеря сообщений при краше
# ✅ Ручной commit после обработки

async def process_messages():
    consumer = AIOKafkaConsumer(
        "orders",
        bootstrap_servers="localhost:9092",
        group_id="order-processor",
        enable_auto_commit=False,        # ручной commit
        auto_offset_reset="earliest",
    )
    
    async for msg in consumer:
        try:
            async with db.transaction():
                await process_order(msg.value)
                await consumer.commit()   # commit после успеха
        except Exception as e:
            logger.error(f"Failed to process: {e}", exc_info=True)
            # Не коммитим — сообщение придёт снова
            await send_to_dlq(msg)        # DLQ для анализа
```

### Dead Letter Queue (DLQ)

```python
class DLQHandler:
    """Обработка сообщений, которые не удалось обработать."""
    
    DLQ_TOPIC = "orders-dlq"
    MAX_RETRIES = 3
    
    async def process_with_retry(self, msg):
        for attempt in range(self.MAX_RETRIES):
            try:
                return await self._process(msg)
            except RetryableError:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
            except NonRetryableError:
                break
        
        # В DLQ
        await self.producer.send(
            self.DLQ_TOPIC,
            key=msg.key,
            value=msg.value,
            headers=[("original_topic", "orders".encode()),
                     ("error", str(e).encode())]
        )
```

### Consumer Group Rebalancing

```python
# Cooperative rebalancing — меньше downtime
consumer = AIOKafkaConsumer(
    "orders",
    group_id="order-processor",
    partition_assignment_strategy=[
        CooperativeStickyAssignor  # вместо RangeAssignor
    ],
)
```

**Battle Scar:** RangeAssignor — при rebalance все consumer'ы останавливаются на 30-60 секунд. CooperativeStickyAssignor — 1-2 секунды.

---

## 5. Schema Management (Avro / Protobuf)

### Schema Registry

```python
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

# Schema в Schema Registry — forward/backward совместимость
ORDER_VALUE_SCHEMA = """
{
  "type": "record",
  "name": "OrderValue",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "user_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"}
  ]
}
"""

producer = AvroProducer(
    {"bootstrap.servers": "localhost:9092",
     "schema.registry.url": "http://schema-registry:8081"},
    default_value_schema=avro.loads(ORDER_VALUE_SCHEMA)
)
```

**Почему не JSON:**  
- Avro/Protobuf в 5-10x меньше JSON  
- Schema Registry гарантирует совместимость  
- Forward/backward compatibility проверяется на запись  

**Battle Scar:** Без Schema Registry producer начал писать новое поле, consumer упал с deserialization error. Прод встал на 2 часа.

---

## 6. Monitoring & Observability

### Key Metrics

| Метрика | Что показывает | Alert |
|---------|---------------|-------|
| `consumer_lag` | Отставание consumer'ов | > 1000 сообщений |
| `request_latency_ms` | Задержка брокера | > 100ms |
| `under_replicated_partitions` | Проблемы репликации | > 0 |
| `offline_partitions_count` | Partitions без лидера | > 0 |
| `bytes_in_per_sec` | Входящий трафик | Baseline + 50% |

### Lag Alerting Script

```python
#!/usr/bin/env python3
"""Мониторинг consumer lag."""
import subprocess
import json

def check_lag(group_id: str, threshold: int = 1000):
    result = subprocess.run(
        ["kafka-consumer-groups", "--bootstrap-server", "localhost:9092",
         "--group", group_id, "--describe"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            lag = int(parts[4])
            if lag > threshold:
                print(f"ALERT: {group_id} lag {lag} > {threshold}")
                return 1
    return 0
```

---

## 7. Performance Tuning

| Параметр | Значение | Эффект |
|----------|----------|--------|
| `batch.size` | 16KB - 64KB | Больше = выше throughput |
| `linger.ms` | 5-20ms | Компромисс latency/throughput |
| `compression.type` | zstd (text) / lz4 (binary) | -40-60% bandwidth |
| `buffer.memory` | 64MB - 128MB | Защита от backpressure |
| `max.request.size` | 1MB (default) | Для больших сообщений — увеличить |
| `fetch.min.bytes` | 1KB | Меньше poll'ов |
| `fetch.max.wait.ms` | 500ms | Лаг consumer'а |

**Battle Scar:** Без `linger.ms` = 0ms — producer отправлял каждое сообщение отдельно. 1000 msg/s = 1000 requests/s. После настройки `linger.ms=10ms` — requests уменьшились до 10/s, throughput вырос в 100x.

---

## 8. Exactly-Once Semantics (EOS)

```python
# Настройки для exactly-once:
# Producer: enable_idempotence=true
# Consumer: isolation.level=read_committed
# Транзакционный consumer

consumer = AIOKafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    group_id="order-processor",
    enable_auto_commit=False,
    isolation_level="read_committed",  # не читает незакоммиченное
)
```

**Когда реально нужно EOS:**  
- Финансовые транзакции  
- Инвентаризация (двойной спуск = loss)  
- Агрегация метрик (двойной подсчёт)

**Когда не нужно:** логи, аналитика, notifications — at-least-once достаточно.

---

## 🧠 Principal Engineer Wisdom for Kafka

| Принцип | Почему |
|---------|--------|
| Партиций = max(consumer_count * 2, N) | Перепартиционировать сложно |
| `min.insync.replicas=2` | Гарантия записи без потери доступности |
| Мониторинг consumer lag — первое дело | Лаг = проблемы |
| Schema Registry обязателен | Без него — deserialization в проде |
| Не используй Kafka как очередь задач | Для задач — RabbitMQ/SQS |
| Retention ≠ бесконечность | 7 дней — обычно достаточно |
| Rebalance — главная боль | CooperativeStickyAssignor спасает |

---

## 🔥 Kafka в Big Tech: что реально работает

**История:** Event-driven архитектура для платёжной системы.

| До (RabbitMQ) | После (Kafka) |
|---------------|---------------|
| 10K msg/s max | 1M+ msg/s |
| Retry: manual | Automatic + DLQ |
| Ordering: not guaranteed | Per-partition ordering |
| Audit trail: нет | Built-in (retention) |
| Replay: нет | Consumer reset |
| Downtime: 99.9% | 99.99% |
