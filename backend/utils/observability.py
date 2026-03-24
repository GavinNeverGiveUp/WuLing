import json
import logging
import os
from contextvars import ContextVar, Token
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore


_REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="-")


def _resolve_log_timezone():
    tz_name = os.getenv("LOG_TIMEZONE", "Asia/Shanghai")
    if ZoneInfo is not None:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            pass

    # Fallback to UTC+8 if zone database is unavailable.
    return timezone(timedelta(hours=8))


_LOG_TZ = _resolve_log_timezone()


def get_request_id() -> str:
    return _REQUEST_ID_CTX.get()


def bind_request_id(request_id: str) -> Token:
    return _REQUEST_ID_CTX.set(request_id)


def reset_request_id(token: Token) -> None:
    _REQUEST_ID_CTX.reset(token)


def _to_json_safe(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(_LOG_TZ).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", get_request_id()),
            "message": record.getMessage(),
        }

        extra_keys = [
            "method",
            "path",
            "status_code",
            "latency_ms",
            "client_ip",
            "username",
            "user_id",
            "db_host",
            "db_name",
            "limit",
            "result_count",
            "message_length",
            "credential_type",
            "token_preview",
            "log_file",
            "stage",
            "error_type",
            "error",
        ]

        for key in extra_keys:
            if hasattr(record, key):
                payload[key] = _to_json_safe(getattr(record, key))

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_fmms_observability_ready", False):
        return

    logs_dir = _project_root() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    formatter = JsonFormatter()
    request_filter = RequestContextFilter()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(request_filter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_filter)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger._fmms_observability_ready = True

    logging.getLogger(__name__).info(
        "observability_logging_ready",
        extra={"log_file": str(log_file)},
    )
