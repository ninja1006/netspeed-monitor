"""Tests for shared database module."""

from pathlib import Path

from backend.shared.db import init_db, insert_sample


def test_init_and_insert(tmp_path: Path) -> None:
    db = tmp_path / "test.db"
    init_db(db)
    insert_sample(
        adapter_name="Ethernet",
        download_mbps=50.0,
        upload_mbps=10.0,
        latency_ms=20.0,
        db_path=db,
    )
    import sqlite3

    conn = sqlite3.connect(db)
    row = conn.execute("SELECT COUNT(*) FROM speed_samples").fetchone()
    conn.close()
    assert row is not None
    assert row[0] == 1
