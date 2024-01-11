from fastapi import FastAPI

from .logger import get_logger
from .models import Ok
from .settings import settings


def fastapi_app() -> FastAPI:
    app = FastAPI()

    @app.get("/readyz")
    @app.get("/livez")
    @app.get("/")
    async def ok() -> Ok:
        return Ok()

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
        log_config=None,
    )
