"""Centralized logging configuration for okgraphics.

Logs to both console (stderr) and a rotating file.
File location: ~/.local/share/okgraphics/logs/okgraphics.log
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_dir() -> Path:
    """Get the log directory, creating it if needed."""
    # Use XDG_DATA_HOME if set, otherwise ~/.local/share
    xdg_data = Path.home() / ".local" / "share"
    log_dir = xdg_data / "okgraphics" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3,
) -> logging.Logger:
    """Configure logging for okgraphics.

    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to log to a rotating file
        log_to_console: Whether to log to stderr
        max_bytes: Max size of each log file before rotation
        backup_count: Number of backup files to keep

    Returns:
        Root logger for okgraphics
    """
    logger = logging.getLogger("okgraphics")
    logger.setLevel(level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_to_file:
        log_dir = get_log_dir()
        log_file = log_dir / "okgraphics.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (e.g., "api", "cli", "generate").
              If None, returns the root okgraphics logger.

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"okgraphics.{name}")
    return logging.getLogger("okgraphics")
