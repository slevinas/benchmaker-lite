import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .config import OTEL_EXPORTER_ENDPOINT, SERVICE_NAME as SERVICE_NAME_VALUE

logger = logging.getLogger(__name__)


def init_instrumentation(app: FastAPI) -> None:
    """
    Set up OpenTelemetry tracing for the FastAPI app.

    This sends traces to an OTEL Collector via OTLP/gRPC.
    """
    resource = Resource(attributes={
        SERVICE_NAME: SERVICE_NAME_VALUE,
    })

    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT, insecure=True)
    span_processor = BatchSpanProcessor(span_exporter)

    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    logger.info("OpenTelemetry instrumentation initialized.")
