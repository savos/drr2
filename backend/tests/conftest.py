"""
Pytest configuration and fixtures for backend tests.
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Ensure .env is loaded and skip app DB init in tests before importing app
try:
    from dotenv import load_dotenv  # type: ignore
    from pathlib import Path
    # repo root: tests -> backend -> repo
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except Exception:
    # If python-dotenv is unavailable, app will still try to load .env
    pass

# Ensure app skips DB initialization/migrations under tests
os.environ.setdefault("SKIP_DB_INIT", "1")

from app.main import app
from app.config.database import Base
from app.database.database import get_db


# Test database URL - configurable via environment variable
# For GitHub Actions: mysql+aiomysql://root:test_root_password@localhost:3306/test_db
# For Docker Compose: mysql+aiomysql://user:password@db:3306/test_db
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "mysql+aiomysql://user:password@db:3306/test_db"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_engine():
    """Create an async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async session for testing."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""

    # Override the get_db dependency
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
