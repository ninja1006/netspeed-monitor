"""FastAPI — serves aggregated speed data from SQLite."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.shared.db import init_db
from backend.shared import queries


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Network Speed Monitor API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_date_param(value: str, param: str) -> str:
    try:
        from datetime import date

        date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param}: use YYYY-MM-DD",
        ) from exc
    return value


@app.get("/health")
def health() -> dict:
    return queries.get_health_stats()


@app.get("/daily")
def daily(date_param: str = Query(..., alias="date")) -> dict:
    date_param = _parse_date_param(date_param, "date")
    result = queries.get_daily(date_param)
    if result is None:
        raise HTTPException(status_code=404, detail="no data")
    return result


@app.get("/week")
def week(end: str = Query(...)) -> dict:
    end = _parse_date_param(end, "end")
    return queries.get_week(end)


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

    if date_param:
        date_param = _parse_date_param(date_param, "date")
    if end:
        end = _parse_date_param(end, "end")

    try:
        result = queries.get_worst_times(
            period=period,
            date_str=date_param,
            end_str=end,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=404, detail="no data")
    return result
