import json
import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler

# own imports
from depsight.utils.constants import (
    LOG_BACKUP_COUNT,
    LOG_DATE_FORMAT,
    LOG_FILE_NAME,
    LOG_FORMAT,
    LOG_JSONL_FILE_NAME,
    LOG_LEVEL,
    LOG_MAX_BYTES,
    USER_LOG_DIR,
)

class _JsonlFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)



def setup_logging(
    *,
    level: int = LOG_LEVEL,
    log_dir: Path | None = None,
    log_file: str = LOG_FILE_NAME,
) -> None:
    """Configure handlers on the root `depsight` logger.

    Call this **once** at application startup (e.g. inside the dispatcher).
    Every module that does `logging.getLogger(__name__)` under the
    `depsight` package will automatically inherit these handlers.

    Parameters
    ----------
    level:
        The minimum logging level (default: `LOG_LEVEL` / `INFO`).
    log_dir:
        Directory for log files.  Defaults to `USER_LOG_DIR`.
    log_file:
        Name of the log file inside *log_dir*.
    """
    root = logging.getLogger("depsight")

    # Avoid adding duplicate handlers when called multiple times
    if root.handlers:
        root.setLevel(level)
        return

    root.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # File handler (rotating)
    # NOTE: No console handler — stdout/stderr are owned by the Textual
    # TUI and writing to them would corrupt the terminal UI.
    log_path = (log_dir or USER_LOG_DIR) / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # JSONL file handler (rotating)
    jsonl_path = (log_dir or USER_LOG_DIR) / LOG_JSONL_FILE_NAME
    jsonl_handler = RotatingFileHandler(
        jsonl_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    jsonl_handler.setLevel(logging.DEBUG)
    jsonl_handler.setFormatter(_JsonlFormatter())
    root.addHandler(jsonl_handler)