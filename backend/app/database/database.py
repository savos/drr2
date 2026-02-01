"""Database connection and session management."""
import os
import re
import logging
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, inspect
import pymysql

from app.config.database import Base

logger = logging.getLogger(__name__)

# Database configuration from environment
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_ROOT_PASSWORD = os.getenv("DB_ROOT_PASSWORD", "root")

# Validate DB_NAME to prevent SQL injection via environment variable
if not re.match(r'^[a-zA-Z0-9_-]+$', DB_NAME):
    raise ValueError(f"DB_NAME contains invalid characters: '{DB_NAME}'. Only alphanumeric, underscore, and hyphen are allowed.")

# Create async database URL
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine — only log queries in DEV
_environment = os.getenv("ENVIRONMENT", "DEV").upper()
engine = create_async_engine(
    DATABASE_URL,
    echo=(_environment == "DEV"),
    pool_pre_ping=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        yield session


async def ensure_database_exists():
    """Ensure the database exists, create it if it doesn't."""
    max_retries = 30
    retry_delay = 1  # Start with 1 second

    for attempt in range(max_retries):
        try:
            # Connect without database name using pymysql (sync)
            connection = pymysql.connect(
                host=DB_HOST,
                port=int(DB_PORT),
                user="root",
                password=DB_ROOT_PASSWORD,
                connect_timeout=5,
            )
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.commit()
            cursor.close()
            connection.close()

            logger.info(f"Database '{DB_NAME}' is ready")
            return
        except pymysql.err.OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10s
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise
        except Exception as e:
            logger.error(f"Error ensuring database exists: {e}")
            raise


async def database_has_tables() -> bool:
    """Check if database has any tables."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(f"SHOW FULL TABLES FROM `{DB_NAME}`"))
            tables = result.fetchall()
            return len(tables) > 0
    except Exception as e:
        logger.error(f"Error checking for tables: {e}")
        return False


async def create_database_and_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


def run_migrations():
    """Run Alembic migrations."""
    import subprocess
    import sys
    from pathlib import Path

    app_dir = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=app_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"Migration failed: {result.stderr}")
        raise RuntimeError(f"Migration failed: {result.stderr}")

    logger.info("Migrations completed successfully")
