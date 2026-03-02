# Task API - Quick Start Guide

## Overview

This FastAPI application is a fully-featured Task API implementing clean
architecture with:

- **Repository Pattern** for data access abstraction
- **Dependency Injection** throughout the application
- **Layered Architecture** (Routes → Service → Repository → Database)
- **Type Safety** with Pydantic and SQLModel
- **Comprehensive Tests** with 85% code coverage

## Quick Start

### Run the Application

```bash
# Using uv (recommended)
uv run uvicorn example_app.main:app --reload

# Or using make
make run
```

The API will be available at <http://localhost:8000>

### API Documentation

Once running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## Example Usage

### Create a Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Study repository pattern and DI",
    "completed": false
  }'
```

### List All Tasks

```bash
curl "http://localhost:8000/tasks"
```

### Get a Specific Task

```bash
curl "http://localhost:8000/tasks/1"
```

### Update a Task

```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI - Updated",
    "completed": true
  }'
```

### Mark as Complete

```bash
curl -X POST "http://localhost:8000/tasks/1/complete"
```

### Filter by Status

```bash
# Only completed
curl "http://localhost:8000/tasks?completed=true"

# Only incomplete
curl "http://localhost:8000/tasks?completed=false"
```

### Delete a Task

```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_app.py -v
```

## Project Structure

```text
src/example_app/
├── main.py              # Application entry + lifespan management
├── routes.py            # API endpoints (HTTP layer)
├── service.py           # Business logic
├── repository.py        # Data access (Repository Pattern)
├── dependencies.py      # Dependency injection configuration
├── database.py          # Database session management
├── entities.py          # SQLModel database entities
├── schemas.py           # Pydantic request/response models
├── settings.py          # Application configuration
└── logger.py            # Logging setup
```

## Architecture Highlights

### Dependency Injection Chain

```text
Session → Repository → Service → Routes
```

Each layer is injected into the next using FastAPI's dependency injection system.

### Repository Pattern

- Abstract interface (`AbstractTaskRepository`)
- Concrete implementation (`TaskRepository`)
- Easy to mock for testing
- Database implementation can be swapped

### Service Layer

- Contains business logic
- Converts between entities and schemas
- Reusable across different interfaces (API, CLI, etc.)

## Features

✅ RESTful API endpoints  
✅ CRUD operations  
✅ Filtering and pagination  
✅ Input validation with Pydantic  
✅ Type safety throughout  
✅ SQLite database with SQLModel  
✅ Comprehensive test suite  
✅ 85% code coverage  
✅ Proper error handling  
✅ API documentation (Swagger + ReDoc)  
✅ Health check endpoints

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).
