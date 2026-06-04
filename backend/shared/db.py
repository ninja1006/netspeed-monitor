"""SQLite helpers for speed samples."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def get_db_path() -> Path:
    raw = os.environ.get("SPEEDMON_DB_PATH", "./data/speedmon.db")
    return Path(raw).resolve()


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = db_path or get_db_path()
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    with _connect(path) as conn:
        conn.executescript(schema)
        conn.commit()
    return path


def insert_sample(
    *,
    adapter_name: str,
    download_mbps: float | None,
    upload_mbps: float | None,
    latency_ms: float | None,
    is_physical: bool = True,
    ts: datetime | None = None,
    db_path: Path | None = None,
) -> None:
    path = db_path or get_db_path()
    when = ts or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    else:
        when = when.astimezone(timezone.utc)
    ts_text = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    with _connect(path) as conn:
        conn.execute(
            """
            INSERT INTO speed_samples
                (ts, adapter_name, download_mbps, upload_mbps, latency_ms, is_physical)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                ts_text,
                adapter_name,
                download_mbps,
                upload_mbps,
                latency_ms,
                1 if is_physical else 0,
            ),
        )
        conn.commit()
