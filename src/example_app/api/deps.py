"""Dependency injection for FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from example_app.db.session import get_session
from example_app.features.tasks.repository import TaskRepository
from example_app.features.tasks.service import TaskService

# Type aliases for dependency injection
SessionDep = Annotated[Session, Depends(get_session)]


def get_task_repository(session: SessionDep) -> TaskRepository:
    """Get Task repository instance.

    Args:
        session: Database session from dependency injection

    Returns:
        TaskRepository instance
    """
    return TaskRepository(session)


RepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]


def get_task_service(repository: RepositoryDep) -> TaskService:
    """Get Task service instance.

    Args:
        repository: Task repository from dependency injection

    Returns:
        TaskService instance
    """
    return TaskService(repository)


ServiceDep = Annotated[TaskService, Depends(get_task_service)]
