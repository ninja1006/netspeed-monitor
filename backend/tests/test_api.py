"""FastAPI integration tests with seeded SQLite."""

from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.shared.db import init_db, insert_sample


def test_api_daily_and_health(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "api.db"
    monkeypatch.setenv("SPEEDMON_DB_PATH", str(db))
    init_db(db)
    now = datetime.now().astimezone()
    today = now.date().isoformat()
    insert_sample(
        adapter_name="Ethernet",
        download_mbps=25.0,
        upload_mbps=5.0,
        latency_ms=15.0,
        ts=now,
        db_path=db,
    )

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["sample_count_24h"] >= 1

        daily = client.get("/daily", params={"date": today})
        assert daily.status_code == 200
        body = daily.json()
        assert body["date"] == today
        assert len(body["points"]) >= 1

        missing = client.get("/daily", params={"date": "2099-01-01"})
        assert missing.status_code == 404
