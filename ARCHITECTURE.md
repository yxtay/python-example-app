# Task API Architecture

This Task API follows **best practices** for FastAPI applications,
implementing a clean **repository pattern** with comprehensive
**dependency injection**.

## Architecture Overview

### Layered Architecture

```text
┌─────────────────────────────────────┐
│         API Layer (routes.py)       │  ← FastAPI endpoints
├─────────────────────────────────────┤
│      Service Layer (service.py)     │  ← Business logic
├─────────────────────────────────────┤
│   Repository Layer (repository.py)  │  ← Data access
├─────────────────────────────────────┤
│    Database Layer (database.py)     │  ← SQLModel/SQLite
└─────────────────────────────────────┘
```

### Key Components

#### 1. **Schemas** (`schemas.py`)

- Pydantic models for request/response validation
- `TodoCreate`, `TodoUpdate`, `TodoResponse`
- Type-safe data transfer objects

#### 2. **Entities** (`entities.py`)

- SQLModel database models
- `Todo` entity with SQLAlchemy mappings

#### 3. **Repository** (`repository.py`)

- Abstract repository interface (`AbstractTodoRepository`)
- Concrete implementation (`TodoRepository`)
- Encapsulates all database operations
- Follows repository pattern for testability

#### 4. **Service** (`service.py`)

- Business logic layer (`TodoService`)
- Uses repository through dependency injection
- Converts between entities and schemas

#### 5. **Routes** (`routes.py`)

- FastAPI endpoint definitions
- Uses service through dependency injection
- HTTP status codes and error handling

#### 6. **Dependencies** (`dependencies.py`)

- FastAPI dependency injection setup
- Type-annotated dependencies
- Automatic dependency resolution

#### 7. **Database** (`database.py`)

- Database connection and session management
- Table creation on startup
- Session factory for dependency injection

## Dependency Injection Flow

```python
# 1. Database Session
SessionDep = Annotated[Session, Depends(get_session)]

# 2. Repository (depends on Session)
RepositoryDep = Annotated[TaskRepository, Depends(get_task_repository)]

# 3. Service (depends on Repository)
ServiceDep = Annotated[TaskService, Depends(get_task_service)]

# 4. Route (depends on Service)
@router.post("")
def create_task(task_data: TaskCreate, service: ServiceDep):
    return service.create_task(task_data)
```

## API Endpoints

### Health Checks

- `GET /` - Health check
- `GET /readyz` - Readiness check
- `GET /livez` - Liveness check

### Todo Operations

- `POST /todos` - Create a new todo
- `GET /todos` - List all todos (with filtering & pagination)
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo
- `POST /todos/{id}/complete` - Mark todo as complete
- `POST /todos/{id}/incomplete` - Mark todo as incomplete

## Running the Application

### Development Mode

```bash
# Using Python module
python -m src.example_app.main

# Or with uvicorn directly
uvicorn example_app.main:app --reload
```

### Using Make

```bash
make run
```

### API Documentation

Once running, visit:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Example Usage

### Create a Todo

```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  }'
```

### List Todos

```bash
# All todos
curl "http://localhost:8000/todos"

# Only completed
curl "http://localhost:8000/todos?completed=true"

# With pagination
curl "http://localhost:8000/todos?skip=0&limit=10"
```

### Update a Todo

```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries - Updated",
    "completed": true
  }'
```

### Mark Complete

```bash
curl -X POST "http://localhost:8000/todos/1/complete"
```

### Delete a Todo

```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_app.py -v
```

## Best Practices Implemented

### 1. **Dependency Injection**

- All dependencies injected through FastAPI's DI system
- Easy to mock for testing
- Loose coupling between layers

### 2. **Repository Pattern**

- Abstract interface for data access
- Easy to swap implementations (SQLite → PostgreSQL)
- Testable without database

### 3. **Separation of Concerns**

- Each layer has single responsibility
- Business logic in service layer
- Data access in repository layer
- HTTP handling in routes layer

### 4. **Type Safety**

- Full type hints throughout
- Pydantic validation
- SQLModel for type-safe queries

### 5. **Error Handling**

- Proper HTTP status codes
- Descriptive error messages
- 404 for not found resources

### 6. **API Design**

- RESTful conventions
- Pagination support
- Filtering capabilities
- Proper HTTP methods

### 7. **Testing**

- Comprehensive test coverage
- Dependency override for testing
- In-memory SQLite for tests
- Test client for API testing

## Project Structure

```text
src/example_app/
├── __init__.py
├── main.py              # Application entry point
├── routes.py            # API endpoints
├── service.py           # Business logic
├── repository.py        # Data access layer
├── dependencies.py      # DI configuration
├── database.py          # Database setup
├── entities.py          # SQLModel entities
├── schemas.py           # Pydantic schemas
├── models.py            # Utility models
├── settings.py          # Configuration
└── logger.py            # Logging setup

tests/
├── test_app.py          # API tests
└── test_settings.py     # Settings tests
```

## Benefits of This Architecture

1. **Maintainability**: Clear separation makes code easy to understand and modify
2. **Testability**: Each layer can be tested independently
3. **Scalability**: Easy to add new features or swap implementations
4. **Type Safety**: Catches errors at development time
5. **Reusability**: Service and repository layers can be reused
6. **Flexibility**: Easy to switch databases or add caching
