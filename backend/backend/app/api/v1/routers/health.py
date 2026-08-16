"""Liveness/readiness endpoint.

Deliberately excluded from auth and tenant-context requirements (see the
middleware bypass list in core/config and, later, the tenant middleware)
so Docker Compose healthchecks and load balancer probes never need
credentials.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    from app.core.config import get_settings

    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment.value,
    )
