"""Speed measurement (stub — random fake metrics)."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class SpeedResult:
    download_mbps: float | None
    upload_mbps: float | None
    latency_ms: float | None


def run_speed_test(adapter_name: str) -> SpeedResult:
    """Stub: random Mbps and latency for development."""
    _ = adapter_name
    return SpeedResult(
        download_mbps=round(random.uniform(10.0, 100.0), 2),
        upload_mbps=round(random.uniform(5.0, 40.0), 2),
        latency_ms=round(random.uniform(10.0, 80.0), 2),
    )
