"""Database session management."""

from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from example_app.core.config import settings
from example_app.features.tasks.models import Task  # noqa: F401

# Create database directory if it doesn't exist
DB_DIR = Path("data")
DB_DIR.mkdir(exist_ok=True)

# Database URL - SQLite for simplicity
DATABASE_URL = f"sqlite:///{DB_DIR}/tasks.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=settings.environment == "dev",
    connect_args={"check_same_thread": False},  # Needed for SQLite
)


def create_db_and_tables() -> None:
    """Create database tables.

    Initializes all tables for models that inherit from SQLModel.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session.

    This is a FastAPI dependency that provides a database session
    and ensures it's properly closed after use.

    Yields:
        Database session
    """
    with Session(engine) as session:
        yield session
