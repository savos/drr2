"""Main FastAPI application."""
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config.env import load_project_env
from app.database.database import (
    create_database_and_tables,
    database_has_tables,
    ensure_database_exists,
    run_migrations,
)
 
# Load environment variables before importing routers that may read env at import time
ENV_FILE = load_project_env()

"""
Import routers explicitly as submodules to avoid issues with package
fromlist imports in certain environments/packagers.
"""
import app.routers.health as health
import app.routers.auth as auth
import app.routers.users as users
import app.routers.slack as slack
import app.routers.telegram as telegram
import app.routers.discord as discord
import app.routers.teams as teams
import app.routers.cases as cases

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    logger.info("Starting application...")

    try:
        # Allow tests/CI to skip DB initialization and migrations entirely
        if os.getenv("SKIP_DB_INIT") == "1":
            logger.info("SKIP_DB_INIT=1 set; skipping DB init/migrations")
            yield
            logger.info("Shutting down application")
            return

        # Ensure database exists
        logger.info("Ensuring database exists...")
        await ensure_database_exists()

        # Get environment setting
        environment = os.getenv("ENVIRONMENT", "DEV").upper()

        # Check if this is a fresh database
        if not await database_has_tables():
            logger.info("Fresh database detected. Creating initial schema...")
            await create_database_and_tables()
            logger.info("Database initialized.")
        else:
            # Database exists with tables - run migrations to update schema
            logger.info("Existing database detected. Running migrations...")
            run_migrations()
            logger.info("Migrations completed.")

    except Exception:
        logger.exception("Failed to initialize database schema.")

    yield

    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="FastAPI React App",
    description="A minimal FastAPI + React application stub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
environment = os.getenv("ENVIRONMENT", "DEV").upper()

if environment == "DEV":
    # In development, allow all origins
    cors_origins = ["*"]
else:
    # In production, restrict to specific domains
    cors_origins = [
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for .well-known directory (Microsoft Identity verification, etc.)
well_known_path = Path(__file__).parent.parent / ".well-known"
if well_known_path.exists():
    app.mount("/.well-known", StaticFiles(directory=str(well_known_path)), name="well-known")
    logger.info(f"Mounted .well-known directory at: {well_known_path}")

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(slack.router, prefix="/api")
app.include_router(telegram.router, prefix="/api")
app.include_router(discord.router, prefix="/api")
app.include_router(teams.router, prefix="/api")
app.include_router(cases.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
