"""FastAPI stub — mock JSON matching technical spec shapes."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.shared.db import get_db_path, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Network Speed Monitor API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_date(value: str, param: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {param}: use YYYY-MM-DD") from exc


def _mock_minute_points() -> list[dict]:
    points = []
    for hour in range(24):
        for minute in (0, 30):
            label = f"{hour:02d}:{minute:02d}"
            base = 40 + (hour % 6) * 5
            points.append(
                {
                    "minute": label,
                    "download_mbps": float(base + minute / 10),
                    "upload_mbps": float(10 + hour % 5),
                    "latency_ms": float(15 + hour % 10),
                    "sample_count": 1,
                }
            )
    return points


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "db_path": str(get_db_path()),
        "last_sample_ts": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_count_24h": 0,
    }


@app.get("/daily")
def daily(date_param: str = Query(..., alias="date")) -> dict:
    _parse_date(date_param, "date")
    points = _mock_minute_points()
    downloads = [p["download_mbps"] for p in points]
    return {
        "date": date_param,
        "timezone": "local",
        "points": points,
        "summary": {
            "avg_download_mbps": round(sum(downloads) / len(downloads), 2),
            "min_download_mbps": min(downloads),
            "max_download_mbps": max(downloads),
        },
    }


@app.get("/week")
def week(end: str = Query(...)) -> dict:
    end_d = _parse_date(end, "end")
    days = []
    for offset in range(6, -1, -1):
        d = end_d - timedelta(days=offset)
        days.append({"date": d.isoformat(), "points": _mock_minute_points()[:12]})
    return {"end": end, "days": days}


@app.get("/worst-times")
def worst_times(
    period: str = Query(...),
    date_param: str | None = Query(None, alias="date"),
    end: str | None = Query(None),
    limit: int = Query(5, ge=1, le=20),
) -> dict:
    if period not in ("day", "week"):
        raise HTTPException(status_code=400, detail="period must be 'day' or 'week'")
    if period == "day" and not date_param:
        raise HTTPException(status_code=400, detail="date is required when period=day")
    if period == "week" and not end:
        raise HTTPException(status_code=400, detail="end is required when period=week")

    windows = []
    for i in range(limit):
        start_h = 14 + i
        windows.append(
            {
                "start": f"2026-05-29T{start_h:02d}:00:00",
                "end": f"2026-05-29T{start_h:02d}:15:00",
                "avg_download_mbps": round(3.0 + i * 0.5, 2),
                "avg_upload_mbps": round(0.8 + i * 0.1, 2),
                "avg_latency_ms": round(85.0 + i * 5, 2),
                "sample_count": 3,
            }
        )
    return {"period": period, "windows": windows}
