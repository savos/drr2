"""
Tests for health check endpoint.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint returns 200 OK."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert "message" in data


@pytest.mark.asyncio
async def test_health_check_structure(client: AsyncClient):
    """Test the health check response has correct structure."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    # Verify required fields
    assert "status" in data
    assert "message" in data

    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["message"], str)
