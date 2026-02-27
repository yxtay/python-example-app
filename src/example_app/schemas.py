"""Pydantic schemas for request/response models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """Base schema for Task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(
        None, max_length=1000, description="Task description"
    )
    completed: bool = Field(False, description="Completion status")


class TaskCreate(TaskBase):
    """Schema for creating a new Task."""


class TaskUpdate(BaseModel):
    """Schema for updating an existing Task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    completed: bool | None = None


class TaskResponse(TaskBase):
    """Schema for Task response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for list of Tasks response."""

    items: list[TaskResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
