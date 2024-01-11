from __future__ import annotations

import rich
import typer
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "example_app"
    environment: str = "dev"

    # gunicorn
    host: str = "127.0.0.1"
    port: int = 8000
    web_concurrency: int = 2

    # logging
    loguru_level: str = "debug"
    loguru_enqueue: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
app = typer.Typer()


@app.command()
def main(key: str) -> str:
    from .logger import get_logger

    logger = get_logger()

    try:
        value = getattr(settings, key.lower())
    except AttributeError:
        logger.warning("invalid settings key: {key}", key=key)
        return ""
    else:
        logger.debug("settings: {key} = {value}", key=key, value=value)
        rich.print(value)
        return value


if __name__ == "__main__":
    app()
