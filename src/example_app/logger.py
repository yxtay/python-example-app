from __future__ import annotations

import inspect
import logging

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


def get_logger() -> logger.__class__:
    for name in ["uvicorn.access", "uvicorn.error"]:
        if name in logging.root.manager.loggerDict:
            _logger = logging.getLogger(name)
            _logger.handlers = [InterceptHandler()]
            _logger.propagate = False

    return logger
