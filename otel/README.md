# **📊 Benchmaker-Lite — FastAPI Benchmarking + Observability Pipeline**

A small but complete DevOps + Observability project demonstrating:

- FastAPI service instrumented with **OpenTelemetry**
- Async benchmark client using **httpx + asyncio**
- OpenTelemetry Collector receiving traces/metrics
- Exporting telemetry into **ClickHouse**
- Docker Compose orchestration across all components
- Benchmark storage, analysis queries, and end-to-end reproducibility


---

### 1️⃣ Observability Pipeline Diagram

```mermaid
flowchart LR
    subgraph App["FastAPI App (benchmaker-lite)"]
        A[Incoming HTTP Requests]
        B[Business Logic / Vector Ops]
        C[OTel SDK<br/>Traces & Metrics]
        A --> B --> C
    end

    C --> D[OTLP Exporter]

    subgraph Collector["OTel Collector"]
        D --> E[Receivers (otlp)]
        E --> F[Processors<br/>(batch, attributes, transform)]
        F --> G[Exporters<br/>(clickhouse / file)]
    end

    G --> H[Fluent Bit (optional)]
    H --> I[ClickHouse]

    I --> J[Analytics / Queries<br/>(latency, errors, throughput)]
```

### 2️⃣ Benchmaker-lite System Diagram

```mermaid
flowchart LR
    U[Developer / Engineer] --> CLI[Benchmark CLI (Python)]
    CLI -->|async httpx| BM[Benchmark Runner]

    subgraph Runner["Benchmark Runner"]
        BM -->|N concurrent requests| API[(FastAPI Service)]
        BM --> MET[Benchmark Summary<br/>(latency stats, errors)]
    end

    API --> OTel[OTel SDK]
    OTel --> COL[OTel Collector]
    COL --> CH[ClickHouse]

    MET --> CH
    CH --> Q[Analysis / Visualization<br/>(SQL queries, notebooks)]
```
---

## **🚀 Features**

### **Benchmarking**

- Async Python client (`httpx`) sending thousands of requests
- Measures: p95/p99 latency, min/max, total throughput
- Stores summary into ClickHouse (`benchmark_results` table)

### **Observability**

- Automatic OTEL instrumentation of FastAPI routes
- Real traces emitted per benchmark request
- Collector pipelines exporting to ClickHouse
- Schema auto-created (`otel_traces`, `otel_metrics_*`)

### **DevOps**

- Multi-container Docker Compose setup
- Resilient startup (collector waits for ClickHouse)
- Configuration via environment variables
- All services run locally with one command:

```bash
docker-compose up --build
```

---

## **🧱 Architecture  Diagram**


```
                        ┌────────────────────────┐
                        │     Benchmark Client    │
                        │  (async httpx load gen) │
                        └────────────┬────────────┘
                                     │
                                     ▼
                         HTTP Requests (load)
                                     │
                                     ▼
                   ┌─────────────────────────────────┐
                   │             FastAPI              │
                   │  - /vector/add benchmark route   │
                   │  - /health                       │
                   ├─────────────────────────────────┤
                   │  OTEL SDK Instrumentation        │
                   │  - Traces emitted per request    │
                   │  - Metrics (latency counters)    │
                   └──────────────────┬────────────────┘
                                      │ OTLP (gRPC/HTTP)
                                      ▼
                        ┌────────────────────────────────┐
                        │  OpenTelemetry Collector        │
                        │---------------------------------│
                        │ Receivers:                      │
                        │   - otlp/http                   │
                        │   - otlp/grpc                   │
                        │ Processors:                     │
                        │   - batch                       │
                        │   - (optional transforms)       │
                        │ Exporters:                      │
                        │   - debug                       │
                        │   - clickhouse (traces/metrics) │
                        └──────────────────┬──────────────┘
                                           │ TCP (9000)
                                           ▼
                         ┌──────────────────────────────────┐
                         │            ClickHouse             │
                         │-----------------------------------│
                         │  Database: otel                   │
                         │  Tables created automatically:    │
                         │    - otel_traces                  │
                         │    - otel_logs                    │
                         │    - otel_metrics_*               │
                         │                                   │
                         │  Benchmark Results (manual insert)│
                         │  stored into: default.bench...    │
                         └───────────────────────────────────┘
```
## **Architecture Overview**
### **What the architecture demonstrates**

- Observability pipeline from code → telemetry → storage
- Automation pipeline for benchmarking, latency measurement
- Real-world DevOps stack (ClickHouse, OTEL Collector, Docker Compose)
- Async load testing and benchmarking framework you built
- Experience in distributed tracing, schema creation, and telemetry exports

---

---

## **🧪 Running a Benchmark**

```bash
python -m benchmark_client.run_benchmark
```

Example output:

```
Benchmark Summary
Total requests: 5000
Avg latency: 0.0080s
p95 latency: 0.021s
p99 latency: 0.041s
Min latency: 0.0017s
Max latency: 0.0876s
```

---

## **📦 Docker Stack**

| Service              | Description                                          |
| -------------------- | ---------------------------------------------------- |
| **FastAPI app**      | Handles `/vector/add` requests and emits OTEL traces |
| **OTEL Collector**   | Receives OTLP data and exports to ClickHouse         |
| **ClickHouse**       | Stores traces, metrics, and benchmark results        |
| **Benchmark Client** | Generates concurrent load using asyncio              |

---

## **🔍 Querying Telemetry in ClickHouse**

### Recent traces:

```sql
SELECT Timestamp, ServiceName, SpanName
FROM otel_traces
ORDER BY Timestamp DESC
LIMIT 20;
```

### p95 latency (example for deeper analysis):

```sql
SELECT
  quantile(0.95)(Duration) AS p95_latency
FROM otel_traces
WHERE ServiceName = 'benchmaker-lite-api';
```

### Benchmark summaries:

```sql
SELECT *
FROM benchmark_results
ORDER BY timestamp DESC
LIMIT 10;
```

---


























# OTEL Collector Configuration

This folder contains the configuration for the **OpenTelemetry Collector** used
by `benchmaker-lite`.

- `collector-config.yaml` – minimal pipeline:
  - `otlp` receiver (gRPC + HTTP)
  - `batch` processor
  - `debug` exporter (prints spans to stdout)

In a more advanced setup, you could:

- Export traces/metrics directly into ClickHouse or another backend.
- Add processors for attribute enriching, sampling, or redaction.
- Add metrics/log pipelines alongside traces.
