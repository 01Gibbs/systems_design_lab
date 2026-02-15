"""OpenTelemetry tracing configuration"""

import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)
from opentelemetry.instrumentation.sqlalchemy import (
    SQLAlchemyInstrumentor,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.engine import Engine


def setup_tracing(app_name: str = "systems-design-lab-backend") -> None:
    """
    Configure OpenTelemetry tracing with Tempo backend.

    Args:
        app_name: Service name for tracing
    """
    # Skip tracing if explicitly disabled (e.g., during tests)
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        return

    # Resource identifies your service
    resource = Resource(
        attributes={
            SERVICE_NAME: app_name,
            "deployment.environment": os.getenv("APP_ENV", "local"),
        }
    )

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # OTLP exporter to Tempo
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317")

    try:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

        # Batch processor for efficiency
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)

        # Set as global tracer provider
        trace.set_tracer_provider(provider)
    except Exception as e:
        # If OTLP endpoint not available (e.g., no tempo), continue without tracing
        import logging

        logging.warning(f"Failed to setup OpenTelemetry: {e}")


def instrument_fastapi(app: FastAPI) -> None:
    """Instrument FastAPI with OpenTelemetry"""
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        import logging

        logging.warning(f"Failed to instrument FastAPI: {e}")


def instrument_sqlalchemy(engine: Engine) -> None:
    """Instrument SQLAlchemy for DB query tracing"""
    try:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    except Exception as e:
        import logging

        logging.warning(f"Failed to instrument SQLAlchemy: {e}")
