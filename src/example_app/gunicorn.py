from __future__ import annotations

import logging
from typing import ClassVar

import gunicorn.app.wsgiapp
import uvicorn.workers
from gunicorn import config, glogging

from .logger import InterceptHandler, get_logger
from .settings import settings


class GunicornLogger(glogging.Logger):
    def __init__(self: GunicornLogger, cfg: config.Config) -> None:
        super().__init__(cfg)

        get_logger()
        for name in ["gunicorn.error", "gunicorn.access"]:
            logging.getLogger(name).handlers = [InterceptHandler(depth=1)]


class UvicornWorker(uvicorn.workers.UvicornWorker):
    CONFIG_KWARGS: ClassVar[dict[str, str]] = {"loop": "asyncio", "http": "auto"}


class Application(gunicorn.app.wsgiapp.WSGIApplication):
    def __init__(self: Application, options: dict[str, str] | None = None) -> None:
        defaults = {
            "wsgi_app": f"{settings.app_name}.main:app",
            "bind": f"{settings.host}:{settings.port}",
            "logger_class": f"{settings.app_name}.gunicorn.GunicornLogger",
            "workers": settings.web_concurrency,
            "worker_class": f"{settings.app_name}.gunicorn.UvicornWorker",
        }
        self.options = defaults | (options or {})
        super().__init__("%(prog)s [OPTIONS] [APP_MODULE]", prog="gunicorn")

    def load_config(self: Application) -> None:
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)
        super().load_config()


if __name__ == "__main__":
    options = {"reload": "true"}
    Application(options).run()
