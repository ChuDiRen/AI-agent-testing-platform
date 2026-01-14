"""
API Automation Agent Platform - Database Management

This module handles database connection, initialization, and migrations.
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from typing import Generator
import os

# Import settings from api_agent package
import sys
from pathlib import Path

# Add parent directory to path to import settings
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api_agent import settings  # type: ignore

from ..models import (
    TaskDB, SessionDB, DocumentDB, TestSuiteDB, TestExecutionDB
)


# Create engine
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug
    )
else:
    engine = create_engine(
        settings.database_url,
        echo=settings.debug
    )


def init_db() -> None:
    """
    Initialize database by creating all tables.
    This function creates all tables defined in models.
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(settings.database_url.replace("sqlite:///", "")), exist_ok=True)

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.
    This is used by FastAPI Depends() to get a session for each request.
    """
    with Session(engine) as session:
        yield session


def drop_all_tables() -> None:
    """
    Drop all tables. Use with caution!
    This is primarily used for testing.
    """
    SQLModel.metadata.drop_all(engine)


# Export for convenience
__all__ = [
    "engine",
    "init_db",
    "get_session",
    "drop_all_tables",
]
