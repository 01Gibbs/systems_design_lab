"""Observability middleware - enriches logs and metrics with context"""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from app.application.ports.metrics import MetricsPort

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Enriches requests with observability context.

    - Adds trace_id and span_id to logs
    - Records HTTP metrics
    - Correlates with request_id
    """

    def __init__(self, app: Any, metrics: MetricsPort) -> None:
        super().__init__(app)
        self.metrics = metrics

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        # Get trace context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else "none"
        span_id = format(span_context.span_id, "016x") if span_context.is_valid else "none"

        # Get request_id from RequestIdMiddleware
        request_id = getattr(request.state, "request_id", "unknown")

        # Enrich logging context
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "method": request.method,
                "path": str(request.url.path),
            },
        )

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        labels = {
            "method": request.method,
            "endpoint": str(request.url.path),
            "status": str(response.status_code),
        }

        self.metrics.increment_counter("http_requests_total", labels)
        self.metrics.observe_histogram("http_request_duration_seconds", duration, labels)

        # Log completion
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "status_code": response.status_code,
                "duration_seconds": duration,
            },
        )

        return response
