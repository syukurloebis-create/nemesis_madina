# backend/telemetry/tracing.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import os


def setup_tracing(service_name: str = "nemesis-dashboard"):
    """Setup OpenTelemetry tracing."""
    provider = TracerProvider()
    
    # Configure exporters
    exporters = []
    
    # Console exporter for development
    if os.getenv("ENV", "development") == "development":
        exporters.append(ConsoleSpanExporter())
    
    # OTLP exporter for production
    if os.getenv("OTLP_ENDPOINT"):
        exporters.append(OTLPSpanExporter(endpoint=os.getenv("OTLP_ENDPOINT")))
    
    for exporter in exporters:
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(service_name)


def instrument_fastapi(app, tracer):
    """Instrument FastAPI application."""
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        excluded_urls="/health,/metrics,/readiness"
    )


def instrument_database(engine):
    """Instrument SQLAlchemy database."""
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        tracer_provider=trace.get_tracer_provider()
    )


@asynccontextmanager
async def trace_operation(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for tracing operations."""
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        yield span