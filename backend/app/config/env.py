"""Environment configuration loader."""
import os
from pathlib import Path
from dotenv import load_dotenv


def load_project_env() -> Path:
    """
    Load environment variables from .env file in project root.

    Returns:
        Path to the loaded .env file
    """
    # Navigate from backend/app/config/env.py up to project root
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[3]  # Go up 3 levels: config -> app -> backend -> root

    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        return env_file
    else:
        # Fall back to searching parent directories
        search_dir = current_file.parent
        for _ in range(10):  # Search up to 10 levels
            candidate = search_dir / ".env"
            if candidate.exists():
                load_dotenv(candidate)
                return candidate
            search_dir = search_dir.parent

        # No .env file found, continue with system environment
        return Path()


# Load environment variables when module is imported
load_project_env()
