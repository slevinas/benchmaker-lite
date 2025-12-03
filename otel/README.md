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
