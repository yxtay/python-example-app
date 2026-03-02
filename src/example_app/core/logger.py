"""Application logging setup."""

from __future__ import annotations

import inspect
import logging

import loguru


class InterceptHandler(logging.Handler):
    """Handler that intercepts standard logging and redirects to loguru."""

    def __init__(self: InterceptHandler, depth: int = 0) -> None:
        super().__init__()
        self.depth = depth

    def emit(self: InterceptHandler, record: logging.LogRecord) -> None:
        """Emit a log record to loguru."""
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), self.depth
        while frame and (
            depth == self.depth or frame.f_code.co_filename == logging.__file__
        ):
            frame = frame.f_back
            depth += 1

        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def get_logger() -> loguru.Logger:
    """Get configured logger instance.

    Sets up uvicorn access and error loggers to use loguru.

    Returns:
        Configured loguru logger instance
    """
    for name in ["uvicorn.access", "uvicorn.error"]:
        if name in logging.root.manager.loggerDict:
            _logger = logging.getLogger(name)
            _logger.handlers = [InterceptHandler()]
            _logger.propagate = False

    return loguru.logger
