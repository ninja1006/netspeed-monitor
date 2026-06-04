"""Smoke-check all API endpoints (Issue #8). API must be running on port 8000.

  py scripts/e2e_api_check.py
  py scripts/e2e_api_check.py --date 2026-06-04
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import date


def get(url: str) -> tuple[int, dict | list | str]:
    with urllib.request.urlopen(url, timeout=30) as resp:
        body = resp.read().decode()
        try:
            return resp.status, json.loads(body)
        except json.JSONDecodeError:
            return resp.status, body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    base = args.base.rstrip("/")
    day = args.date

    checks = [
        ("health", f"{base}/health"),
        ("daily", f"{base}/daily?date={day}"),
        ("week", f"{base}/week?end={day}"),
        ("worst-times", f"{base}/worst-times?period=day&date={day}&limit=3"),
    ]

    failed = 0
    for name, url in checks:
        try:
            status, data = get(url)
        except urllib.error.URLError as exc:
            print(f"FAIL {name}: {exc}")
            failed += 1
            continue

        if status != 200:
            print(f"FAIL {name}: HTTP {status}")
            failed += 1
            continue

        if name == "health" and isinstance(data, dict):
            ok = data.get("status") == "ok"
            print(
                f"OK   {name}: samples_24h={data.get('sample_count_24h')} "
                f"last={data.get('last_sample_ts')}"
            )
            if not ok:
                failed += 1
        elif name == "daily" and isinstance(data, dict):
            pts = len(data.get("points", []))
            print(f"OK   {name}: {pts} points, avg={data.get('summary', {}).get('avg_download_mbps')}")
            if pts == 0:
                print(f"     hint: run poller or: py scripts/seed_db.py --date {day}")
                failed += 1
        elif name == "week" and isinstance(data, dict):
            days = data.get("days", [])
            with_data = sum(1 for d in days if d.get("points"))
            print(f"OK   {name}: {len(days)} days, {with_data} with data")
        elif name == "worst-times" and isinstance(data, dict):
            wins = data.get("windows", [])
            print(f"OK   {name}: {len(wins)} windows")
            if not wins:
                failed += 1
        else:
            print(f"OK   {name}")

    if failed:
        print(f"\n{failed} check(s) failed.")
        return 1
    print("\nAll API checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
