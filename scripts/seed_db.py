"""Seed speedmon.db with sample rows for API/dashboard QA (Issue #8).

Run from repo root:
  py scripts/seed_db.py
  py scripts/seed_db.py --date 2026-06-04 --samples-per-hour 12
"""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.shared.db import get_db_path, init_db, insert_sample  # noqa: E402


def seed_day(
    target: date,
    *,
    samples_per_hour: int,
    db_path: Path,
    adapter: str = "Ethernet",
) -> int:
    if samples_per_hour < 1:
        raise ValueError("samples_per_hour must be >= 1")

    interval_minutes = max(1, 60 // samples_per_hour)
    tz = datetime.now().astimezone().tzinfo
    start = datetime.combine(target, datetime.min.time(), tzinfo=tz)
    end = start + timedelta(days=1) - timedelta(seconds=1)

    count = 0
    when = start
    while when <= end:
        download = round(random.uniform(1.5, 25.0), 2)
        upload = round(random.uniform(0.5, 8.0), 2)
        latency = round(random.uniform(10.0, 120.0), 2)
        insert_sample(
            adapter_name=adapter,
            download_mbps=download,
            upload_mbps=upload,
            latency_ms=latency,
            ts=when,
            db_path=db_path,
        )
        count += 1
        when += timedelta(minutes=interval_minutes)

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed SQLite with test speed samples")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Local calendar day to seed (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of consecutive days ending on --date",
    )
    parser.add_argument(
        "--samples-per-hour",
        type=int,
        default=12,
        help="Rough samples per hour (spaced evenly)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Database path (default: SPEEDMON_DB_PATH or data/speedmon.db)",
    )
    parser.add_argument(
        "--reset-day",
        action="store_true",
        help="Delete existing samples for each seeded day before insert",
    )
    args = parser.parse_args()

    end_day = date.fromisoformat(args.date)
    db_path = Path(args.db).resolve() if args.db else get_db_path()
    init_db(db_path)

    total = 0
    for offset in range(args.days - 1, -1, -1):
        day = end_day - timedelta(days=offset)
        if args.reset_day:
            start_utc = datetime.combine(
                day, datetime.min.time(), tzinfo=datetime.now().astimezone().tzinfo
            ).astimezone(timezone.utc)
            end_utc = datetime.combine(
                day, datetime.max.time(), tzinfo=datetime.now().astimezone().tzinfo
            ).astimezone(timezone.utc)
            import sqlite3

            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "DELETE FROM speed_samples WHERE ts >= ? AND ts <= ?",
                    (
                        start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                )
                conn.commit()

        n = seed_day(
            day,
            samples_per_hour=args.samples_per_hour,
            db_path=db_path,
        )
        total += n
        print(f"Seeded {n} samples for {day.isoformat()}")

    print(f"Done. {total} rows in {db_path}")


if __name__ == "__main__":
    main()
