# Observability Pipeline (Mermaid Diagram)

```mermaid
flowchart LR
    subgraph App["FastAPI App (benchmaker-lite)"]
        A[HTTP Request]
        B[Business Logic]
        C[OTel SDK<br/>Traces + Spans]
        A --> B --> C
    end

    C --> D[OTLP Export]

    subgraph Collector["OTel Collector"]
        D --> E[Receivers (otlp)]
        E --> F[Processors (batch)]
        F --> G[Exporters (debug)]
    end
