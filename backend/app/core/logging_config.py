"""
Application logging configuration.

- Adds request_id into log records (via ContextVar).
- Local dev: colored key=value logs (human-friendly) to stderr.
- Server: JSON logs without ANSI sequences to stderr.
- Also writes to app.log in project root (rotating, 10MB x 5 files).
"""

import datetime
import json
import logging
import logging.handlers
import os
import pathlib
import sys
import typing as tp

from app.core import config as core_config
from app.core import request_context as request_context


_BUILTIN_RECORD_ATTRS: frozenset[str] = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }
)


_LOGS_DIR = pathlib.Path(__file__).parent.parent.parent / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _utc_now_iso() -> str:
    return datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec="milliseconds")


def _json_default(obj: tp.Any) -> str:
    return str(obj)


def _extract_extras(record: logging.LogRecord) -> dict[str, tp.Any]:
    extras: dict[str, tp.Any] = {}
    for key, value in record.__dict__.items():
        if key in _BUILTIN_RECORD_ATTRS:
            continue
        if key.startswith("_"):
            continue
        extras[key] = value
    return extras


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.request_id = request_context.get_request_id()
        record.service = core_config.settings.SERVICE_NAME
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, tp.Any] = {
            "ts": _utc_now_iso(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "service": getattr(record, "service", core_config.settings.SERVICE_NAME),
            "msg": record.getMessage(),
        }
        payload.update(_extract_extras(record))

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=_json_default)


class KeyValueFormatter(logging.Formatter):
    _RESET = "\x1b[0m"
    _COLORS: dict[str, str] = {
        "DEBUG": "\x1b[36m",  # cyan
        "INFO": "\x1b[32m",  # green
        "WARNING": "\x1b[33m",  # yellow
        "ERROR": "\x1b[31m",  # red
        "CRITICAL": "\x1b[35m",  # magenta
    }

    def __init__(self, *, color: bool) -> None:
        super().__init__()
        self._color = color

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        level = record.levelname
        if self._color:
            level = f"{self._COLORS.get(record.levelname, '')}{record.levelname}{self._RESET}"

        parts: list[str] = [
            f"ts={_utc_now_iso()}",
            f"level={level}",
            f"logger={record.name}",
            f"service={getattr(record, 'service', core_config.settings.SERVICE_NAME)}",
            f"request_id={getattr(record, 'request_id', '-')}",
            f"msg={json.dumps(record.getMessage(), ensure_ascii=False)}",
        ]

        for key, value in _extract_extras(record).items():
            parts.append(f"{key}={json.dumps(value, ensure_ascii=False, default=_json_default)}")

        if record.exc_info:
            parts.append(f"exc_info={json.dumps(self.formatException(record.exc_info), ensure_ascii=False)}")

        return " ".join(parts)


def setup_logging() -> None:
    """
    Configure root logging.

    Idempotent (safe to call multiple times).
    """
    settings = core_config.settings

    requested_level = (settings.LOG_LEVEL or "").strip().upper()
    if requested_level:
        level = getattr(logging, requested_level, logging.INFO)
    else:
        level = logging.DEBUG if settings.DEBUG else logging.INFO

    use_json = settings.LOG_JSON if settings.LOG_JSON is not None else (not settings.DEBUG)

    # Use stderr for logs (common convention) and colorize only when tty.
    stream = sys.stderr
    use_color_default = settings.DEBUG and stream.isatty()
    use_color = settings.LOG_COLOR if settings.LOG_COLOR is not None else use_color_default

    handler = logging.StreamHandler(stream=stream)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(JsonFormatter() if use_json else KeyValueFormatter(color=use_color))

    # Rotating file handler (always JSON, no colors, for debugging)
    file_handler = logging.handlers.RotatingFileHandler(
        _LOGS_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.addFilter(RequestIdFilter())
    file_handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler, file_handler]
    root.setLevel(level)

    # Use our handler/format for uvicorn, suppress access logs (we log in middleware).
    for name in ("uvicorn", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True
        logger.setLevel(level)

    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = []
    access_logger.propagate = True
    access_logger.setLevel(logging.WARNING)

