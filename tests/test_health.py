"""Tests for health and version endpoints."""

import pytest
from httpx import AsyncClient

from app.main import app
from app.api.v1.health import health_check, version


@pytest.mark.asyncio
async def test_health_check():
    """Health endpoint returns status ok."""
    result = await health_check()
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_version():
    """Version endpoint returns version string."""
    result = await version()
    assert "version" in result
    assert result["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_via_client(client: AsyncClient):
    """GET /api/v1/health returns 200 and status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient):
    """GET /health at root returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_version(client: AsyncClient):
    """GET /version at root returns 200."""
    response = await client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
