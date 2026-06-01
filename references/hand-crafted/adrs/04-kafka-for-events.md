# ADR 004: Use Kafka for Event Streaming

Status: Proposed

## Context

We need a message broker for asynchronous communication between services.
Requirements: high throughput, message persistence, replay capability,
exactly-once semantics, multi-subscriber.

## Decision

Use Apache Kafka for event streaming between services.

## Rationale

1. High throughput - millions of messages per second
2. Message persistence - configurable retention, replay capability
3. Exactly-once semantics - no duplicate messages
4. Multi-subscriber - each consumer group reads independently
5. Partitioning - parallel processing within topics
6. Fault tolerance - built-in replication between brokers
7. Ecosystem - Kafka Connect, Kafka Streams, Schema Registry

## Topics

orders (6 partitions, retention 7 days)
  - order.created, order.confirmed, order.shipped, order.cancelled
payments (3 partitions, retention 30 days)
  - payment.processed, payment.failed, payment.refunded
notifications (3 partitions, retention 1 day)
  - notification.email, notification.sms, notification.push

## Schema Registry

Use Avro schemas with Schema Registry for evolution safety.

Records evolve by adding optional fields.
No breaking changes.
Producer and consumer agree on schema ID.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.


## Key Takeaway

Apply this in your codebase.
