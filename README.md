# benchmaker-lite

A lightweight, public-safe example of a **benchmarking + observability pipeline** inspired by real-world work:

- Python async benchmark client (`httpx` + `asyncio`)
- FastAPI service with vector operations
- OpenTelemetry instrumentation for HTTP requests
- OTEL Collector pipeline (initially exporting to debug logs)
- ClickHouse for storing benchmark summaries
- Docker Compose for local development
- GitHub Actions CI (basic)

> ⚠️ Note: This repo is intentionally small and generic.  




---
# **📊 Benchmaker-Lite — FastAPI Benchmarking + Observability Pipeline**

A small but complete DevOps + Observability project demonstrating:

* FastAPI service instrumented with **OpenTelemetry**
* Async benchmark client using **httpx + asyncio**
* OpenTelemetry Collector receiving traces/metrics
* Exporting telemetry into **ClickHouse**
* Docker Compose orchestration across all components
* Benchmark storage, analysis queries, and end-to-end reproducibility

---

## **🚀 Features**

### **Benchmarking**

* Async Python client (`httpx`) sending thousands of requests
* Measures: p95/p99 latency, min/max, total throughput
* Stores summary into ClickHouse (`benchmark_results` table)

### **Observability**

* Automatic OTEL instrumentation of FastAPI routes
* Real traces emitted per benchmark request
* Collector pipelines exporting to ClickHouse
* Schema auto-created (`otel_traces`, `otel_metrics_*`)

### **DevOps**

* Multi-container Docker Compose setup
* Resilient startup (collector waits for ClickHouse)
* Configuration via environment variables
* All services run locally with one command:

```bash
docker-compose up --build
```

---

## **🧱 Architecture Diagram**

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
                   ┌───────────────────────────────── ┐
                   │             FastAPI              │
                   │  - /vector/add benchmark route   │
                   │  - /health                       │
                   ├───────────────────────────────── ┤
                   │  OTEL SDK Instrumentation        │
                   │  - Traces emitted per request    │
                   │  - Metrics (latency counters)    │
                   └──────────────────┬───────────────┘
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
---

## 🚀 Getting Started

### 1. Start the stack

```bash
docker-compose up --build
```
---





---
##### Running the docker compose walkthrough and fixing plan

Love this, this is exactly the right instinct: understand the moving pieces before we crank up the complexity. 😊

I’ll do two things in this reply:

1. Walk through your **current `docker-compose.yml` and its execution flow** so it’s crystal clear.
2. Confirm why the **build will fail right now** and give you a **simple Dockerfile + small tweaks** so `docker-compose up` actually works.

We’ll handle the **“B: full OTel traces + metrics into ClickHouse”** in the *next* step, after the basics are solid.

---

## 1️⃣ What your current `docker-compose.yml` is doing

This is (roughly) what we have:

```yaml
version: "3.9"

services:
  api:
    build: ./api
    container_name: benchmaker_api
    ports:
      - "8000:8000"
    environment:
      OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
    depends_on:
      - clickhouse
      - otel-collector

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    container_name: benchmaker_clickhouse
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - ./clickhouse/init.sql:/docker-entrypoint-initdb.d/init.sql

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    container_name: benchmaker_otel_collector
    command: ["--config=/otel-local-config.yaml"]
    volumes:
      - ./otel/collector-config.yaml:/otel-local-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
```

### Compose execution flow when you run `docker-compose up`:

1. **Compose looks at each service**: `api`, `clickhouse`, `otel-collector`.

2. For each service:

   * If it has **`image:`**, it pulls the image (if needed).
   * If it has **`build:`**, it builds a Docker image from that path.

3. In your case:

   * `clickhouse` → pulls `clickhouse/clickhouse-server:latest`
   * `otel-collector` → pulls `otel/opentelemetry-collector-contrib:latest`
   * `api` → tries to **build** from `./api` (this is where it will currently fail)

4. **`depends_on`** for `api`:

   * Compose will *start* `clickhouse` and `otel-collector` containers before `api`.
   * It does **not** wait for them to be “healthy,” only started. (We can add healthchecks later if we want.)

5. **Networking**:

   * All services are on the same default network.
   * Each service name (`api`, `clickhouse`, `otel-collector`) becomes a DNS name inside the network.
   * That’s why this env var works inside the `api` container:

     ```yaml
     OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317
     ```

     From inside the `api` container, `otel-collector` resolves to the collector’s container IP.

6. **Volumes**:

   * `clickhouse` mounts `./clickhouse/init.sql` into `/docker-entrypoint-initdb.d/init.sql`.

     * ClickHouse’s entrypoint runs all `.sql` files in that directory on first startup.
     * That creates your `benchmark_results` table automatically.
   * `otel-collector` mounts your local `./otel/collector-config.yaml` as `/otel-local-config.yaml` inside the container, then uses that file via the `command:`.

7. **Ports**:

   * `api: 8000:8000` → you can hit `http://localhost:8000` from your host.
   * `clickhouse: 8123:8123` → HTTP interface on `http://localhost:8123`.
   * `clickhouse: 9000:9000` → native TCP protocol (for drivers).
   * `otel-collector: 4317:4317`, `4318:4318` → OTLP endpoints accessible from the host (and containers).

So conceptually, the flow is:

* **Benchmark client on host** → calls `http://localhost:8000` → hits **api container**
* **API** → emits traces via OTel SDK → sends spans to `http://otel-collector:4317` (inside network)
* **Collector** → processes/export traces (right now only debug; later to ClickHouse)
* **Benchmark client** → writes summary to ClickHouse via `http://localhost:8123` (host→container mapping)

---

## 2️⃣ Why `docker-compose` build will fail right now

You’re absolutely right: with the current config, this will likely fail:

```bash
docker-compose up
```

…because of this line:

```yaml
  api:
    build: ./api
```

Compose expects a **Dockerfile in `./api`**, but we haven’t created one yet. So it will error with something like:

> `ERROR: Cannot locate specified Dockerfile: Dockerfile`
> or
> `failed to solve: failed to read dockerfile: open /api/Dockerfile: no such file or directory`

So your intuition is correct. ✅

---

## 3️⃣ Fixing this: add a simple `Dockerfile` for the API

Let’s make the minimal thing that works and is clear.

### Step 1: Create `api/requirements.txt`

```txt
fastapi
uvicorn[standard]
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp
opentelemetry-instrumentation-fastapi
```

You can add more later (e.g. pydantic, etc.), but FastAPI already pulls that in.

---

### Step 2: Create `api/Dockerfile`

In `api/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system deps (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual app code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the app with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> Note: the key here is that the module path `api.main:app` matches your package structure
> (i.e., the container sees `/app/api/main.py` with `app = create_app()`).

Your repo structure should look like:

```text
benchmaker-lite/
├─ api/
│  ├─ main.py
│  ├─ routes.py
│  ├─ instrumentation.py
│  ├─ config.py
│  ├─ requirements.txt
│  └─ Dockerfile
...
```

---

### Step 3: Validate the build and start sequence

From the project root:

```bash
# Build the api image
docker-compose build api

# Then start everything
docker-compose up
```

You should see:

* ClickHouse logs showing startup + table creation
* OTel Collector logs with “Starting…” and debug exporter info
* API logs from uvicorn starting on `0.0.0.0:8000`

Then you can hit:

```bash
curl http://localhost:8000/health
```

And run the benchmark (from host):

```bash
python -m benchmark_client.run_benchmark
```

---

## 4️⃣ Recap of the execution flow (with Dockerfile in place)

When you do:

```bash
docker-compose up
```

1. **Builds `api` image** using `api/Dockerfile`
2. **Starts `clickhouse`**:

   * Runs `init.sql`, creates `benchmark_results` table
3. **Starts `otel-collector`**:

   * Loads `collector-config.yaml`
   * Opens OTLP endpoints
4. **Starts `api`**:

   * Runs uvicorn, exposes port 8000
   * OTel SDK inside the app connects to `http://otel-collector:4317`
5. You then **run the benchmark client** from your host:

   * Calls the API
   * API emits traces to collector
   * Benchmark client writes summary into ClickHouse

This is the foundational flow we’ll extend to **full traces + metrics → ClickHouse** in the next step.

---

## 🔜 Next: Implementing your choice **B** (full OTel traces + metrics into ClickHouse)

Now that we’re on the same page about:

* `docker-compose` behavior
* How the containers interact
* Why the build was failing and how to fix it

Next step will be to:

1. Add ClickHouse tables for OTel traces & metrics
2. Update `collector-config.yaml` to:

   * receive OTLP traces + metrics
   * process them
   * export them to ClickHouse
3. Validate with:

   * generating some requests
   * querying ClickHouse for spans/metrics

---

If you’d like, your very next move could be:

1. Add `api/requirements.txt`
2. Add `api/Dockerfile`
3. Run:

```bash
docker-compose build api
docker-compose up
```

If something blows up, send me the error text, and I’ll help you fix it.
Once it starts cleanly, we jump straight into **OTel → ClickHouse traces + metrics (Option B)**.


