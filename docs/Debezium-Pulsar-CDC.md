# Debezium & Apache Pulsar for Change Data Capture (CDC)

## Overview
This document explains the architecture, purpose, and operation of integrating Debezium with Apache Pulsar for Change Data Capture (CDC) from PostgreSQL. It covers how each component works, why they are used, and the benefits of this approach.

---

## What is Change Data Capture (CDC)?
CDC is a technique for identifying and capturing changes made to data in a database. These changes (inserts, updates, deletes) are then published to downstream systems for processing, analytics, or replication.

**Why use CDC?**
- Real-time data synchronization
- Event-driven architectures
- Data lake ingestion
- Auditing and compliance

---

## What is Debezium?
Debezium is an open-source distributed platform for CDC. It monitors databases and streams all change events (row-level changes) in a consistent, reliable manner.

### How Debezium Works
- **Connector**: Debezium uses connectors for various databases (PostgreSQL, MySQL, MongoDB, etc.).
- **Logical Replication**: For PostgreSQL, Debezium uses logical replication slots to read WAL (Write-Ahead Log) changes.
- **Event Generation**: Changes to tables are converted into structured CDC events (JSON format).
- **Publishing**: These events are published to a message broker (here, Apache Pulsar).

### Why Use Debezium?
- Non-intrusive: No application code changes required
- Reliable: Handles schema changes, restarts, and failures
- Rich ecosystem: Supports many databases and sinks

---

## What is Apache Pulsar?
Apache Pulsar is a cloud-native, distributed messaging and streaming platform.

### How Pulsar Works
- **Topics**: Pulsar organizes messages into topics, which producers write to and consumers read from.
- **Producers/Consumers**: Multiple producers can write to a topic; multiple consumers can subscribe with different subscription modes (exclusive, shared, failover, etc.).
- **Persistence**: Pulsar stores messages durably for configurable retention periods.
- **Scalability**: Supports multi-tenancy, geo-replication, and horizontal scaling.

### Why Use Pulsar?
- High throughput and low latency
- Built-in message retention and replay
- Flexible subscription models
- Seamless integration with CDC and event-driven architectures

---

## Debezium + Pulsar CDC Architecture

```
PostgreSQL  <--WAL--  Debezium Connector  -->  Pulsar Topic  -->  Consumer (Python, Java, etc.)
```

1. **PostgreSQL**: The source database where changes occur.
2. **Debezium Connector**: Captures changes using logical replication, converts them to CDC events.
3. **Pulsar Source Connector**: Debezium acts as a Pulsar source, publishing CDC events to a Pulsar topic (e.g., `persistent://public/default/rds-pg.public.users`).
4. **Consumer**: Applications (like your Python script) subscribe to the Pulsar topic to process CDC events in real time.

---

## Why This Approach?
- **Loose coupling**: Producers and consumers are decoupled via Pulsar topics
- **Scalability**: Multiple consumers can process the same stream independently
- **Reliability**: Pulsar ensures durable storage and delivery guarantees
- **Flexibility**: CDC events can be routed to multiple downstream systems

---

## Example: Event Flow
1. A row is inserted/updated/deleted in PostgreSQL.
2. Debezium reads the change from WAL and creates a CDC event.
3. The event is published to a Pulsar topic.
4. Any consumer subscribed to the topic receives the event and can process it (e.g., update a cache, trigger a workflow, replicate data, etc.).

---

## When NOT to Use This Pattern
- For simple, low-volume, or rarely-changing databases
- If you do not need real-time change propagation
- If your consumers cannot tolerate eventual consistency

---

## References
- [Debezium Documentation](https://debezium.io/documentation/)
- [Apache Pulsar Documentation](https://pulsar.apache.org/docs/)
- [CDC Concepts (Martin Kleppmann)](https://martin.kleppmann.com/2015/05/18/event-sourcing-cdc.html)
