"""Read aggregations from speed_samples for the API."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from statistics import mean

from backend.shared.db import _connect, get_db_path


def _parse_ts(ts_text: str) -> datetime:
    text = ts_text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


def _local_tz():
    return datetime.now().astimezone().tzinfo


def _local_day_bounds(target: date) -> tuple[str, str]:
    tz = _local_tz()
    start = datetime.combine(target, time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(target, time.max, tzinfo=tz).astimezone(timezone.utc)
    return (
        start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        end.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def _fetch_rows(
    conn: sqlite3.Connection,
    start_utc: str,
    end_utc: str,
) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT ts, download_mbps, upload_mbps, latency_ms
        FROM speed_samples
        WHERE ts >= ? AND ts <= ?
        ORDER BY ts
        """,
        (start_utc, end_utc),
    ).fetchall()


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(mean(values), 2)


def get_health_stats(db_path: Path | None = None) -> dict:
    path = db_path or get_db_path()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with _connect(path) as conn:
        row = conn.execute(
            """
            SELECT MAX(ts) AS last_ts, COUNT(*) AS cnt
            FROM speed_samples
            WHERE ts >= ?
            """,
            (cutoff,),
        ).fetchone()
    last_ts = row["last_ts"] if row and row["last_ts"] else None
    count = int(row["cnt"]) if row else 0
    return {
        "status": "ok",
        "db_path": str(path),
        "last_sample_ts": last_ts,
        "sample_count_24h": count,
    }


def get_daily(date_str: str, db_path: Path | None = None) -> dict | None:
    target = date.fromisoformat(date_str)
    start_utc, end_utc = _local_day_bounds(target)
    path = db_path or get_db_path()

    buckets: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"download": [], "upload": [], "latency": []}
    )

    with _connect(path) as conn:
        rows = _fetch_rows(conn, start_utc, end_utc)

    if not rows:
        return None

    for row in rows:
        local = _parse_ts(row["ts"]).astimezone()
        key = local.strftime("%H:%M")
        if row["download_mbps"] is not None:
            buckets[key]["download"].append(float(row["download_mbps"]))
        if row["upload_mbps"] is not None:
            buckets[key]["upload"].append(float(row["upload_mbps"]))
        if row["latency_ms"] is not None:
            buckets[key]["latency"].append(float(row["latency_ms"]))

    points = []
    downloads_for_summary: list[float] = []
    for minute in sorted(buckets.keys()):
        b = buckets[minute]
        down = _avg(b["download"])
        up = _avg(b["upload"])
        lat = _avg(b["latency"])
        count = max(len(b["download"]), len(b["upload"]), len(b["latency"]))
        if down is not None:
            downloads_for_summary.append(down)
        points.append(
            {
                "minute": minute,
                "download_mbps": down,
                "upload_mbps": up,
                "latency_ms": lat,
                "sample_count": count,
            }
        )

    if not downloads_for_summary:
        return None

    return {
        "date": date_str,
        "timezone": "local",
        "points": points,
        "summary": {
            "avg_download_mbps": round(mean(downloads_for_summary), 2),
            "min_download_mbps": round(min(downloads_for_summary), 2),
            "max_download_mbps": round(max(downloads_for_summary), 2),
        },
    }


def get_week(end_str: str, db_path: Path | None = None) -> dict:
    end_d = date.fromisoformat(end_str)
    days = []
    for offset in range(6, -1, -1):
        d = end_d - timedelta(days=offset)
        daily = get_daily(d.isoformat(), db_path=db_path)
        if daily:
            days.append({"date": d.isoformat(), "points": daily["points"]})
        else:
            days.append({"date": d.isoformat(), "points": []})
    return {"end": end_str, "days": days}


def _window_start_local(local_dt: datetime) -> datetime:
    slot = (local_dt.minute // 15) * 15
    return local_dt.replace(minute=slot, second=0, microsecond=0)


def get_worst_times(
    *,
    period: str,
    date_str: str | None = None,
    end_str: str | None = None,
    limit: int = 5,
    db_path: Path | None = None,
) -> dict | None:
    path = db_path or get_db_path()

    if period == "day":
        if not date_str:
            raise ValueError("date required")
        target = date.fromisoformat(date_str)
        start_utc, end_utc = _local_day_bounds(target)
    else:
        if not end_str:
            raise ValueError("end required")
        end_d = date.fromisoformat(end_str)
        start_d = end_d - timedelta(days=6)
        start_utc, _ = _local_day_bounds(start_d)
        _, end_utc = _local_day_bounds(end_d)

    windows: dict[datetime, dict[str, list[float]]] = defaultdict(
        lambda: {"download": [], "upload": [], "latency": []}
    )

    with _connect(path) as conn:
        rows = _fetch_rows(conn, start_utc, end_utc)

    if not rows:
        return None

    for row in rows:
        local = _parse_ts(row["ts"]).astimezone()
        start = _window_start_local(local)
        w = windows[start]
        if row["download_mbps"] is not None:
            w["download"].append(float(row["download_mbps"]))
        if row["upload_mbps"] is not None:
            w["upload"].append(float(row["upload_mbps"]))
        if row["latency_ms"] is not None:
            w["latency"].append(float(row["latency_ms"]))

    ranked = []
    for start, metrics in windows.items():
        down = _avg(metrics["download"])
        if down is None:
            continue
        end = start + timedelta(minutes=15)
        ranked.append(
            {
                "start": start.isoformat(timespec="seconds"),
                "end": end.isoformat(timespec="seconds"),
                "avg_download_mbps": down,
                "avg_upload_mbps": _avg(metrics["upload"]) or 0.0,
                "avg_latency_ms": _avg(metrics["latency"]) or 0.0,
                "sample_count": max(
                    len(metrics["download"]),
                    len(metrics["upload"]),
                    len(metrics["latency"]),
                ),
                "_sort_latency": _avg(metrics["latency"]) or 0.0,
            }
        )

    # Slowest download first; tie-break with higher latency
    ranked.sort(key=lambda w: (w["avg_download_mbps"], -w["_sort_latency"]))

    for w in ranked:
        w.pop("_sort_latency", None)

    return {
        "period": period,
        "windows": ranked[:limit],
    }
