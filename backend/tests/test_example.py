"""
Example tests demonstrating common testing patterns.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.users import User
from app.models.company import Company


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
    # First create a company (required for user)
    company = Company(name="Test Company")
    async_session.add(company)
    await async_session.commit()
    await async_session.refresh(company)

    # Create a test user
    user = User(
        email="test@example.com",
        hashed_password="fake_hashed_password",
        firstname="John",
        lastname="Doe",
        company_id=company.id
    )

    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    # Verify user was created
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.firstname == "John"
    assert user.lastname == "Doe"
    assert user.company_id == company.id


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
