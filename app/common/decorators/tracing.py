"""Module documentation for `app/common/decorators/tracing.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

import os
from functools import wraps

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.enums.env import EnvName


def setup_tracing(service_name: str = "enterprise_agent") -> None:
    """Summary of `setup_tracing`.

    Args:
        service_name (str): Description of service_name, default='enterprise_agent'.

    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    if os.getenv("ENV", EnvName.DEV) != "prod":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
        )
    )


def get_tracer(module_name: str = __name__):
    """Summary of `get_tracer`.

    Args:
        module_name (str): Description of module_name, default=__name__.

    Returns:
        Any: Description of return value.

    """
    return trace.get_tracer(module_name)


def trace_span(name: str):
    """Summary of `trace_span`.

    Args:
        name (str): Description of name.

    Returns:
        Any: Description of return value.

    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(name) as span:
                return func(*args, **kwargs)

        return wrapper

    return decorator
