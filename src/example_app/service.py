"""Service layer for business logic."""

from .repository import AbstractTaskRepository
from .schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


class TaskService:
    """Service layer for Task business logic."""

    def __init__(self, repository: AbstractTaskRepository) -> None:
        """Initialize service with repository.

        Args:
            repository: Task repository for data access
        """
        self.repository = repository

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """Create a new task.

        Args:
            task_data: Data for creating task

        Returns:
            Created task response
        """
        task = self.repository.create(task_data)
        return TaskResponse.model_validate(task)

    def get_task(self, task_id: int) -> TaskResponse | None:
        """Get task by ID.

        Args:
            task_id: ID of the task

        Returns:
            Task response or None if not found
        """
        task = self.repository.get_by_id(task_id)
        if not task:
            return None
        return TaskResponse.model_validate(task)

    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        completed: bool | None = None,
    ) -> TaskListResponse:
        """List all tasks with optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            completed: Filter by completion status if provided

        Returns:
            List of tasks with total count
        """
        tasks = self.repository.get_all(skip=skip, limit=limit, completed=completed)
        total = self.repository.count(completed=completed)

        return TaskListResponse(
            items=[TaskResponse.model_validate(task) for task in tasks],
            total=total,
        )

    def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse | None:
        """Update an existing task.

        Args:
            task_id: ID of the task to update
            task_data: Data for updating task

        Returns:
            Updated task response or None if not found
        """
        task = self.repository.update(task_id, task_data)
        if not task:
            return None
        return TaskResponse.model_validate(task)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(task_id)

    def mark_complete(self, task_id: int) -> TaskResponse | None:
        """Mark a task as complete.

        Args:
            task_id: ID of the task to mark complete

        Returns:
            Updated task response or None if not found
        """
        return self.update_task(task_id, TaskUpdate(completed=True))

    def mark_incomplete(self, task_id: int) -> TaskResponse | None:
        """Mark a task as incomplete.

        Args:
            task_id: ID of the task to mark incomplete

        Returns:
            Updated task response or None if not found
        """
        return self.update_task(task_id, TaskUpdate(completed=False))
