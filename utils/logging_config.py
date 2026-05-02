import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging(app) -> None:
    """Configure application logging.

    Production: rotating file handler in logs/app.log + stderr.
    Development/testing: single stderr handler at DEBUG/INFO.
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT)

    for handler in list(app.logger.handlers):
        app.logger.removeHandler(handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    app.logger.addHandler(stream_handler)

    if app.config.get("ENV") == "production":
        log_dir = Path(os.getenv("LOG_DIR", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024)),
            backupCount=int(os.getenv("LOG_BACKUP_COUNT", 5)),
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(level)
    app.logger.propagate = False
