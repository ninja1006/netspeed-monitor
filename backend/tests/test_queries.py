"""Tests for API aggregation queries."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.shared.db import init_db, insert_sample
from backend.shared import queries


def _seed_day(db: Path, day: str, downloads: list[float]) -> None:
    init_db(db)
    base = datetime.fromisoformat(f"{day}T12:00:00+00:00")
    for i, down in enumerate(downloads):
        insert_sample(
            adapter_name="Ethernet",
            download_mbps=down,
            upload_mbps=5.0,
            latency_ms=20.0 + i,
            ts=base + timedelta(minutes=i * 5),
            db_path=db,
        )


def test_get_daily_aggregates(tmp_path: Path) -> None:
    db = tmp_path / "q.db"
    _seed_day(db, "2026-06-02", [10.0, 30.0])
    result = queries.get_daily("2026-06-02", db_path=db)
    assert result is not None
    assert result["date"] == "2026-06-02"
    assert len(result["points"]) >= 1
    assert result["summary"]["min_download_mbps"] <= result["summary"]["max_download_mbps"]


def test_get_daily_no_data(tmp_path: Path) -> None:
    db = tmp_path / "empty.db"
    init_db(db)
    assert queries.get_daily("2099-01-01", db_path=db) is None


def test_get_worst_times_slowest_first(tmp_path: Path) -> None:
    db = tmp_path / "worst.db"
    init_db(db)
    day = "2026-06-02"
    # Slow window ~12:00 local (depends on TZ) — use explicit UTC times spread
    insert_sample(
        adapter_name="Ethernet",
        download_mbps=1.0,
        upload_mbps=1.0,
        latency_ms=100.0,
        ts=datetime(2026, 6, 2, 14, 5, tzinfo=timezone.utc),
        db_path=db,
    )
    insert_sample(
        adapter_name="Ethernet",
        download_mbps=50.0,
        upload_mbps=10.0,
        latency_ms=10.0,
        ts=datetime(2026, 6, 2, 14, 20, tzinfo=timezone.utc),
        db_path=db,
    )
    result = queries.get_worst_times(period="day", date_str=day, limit=3, db_path=db)
    assert result is not None
    windows = result["windows"]
    assert len(windows) >= 1
    if len(windows) >= 2:
        assert windows[0]["avg_download_mbps"] <= windows[1]["avg_download_mbps"]


def test_get_week_returns_seven_days(tmp_path: Path) -> None:
    db = tmp_path / "week.db"
    _seed_day(db, "2026-06-02", [20.0])
    result = queries.get_week("2026-06-02", db_path=db)
    assert len(result["days"]) == 7
