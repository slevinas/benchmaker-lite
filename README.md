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
> It demonstrates architecture and practices, **not** any real XPLG code or IP.

---

## 🚀 Getting Started

### 1. Start the stack

```bash
docker-compose up --build
```
