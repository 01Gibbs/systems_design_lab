"""Metrics endpoint for Prometheus scraping"""

from fastapi import APIRouter, Request, Response

router = APIRouter(tags=["observability"])


@router.get("/metrics")
async def metrics_endpoint(request: Request) -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text exposition format.
    """
    metrics_port = request.app.state.metrics
    metrics_data = metrics_port.get_metrics()
    return Response(content=metrics_data, media_type="text/plain")
