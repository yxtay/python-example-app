from __future__ import annotations

import logging

import gunicorn.app.wsgiapp
from gunicorn import config, glogging

from .logger import InterceptHandler, get_logger
from .settings import settings


class GunicornLogger(glogging.Logger):
    def __init__(self: GunicornLogger, cfg: config.Config) -> None:
        super().__init__(cfg)

        get_logger()
        for name in ["gunicorn.error", "gunicorn.access"]:
            logging_logger = logging.getLogger(name)
            logging_logger.handlers = [InterceptHandler(depth=1)]


class Application(gunicorn.app.wsgiapp.WSGIApplication):
    def __init__(self: Application) -> None:
        self.options = {
            "wsgi_app": f"{settings.app_name}.main:app",
            "bind": f"{settings.host}:{settings.port}",
            "worker_class": "uvicorn.workers.UvicornWorker",
            "logger_class": f"{settings.app_name}.gunicorn.GunicornLogger",
            "reload": True,
        }
        super().__init__()

    def load_config(self: Application) -> None:
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

        super().load_config()


if __name__ == "__main__":
    Application().run()
