"""Tests for the Task API application."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from example_app import main
from example_app.database import get_session


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database session."""

    def get_session_override():
        return session

    app = main.fastapi_app()
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def test_app_creation() -> None:
    """Test that the FastAPI app can be created."""
    app = main.fastapi_app()
    assert app is not None
    assert app.title == "Task API"


def test_health_check(client: TestClient) -> None:
    """Test health check endpoints."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "ok"

    response = client.get("/readyz")
    assert response.status_code == 200

    response = client.get("/livez")
    assert response.status_code == 200


def test_create_task(client: TestClient) -> None:
    """Test creating a task."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
    }

    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_list_tasks(client: TestClient) -> None:
    """Test listing tasks."""
    # Create a task first
    client.post("/tasks", json={"title": "Test Task", "completed": False})

    response = client.get("/tasks")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0


def test_get_task(client: TestClient) -> None:
    """Test getting a specific task."""
    # Create a task first
    create_response = client.post("/tasks", json={"title": "Test Task"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


def test_get_nonexistent_task(client: TestClient) -> None:
    """Test getting a nonexistent task."""
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task(client: TestClient) -> None:
    """Test updating a task."""
    # Create a task first
    create_response = client.post("/tasks", json={"title": "Original Title"})
    task_id = create_response.json()["id"]

    # Update it
    update_data = {"title": "Updated Title", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True


def test_delete_task(client: TestClient) -> None:
    """Test deleting a task."""
    # Create a task first
    create_response = client.post("/tasks", json={"title": "To Delete"})
    task_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_mark_complete(client: TestClient) -> None:
    """Test marking a task as complete."""
    # Create a task first
    create_response = client.post("/tasks", json={"title": "To Complete"})
    task_id = create_response.json()["id"]

    # Mark it complete
    response = client.post(f"/tasks/{task_id}/complete")
    assert response.status_code == 200

    data = response.json()
    assert data["completed"] is True


def test_mark_incomplete(client: TestClient) -> None:
    """Test marking a task as incomplete."""
    # Create a completed task
    create_response = client.post(
        "/tasks", json={"title": "Completed", "completed": True}
    )
    task_id = create_response.json()["id"]

    # Mark it incomplete
    response = client.post(f"/tasks/{task_id}/incomplete")
    assert response.status_code == 200

    data = response.json()
    assert data["completed"] is False


def test_filter_by_completed(client: TestClient) -> None:
    """Test filtering tasks by completion status."""
    # Create completed and incomplete tasks
    client.post("/tasks", json={"title": "Incomplete", "completed": False})
    client.post("/tasks", json={"title": "Complete", "completed": True})

    # Filter for completed
    response = client.get("/tasks?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert all(item["completed"] for item in data["items"])

    # Filter for incomplete
    response = client.get("/tasks?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert all(not item["completed"] for item in data["items"])
