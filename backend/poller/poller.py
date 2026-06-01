"""Poll loop: adapter → speed test → SQLite."""

from __future__ import annotations

import logging
import os
import random
import time

from backend.poller.adapter_filter import select_physical_adapter
from backend.poller.logging_config import setup_poller_logging
from backend.poller.speed_test import run_speed_test
from backend.shared.db import init_db, insert_sample

logger = logging.getLogger(__name__)


def _sleep_seconds() -> float:
    if os.environ.get("SPEEDMON_DEV", "").lower() in ("1", "true", "yes"):
        return 10.0
    return random.uniform(180, 300)


def _retry_sleep_seconds() -> float:
    return 60.0


def run_once() -> bool:
    logger.info("Selecting physical network adapter...")
    adapter = select_physical_adapter()
    if adapter is None:
        logger.warning("No physical adapter found; skipping sample")
        return False
    logger.info("Running speed test on adapter=%s (may take up to 60s)...", adapter)
    result = run_speed_test(adapter)
    insert_sample(
        adapter_name=adapter,
        download_mbps=result.download_mbps,
        upload_mbps=result.upload_mbps,
        latency_ms=result.latency_ms,
    )
    logger.info(
        "Sample saved adapter=%s down=%.2f Mbps up=%.2f Mbps latency=%.2f ms",
        adapter,
        result.download_mbps or 0,
        result.upload_mbps or 0,
        result.latency_ms or 0,
    )
    return True


def main() -> None:
    print("Network Speed Monitor — poller starting (Ctrl+C to stop)...", flush=True)
    log_path = setup_poller_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    db_path = init_db()
    logger.info(
        "Poller started db=%s log=%s dev_mode=%s",
        db_path,
        log_path,
        bool(os.environ.get("SPEEDMON_DEV")),
    )
    while True:
        try:
            if not run_once():
                time.sleep(_retry_sleep_seconds())
                continue
        except Exception:
            logger.exception("Poll iteration failed")
        time.sleep(_sleep_seconds())


if __name__ == "__main__":
    main()
