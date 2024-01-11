from __future__ import annotations

import atexit
import inspect
import logging
import sys

import loguru
from loguru import logger


class InterceptHandler(logging.Handler):
    def __init__(self: InterceptHandler, depth: int = 0) -> None:
        super().__init__()
        self.depth = depth

    def emit(self: InterceptHandler, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), self.depth
        while frame and (
            depth == self.depth or frame.f_code.co_filename == logging.__file__
        ):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def get_logger() -> loguru.Logger:
    from .settings import settings

    logger.remove()
    logger.add(
        sys.stderr, level=settings.loguru_level.upper(), enqueue=settings.loguru_enqueue
    )
    logging.basicConfig(
        level=settings.loguru_level.upper(), handlers=[InterceptHandler()]
    )
    for name in ["uvicorn.access", "uvicorn.error"]:
        if name in logging.root.manager.loggerDict:
            _logger = logging.getLogger(name)
            _logger.handlers = [InterceptHandler()]
            _logger.propagate = False

    atexit.register(logger.complete)
    return logger
