"""API routes for Task operations."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from example_app.dependencies import ServiceDep
from example_app.schemas import (
    MessageResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    task_data: TaskCreate,
    service: ServiceDep,
) -> TaskResponse:
    """Create a new task item.

    Args:
        task_data: Data for creating the task
        service: Task service from dependency injection

    Returns:
        Created task
    """
    return service.create_task(task_data)


@router.get(
    "",
    summary="List all tasks",
)
def list_tasks(
    service: ServiceDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Maximum number of records to return")
    ] = 100,
    completed: Annotated[
        bool | None, Query(description="Filter by completion status")
    ] = None,
) -> TaskListResponse:
    """List all tasks with optional filtering.

    Args:
        service: Task service from dependency injection
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        completed: Filter by completion status if provided

    Returns:
        List of tasks with total count
    """
    return service.list_tasks(skip=skip, limit=limit, completed=completed)


@router.get(
    "/{task_id}",
    summary="Get a task by ID",
)
def get_task(
    task_id: int,
    service: ServiceDep,
) -> TaskResponse:
    """Get a specific task by ID.

    Args:
        task_id: ID of the task to retrieve
        service: Task service from dependency injection

    Returns:
        Task details

    Raises:
        HTTPException: If task not found
    """
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.put(
    "/{task_id}",
    summary="Update a task",
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: ServiceDep,
) -> TaskResponse:
    """Update an existing task.

    Args:
        task_id: ID of the task to update
        task_data: Data for updating the task
        service: Task service from dependency injection

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found
    """
    task = service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.delete(
    "/{task_id}",
    summary="Delete a task",
)
def delete_task(
    task_id: int,
    service: ServiceDep,
) -> MessageResponse:
    """Delete a task.

    Args:
        task_id: ID of the task to delete
        service: Task service from dependency injection

    Returns:
        Success message

    Raises:
        HTTPException: If task not found
    """
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return MessageResponse(message=f"Task with id {task_id} deleted successfully")


@router.post(
    "/{task_id}/complete",
    summary="Mark task as complete",
)
def mark_complete(
    task_id: int,
    service: ServiceDep,
) -> TaskResponse:
    """Mark a task as complete.

    Args:
        task_id: ID of the task to mark complete
        service: Task service from dependency injection

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found
    """
    task = service.mark_complete(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post(
    "/{task_id}/incomplete",
    summary="Mark task as incomplete",
)
def mark_incomplete(
    task_id: int,
    service: ServiceDep,
) -> TaskResponse:
    """Mark a task as incomplete.

    Args:
        task_id: ID of the task to mark incomplete
        service: Task service from dependency injection

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found
    """
    task = service.mark_incomplete(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task
