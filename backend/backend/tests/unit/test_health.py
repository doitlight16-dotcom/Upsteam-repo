"""Sanity check that the app factory and health endpoint work end to end."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_check_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Appex Asset Suite"
