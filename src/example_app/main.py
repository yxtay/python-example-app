from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_db_and_tables
from .logger import get_logger
from .models import Ok
from .routes import router as task_router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events for the application.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    get_logger().info("Starting up application")
    create_db_and_tables()
    get_logger().info("Database tables created")

    yield

    # Shutdown
    get_logger().info("Shutting down application")


def fastapi_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Task API",
        description="A simple Task API following repository pattern with dependency injection",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Health check endpoints
    @app.get("/readyz", tags=["health"])
    @app.get("/livez", tags=["health"])
    @app.get("/", tags=["health"])
    async def health_check() -> Ok:
        """Health check endpoint."""
        return Ok()

    # Include routers
    app.include_router(task_router)

    return app


get_logger()
app = fastapi_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=f"{settings.app_name}.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
