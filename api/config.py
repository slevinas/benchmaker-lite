import os
import sys

OTEL_EXPORTER_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4317",
)
SERVICE_NAME = os.getenv("SERVICE_NAME", "benchmaker-lite-api")
