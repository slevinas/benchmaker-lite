
---

## `diagrams/benchmaker-architecture.md`

```markdown
# Benchmaker-lite Architecture (Mermaid Diagram)

```mermaid
flowchart LR
    U[Engineer / CLI] --> CLI[Benchmark Runner (Python, asyncio)]
    CLI -->|Concurrent HTTP requests| API[(FastAPI Service)]

    API --> OTel[OTel SDK]
    OTel --> COL[OTel Collector]
    COL --> CH[(ClickHouse? / Other backend)]

    CLI --> SUM[Benchmark Summary (avg, p95, etc.)]
    SUM --> CH
