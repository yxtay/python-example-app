"""Task repository for data access."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlmodel import Session, select

from .models import Task
from .schemas import TaskCreate, TaskUpdate


class AbstractTaskRepository(ABC):
    """Abstract repository interface for Task operations."""

    @abstractmethod
    def create(self, task_data: TaskCreate) -> Task:
        """Create a new task."""

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None:
        """Get task by ID."""

    @abstractmethod
    def get_all(
        self, skip: int = 0, limit: int = 100, completed: bool | None = None
    ) -> list[Task]:
        """Get all tasks with optional filtering."""

    @abstractmethod
    def update(self, task_id: int, task_data: TaskUpdate) -> Task | None:
        """Update an existing task."""

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task."""

    @abstractmethod
    def count(self, completed: bool | None = None) -> int:
        """Count total tasks with optional filtering."""


class TaskRepository(AbstractTaskRepository):
    """Concrete repository implementation for Task operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create(self, task_data: TaskCreate) -> Task:
        """Create a new task.

        Args:
            task_data: Data for creating task

        Returns:
            Created task entity
        """
        task = Task.model_validate(task_data)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        """Get task by ID.

        Args:
            task_id: ID of the task

        Returns:
            Task entity or None if not found
        """
        return self.session.get(Task, task_id)

    def get_all(
        self, skip: int = 0, limit: int = 100, completed: bool | None = None
    ) -> list[Task]:
        """Get all tasks with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            completed: Filter by completion status if provided

        Returns:
            List of task entities
        """
        statement = select(Task)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        statement = statement.offset(skip).limit(limit).order_by(Task.created_at.desc())

        return list(self.session.exec(statement).all())

    def update(self, task_id: int, task_data: TaskUpdate) -> Task | None:
        """Update an existing task.

        Args:
            task_id: ID of the task to update
            task_data: Data for updating task

        Returns:
            Updated task entity or None if not found
        """
        task = self.session.get(Task, task_id)
        if not task:
            return None

        update_dict = task_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(task, key, value)

        task.updated_at = datetime.now(UTC)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if deleted, False if not found
        """
        task = self.session.get(Task, task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def count(self, completed: bool | None = None) -> int:
        """Count total tasks with optional filtering.

        Args:
            completed: Filter by completion status if provided

        Returns:
            Total count of tasks
        """
        statement = select(Task)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        return len(list(self.session.exec(statement).all()))
