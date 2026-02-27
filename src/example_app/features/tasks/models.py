"""Task data models."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task entity for database."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(..., max_length=200, index=True)
    description: str | None = Field(None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
