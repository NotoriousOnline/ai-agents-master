"""Tests for the example agent API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_example_agent_run(client: AsyncClient):
    """POST /api/v1/agents/example/run returns agent response."""
    response = await client.post(
        "/api/v1/agents/example/run",
        json={"query": "hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "example"
    assert data["query"] == "hello"
    assert "Echo: hello" in data["result"]
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_example_agent_run_empty_query(client: AsyncClient):
    """POST with empty query returns validation error."""
    response = await client.post(
        "/api/v1/agents/example/run",
        json={"query": ""},
    )
    assert response.status_code == 422
