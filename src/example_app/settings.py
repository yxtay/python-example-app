from __future__ import annotations

import multiprocessing

import rich
import typer
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import get_logger


class Settings(BaseSettings):
    app_name: str = "example_app"
    environment: str = "dev"

    # gunicorn
    host: str = "127.0.0.1"  # devskim: ignore DS162092
    port: int = 8000
    web_concurrency: int = 2 * multiprocessing.cpu_count() + 1

    # loguru
    loguru_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
app = typer.Typer()


@app.command()
def main(key: str) -> str:
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
