"""Rotating file logging for the poller."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_poller_logging() -> Path:
    log_path = Path(os.environ.get("SPEEDMON_LOG_PATH", "./data/poller.log")).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console, file_handler],
        force=True,
    )

    return log_path
