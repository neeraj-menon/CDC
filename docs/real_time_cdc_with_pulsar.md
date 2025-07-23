# Real-Time CDC with Event Retention via Apache Pulsar

## Overview
This document outlines the architecture and implementation plan for a real-time Change Data Capture (CDC) pipeline for device event management, leveraging PostgreSQL (RDS), a custom CDC engine, Apache Pulsar for event retention, and downstream AI-driven workflows.

---

## 1. CDC Event Capture
- Use PostgreSQL logical decoding (WAL) to capture device events (inserts/updates) in real time.
- Implement a Python-based CDC engine (`anti-debezium/cdc_consumer.py`).

## 2. Publish Events to Apache Pulsar
- Integrate the Pulsar Python client into the CDC engine.
- For each event, publish to a Pulsar topic (e.g., `persistent://public/default/device-cdc-events`).
- Pulsar retains events for a configurable period, supporting replay and durability.

## 3. Downstream Processing (Activi Workflow)
- Pulsar consumers ingest events for:
  - Status evaluation (BAU, Delayed, Defaulted, Fraud)
  - LLM summarization and trend detection
  - Saving summaries/results back to the DB
  - Sending notifications (email, Slack, etc.)

## 4. Observability & Reliability
- Add logging to CDC and Pulsar publishing steps.
- Implement error handling and retry logic for Pulsar publish failures.
- Monitor Pulsar topic lag and consumer health.

## 5. Documentation & Testing
- Document setup, configuration, and operational procedures.
- Test end-to-end: insert test events, verify Pulsar ingestion, and downstream processing.

---

## Workflow Diagram

```mermaid
flowchart TD
    subgraph Device_Provisioning["📱 Device Provisioning"]
        A1[OEM/Customer/Your Team<br/>Installs Security Software]
        A2[Device Registered<br/>with Management Service]
    end

    subgraph Postgres_RDS["📦 PostgreSQL (RDS)"]
        B1[Device Event Table<br/>(Usage, Payment, SIM Change)]
        B2[Policy & Status Tables<br/>(BAU, Delayed, Defaulted, Fraud)]
    end

    subgraph Scintle_CDC["🔁 Scintle CDC Engine"]
        C1[Capture Change<br/>(WAL Decode)]
        C2[Publish Event<br/>to Apache Pulsar]
    end

    subgraph Activi_Workflow["🧠 Activi Visual Workflow"]
        D1[Ingest Event<br/>from Pulsar]
        D2[Determine Status<br/>(BAU, Delayed, Defaulted, Fraud)]
        D3[LLM Summary & Trend Detection]
        D4[Save Summary<br/>Back to DB]
        D5[Send Notification<br/>(Email/Slack)]
    end

    subgraph Manager["👤 Manager"]
        E1[Receives Notification]
    end

    %% Flow Connections
    A1 --> A2 --> B1
    B1 --> C1 --> C2 --> D1
    B2 --> D2
    D1 --> D2
    D2 --> D3
    D3 --> D4
    D3 --> D5
    D5 --> E1
```

---

## Notes
- Pulsar is retained as the event backbone for reliability, replayability, and decoupling of CDC and downstream workflows.
- This architecture supports future extensibility (new consumers, analytics, etc.) with minimal changes.
