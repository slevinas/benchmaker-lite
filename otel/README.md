# **Benchmaker-Lite — FastAPI Benchmarking & Observability Pipeline**

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" />
  <img src="https://img.shields.io/badge/FastAPI-Instrumented%20with%20OTel-009688.svg" />
  <img src="https://img.shields.io/badge/ClickHouse-Analytics%20DB-yellow.svg" />
  <img src="https://img.shields.io/badge/OpenTelemetry-Collector%20Pipeline-purple.svg" />
  <img src="https://img.shields.io/badge/Asyncio-Concurrency%20Testing-orange.svg" />
  <img src="https://img.shields.io/badge/Docker-Compose-green.svg" />
  <img src="https://img.shields.io/badge/Status-Active%20Project-brightgreen.svg" />
</p>


## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [FastAPI Benchmark Target](#1-fastapi-benchmark-target)
  - [Async Benchmark Client](#2-async-benchmark-client)
  - [ClickHouse Layer](#3-clickhouse--db-layer)
  - [OpenTelemetry Collector](#4-opentelemetry-collector)
- [Schema](#schema)
- [Running the Stack](#running-the-stack)
  - [Start Services](#1-start-services)
  - [Run a Benchmark](#2-run-a-benchmark)
  - [Query Results](#3-query-results)
- [Why This Project Exists](#why-this-project)
- [Project Internals](#project-internals)
- [Roadmap](#roadmap)
- [License](#license)



Benchmaker-Lite is a **fully containerized benchmarking and observability system** built around:

- **FastAPI** (instrumented with OpenTelemetry)
- **OpenTelemetry Collector** (file + debug exporters)
- **ClickHouse** (analytics DB)
- **Async Python benchmark client** (httpx + asyncio)
- **Custom ClickHouse client** (env-driven config, JSONEachRow inserts)

It demonstrates real-world DevOps, observability, performance engineering, and backend automation patterns.

---

# 📐 **Architecture Overview**

```
                      ┌──────────────────────┐
                      │   Benchmark Client    │
                      │  (asyncio + httpx)    │
                      │  generate load / run  │
                      └───────────┬───────────┘
                                  │
                                  ▼
                     POST /api/vector/add (FastAPI)
                                  │
                                  ▼
                ┌────────────────────────────────────┐
                │        FastAPI Service              │
                │  - Vector-add endpoint              │
                │  - OTel instrumentation (SDK)       │
                │  - Emits traces & metrics           │
                └─────────────────┬───────────────────┘
                                  │  OTLP/gRPC
                                  ▼
               ┌──────────────────────────────────────┐
               │        OpenTelemetry Collector        │
               │  - Receives telemetry                 │
               │  - Batching processor                 │
               │  - Exports: file(traces), file(metrics) │
               │  - Debug exporter (stdout)            │
               └─────────────────┬────────────────────┘
                                  │
                              ETL / Ingest
                                  │
                                  ▼
              ┌────────────────────────────────────────┐
              │               ClickHouse                │
              │  - schema: benchmark_results           │
              │  - JSONEachRow inserts                 │
              │  - analytical queries (p95, p99, etc.) │
              └────────────────────────────────────────┘
```

---

# ⚙️ **Components**

### **1. `/api` — FastAPI Benchmark Target**

- Implements `/api/vector/add`
- Instrumented with OpenTelemetry SDK
- Emits traces & metrics to OTEL Collector
- Designed for load-generation & latency measurement

### **2. `/benchmark_client` — Async Python Runner**

- Uses `httpx.AsyncClient` + `asyncio`
- Launches concurrent workers
- Computes:

  - avg latency
  - p95, p99
  - min/max

- Stores structured results into ClickHouse
- Can fetch and display recent benchmark history

### **3. `/clickhouse` — DB Layer**

Includes:

- `client.py` (custom ClickHouse HTTP client)
- `init.sql` (schema definitions)
- Config-driven table design for benchmark analytics

Table:

```sql
CREATE TABLE benchmark_results (
    timestamp       DateTime DEFAULT now(),
    endpoint        String,
    avg_latency     Float64,
    p95_latency     Float64,
    p99_latency     Float64,
    min_latency     Float64,
    max_latency     Float64,
    total_requests  UInt32
) ENGINE = MergeTree()
ORDER BY (timestamp, endpoint);
```

### **4. `/otel` — OpenTelemetry Collector**

- Receives FastAPI telemetry
- Writes traces/metrics to local file
- Debug exporter for introspection

---

# 🐳 **Running the Entire Pipeline**

### **1. Start dependencies**

```bash
docker-compose up --build
```

This launches:

- ClickHouse
- OTEL Collector
- FastAPI benchmark service

### **2. Run a benchmark**

```bash
python -m benchmark_client.run_benchmark
```

Output:

```
=== Benchmark Summary ===
count: 500
avg: 0.0103s
p95: 0.0199s
p99: 0.0642s
min: 0.0041s
max: 0.0888s

Saving summary to ClickHouse...
Saved.

Fetching recent results...
timestamp                  avg_latency     p95_latency   total_requests
-----------------------------------------------------------------------
2025-12-05 13:24:33        0.0103           0.0199         500
...
```

### **3. Query results manually**

```sql
SELECT *
FROM benchmark_results
ORDER BY timestamp DESC
LIMIT 10;
```

---

# 📦 **Why This Project?**

This system simulates a **real observability + benchmarking pipeline**:

- Microservice exposing a performance-critical endpoint
- Telemetry instrumentation & OTEL ingestion
- Async load generation (multi-worker)
- Persistance to ClickHouse for analytics
- Queryable history of performance metrics

It showcases:

- DevOps automation
- Distributed tracing
- Telemetry pipelines
- Backend benchmarking
- Async Python tooling
- ClickHouse data engineering
- Docker Compose orchestration
- Practical, production-style architecture

---
