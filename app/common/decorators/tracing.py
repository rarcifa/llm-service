"""
tracing.py

Sets up distributed tracing using OpenTelemetry. Includes configuration for:
- Console exporter in development
- OTLP exporter in all environments (e.g., for Phoenix, Grafana Tempo, etc.)
- Span-level decorators for automatic instrumentation

This module is safe to import across all services and ensures trace context
is preserved across spans.

Author: Ricardo Arcifa
Created: 2025-02-03
"""

import os
from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_tracing(service_name: str = "enterprise_agent") -> None:
    """
    Configures the global OpenTelemetry tracer provider with span processors.

    - In development (`ENV != "prod"`), logs spans to the console.
    - In all environments, exports spans to a local OTLP collector.

    Args:
        service_name (str): Name used for tracing service resource. Defaults to "enterprise_agent".
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Log to console in non-production environments
    if os.getenv("ENV", "dev") != "prod":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Always export to OTLP for backend tracing
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
        )
    )


def get_tracer(module_name: str = __name__):
    """
    Returns an OpenTelemetry tracer for the specified module or context.

    Args:
        module_name (str): Name of the module (used in trace UI). Defaults to `__name__`.

    Returns:
        Tracer: An OpenTelemetry tracer instance.
    """
    return trace.get_tracer(module_name)


def trace_span(name: str):
    """
    Decorator that wraps a function in an OpenTelemetry span.

    Args:
        name (str): Name of the span to show in tracing tools.

    Returns:
        Callable: Wrapped function that will trace execution duration and errors.

    Example:
        @trace_span("generate_response")
        def generate(...): ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(name) as span:
                return func(*args, **kwargs)

        return wrapper

    return decorator
