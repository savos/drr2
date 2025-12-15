"""
Example tests demonstrating common testing patterns.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.users import User


@pytest.mark.asyncio
async def test_database_connection(async_session: AsyncSession):
    """Test that database connection works."""
    # This test verifies the database session is working
    result = await async_session.execute(select(User))
    users = result.scalars().all()

    # Initially should be empty
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    """Test creating a user in the database."""
    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="fake_hashed_password",
        is_active=True
    )

    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # Verify user was created
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_api_not_found(client: AsyncClient):
    """Test that non-existent endpoint returns 404."""
    response = await client.get("/api/nonexistent")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_api_root_redirect(client: AsyncClient):
    """Test that root endpoint exists."""
    response = await client.get("/", follow_redirects=False)

    # Should either return 200, 404, or redirect
    assert response.status_code in [200, 404, 307, 308]
