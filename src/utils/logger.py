"""
Logger setup for Modern EBook Reader.
Provides a configured logging.Logger with rotating file handler and rich formatting.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(log_path: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    """Set up application-wide logging.

    - Writes to ebook-reader.log in the current working directory by default
    - Rotates at ~5MB with up to 3 backups
    - Includes timestamp, level, module, function, and line number
    """
    logger = logging.getLogger("ebook_reader")
    if logger.handlers:
        # Already configured
        return logger

    logger.setLevel(level)

    # Determine log file path
    if log_path is None:
        log_path = Path.cwd() / "ebook-reader.log"

    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        str(log_path), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug("Logging initialized. Log file: %s", log_path)
    return logger

