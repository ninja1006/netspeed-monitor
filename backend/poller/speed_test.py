"""HTTP download speed test bound to a physical adapter when possible."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from backend.poller.adapter_filter import get_adapter_ipv4

logger = logging.getLogger(__name__)

DEFAULT_TEST_URLS: tuple[str, ...] = (
    "https://proof.ovh.net/files/1Mb.dat",
    "http://ipv4.download.thinkbroadband.com/5MB.zip",
)

DEFAULT_MAX_BYTES = 1_048_576  # 1 MiB cap per sample
DEFAULT_TIMEOUT = 60.0
DEV_TIMEOUT = 20.0


@dataclass
class SpeedResult:
    download_mbps: float | None
    upload_mbps: float | None
    latency_ms: float | None


def _test_urls() -> list[str]:
    raw = os.environ.get("SPEEDMON_TEST_URL", "").strip()
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return list(DEFAULT_TEST_URLS)


def _http_timeout() -> float:
    if os.environ.get("SPEEDMON_DEV", "").lower() in ("1", "true", "yes"):
        return DEV_TIMEOUT
    return DEFAULT_TIMEOUT


def _max_bytes() -> int:
    raw = os.environ.get("SPEEDMON_TEST_MAX_BYTES", "").strip()
    if raw.isdigit():
        return max(64_000, int(raw))
    if os.environ.get("SPEEDMON_DEV", "").lower() in ("1", "true", "yes"):
        return 256_000  # smaller cap in dev for faster feedback
    return DEFAULT_MAX_BYTES


def _make_client(bind_ip: str | None) -> httpx.Client:
    if bind_ip:
        transport = httpx.HTTPTransport(local_address=bind_ip)
        return httpx.Client(transport=transport, follow_redirects=True)
    return httpx.Client(follow_redirects=True)


def _measure_latency(client: httpx.Client, url: str) -> float | None:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}/"
    start = time.perf_counter()
    try:
        client.head(base, timeout=15.0)
        return round((time.perf_counter() - start) * 1000, 2)
    except Exception:
        try:
            client.get(url, timeout=15.0)
            return round((time.perf_counter() - start) * 1000, 2)
        except Exception:
            return None


def _measure_download_mbps(client: httpx.Client, url: str, max_bytes: int) -> float | None:
    start = time.perf_counter()
    nbytes = 0
    try:
        with client.stream("GET", url, timeout=_http_timeout()) as response:
            response.raise_for_status()
            for chunk in response.iter_bytes(chunk_size=64_000):
                nbytes += len(chunk)
                if nbytes >= max_bytes:
                    break
    except Exception as exc:
        logger.warning("Download test failed url=%s error=%s", url, exc)
        return None

    elapsed = time.perf_counter() - start
    if elapsed <= 0 or nbytes == 0:
        return None
    megabits = (nbytes * 8) / 1_000_000
    return round(megabits / elapsed, 2)


def run_speed_test(adapter_name: str) -> SpeedResult:
    """Run HTTP download + latency using adapter-bound client when IP is known."""
    bind_ip = get_adapter_ipv4(adapter_name)
    if bind_ip:
        logger.debug("Speed test bind ip=%s adapter=%s", bind_ip, adapter_name)
    else:
        logger.warning("No IPv4 for adapter %s; using default route", adapter_name)

    max_bytes = _max_bytes()
    download: float | None = None
    latency: float | None = None

    with _make_client(bind_ip) as client:
        for url in _test_urls():
            latency = _measure_latency(client, url) or latency
            download = _measure_download_mbps(client, url, max_bytes)
            if download is not None:
                break

    return SpeedResult(
        download_mbps=download,
        upload_mbps=None,
        latency_ms=latency,
    )
