# Technical Specification

## Network Speed Monitor v1.0

**Related:** [prd.md](./prd.md)  
**Last updated:** Phase 1

---

## 1. System Architecture

```
┌─────────────────┐     writes      ┌──────────────┐
│  Poller (EXE)   │ ──────────────► │   SQLite     │
│  Python/psutil  │                 │ speedmon.db  │
│  WMI + routes   │                 └──────┬───────┘
└─────────────────┘                        │
                                             │ reads
                                             ▼
┌─────────────────┐     REST        ┌──────────────┐
│ React Dashboard │ ◄────────────── │ FastAPI      │
│ Recharts        │                 │ uvicorn      │
└─────────────────┘                 └──────────────┘
```

| Component | Technology | Deployment |
|-----------|------------|------------|
| Poller | Python 3.11+, psutil, WMI, pywin32 | Windows Service (nssm) or EXE |
| API | FastAPI, uvicorn, aiosqlite | Same host, port 8000 default |
| Frontend | React, TypeScript, Recharts, axios | Static build served by API or local dev server |
| Database | SQLite 3 | `data/speedmon.db` (portable) |

---

## 2. Repository Layout (Phase 2+)

```
/
├── backend/
│   ├── poller/          # Adapter filter, speed test, poll loop
│   ├── api/             # FastAPI routes
│   └── shared/          # schema.sql, db helpers
├── frontend/            # React app
├── scripts/             # install.bat, nssm, seed data
├── data/                # Runtime DB (gitignored)
└── docs/
```

---

## 3. Data Model

### 3.1 Table: `speed_samples`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate key |
| `ts` | TEXT | NOT NULL | ISO 8601 UTC timestamp |
| `adapter_name` | TEXT | NOT NULL | Windows adapter name used for test |
| `download_mbps` | REAL | NULL allowed | Measured download |
| `upload_mbps` | REAL | NULL allowed | Measured upload |
| `latency_ms` | REAL | NULL allowed | RTT estimate |
| `is_physical` | INTEGER | NOT NULL DEFAULT 1 | 1 = physical, 0 = excluded/virtual |

**Indexes:**

- `idx_samples_ts` on `(ts)` — range queries for daily/weekly  

### 3.2 DDL (`backend/shared/schema.sql`)

```sql
CREATE TABLE IF NOT EXISTS speed_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    adapter_name TEXT NOT NULL,
    download_mbps REAL,
    upload_mbps REAL,
    latency_ms REAL,
    is_physical INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_samples_ts ON speed_samples(ts);
```

### 3.3 Sample retention

- v1.0: no automatic purge (disk growth ~ few MB/week at 3–5 min intervals)  
- v1.1: configurable retention days  

---

## 4. Poller Design

### 4.1 Adapter selection (VPN-aware)

1. **WMI** `Win32_NetworkAdapter`: enumerate adapters; exclude virtual types and name patterns (`TAP`, `TUN`, `WireGuard`, `OpenVPN`, `Hyper-V`, `vEthernet`, `VPN`, etc.).  
2. **Route table**: prefer interface associated with default route (`0.0.0.0/0`) that is not flagged virtual.  
3. **Fallback**: `psutil.net_io_counters(pernic=True)` — highest delta bytes on non-excluded names.

### 4.2 Polling loop

```
init_db()
loop forever:
    adapter = select_physical_adapter()
    if adapter is None:
        log warning; sleep 60; continue
    metrics = run_speed_test(adapter)
    insert_sample(metrics)
    sleep random.uniform(180, 300)  # 3–5 minutes
```

### 4.3 Speed test (v1 placeholder contract)

```python
@dataclass
class SpeedResult:
    download_mbps: float | None
    upload_mbps: float | None
    latency_ms: float | None
```

Implementation may use HTTP download timing against a configurable URL list.

### 4.4 Configuration (environment / `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SPEEDMON_DB_PATH` | `./data/speedmon.db` | SQLite file path |
| `SPEEDMON_LOG_PATH` | `./data/poller.log` | Rotating log file |
| `SPEEDMON_TEST_URL` | (TBD) | Download test endpoint |

---

## 5. API Specification

**Base URL:** `http://127.0.0.1:8000`  
**Format:** JSON  
**Auth:** None (localhost-only v1.0)

### 5.1 `GET /health`

**Purpose:** Liveness and last sample time for monitoring.

**Response 200:**

```json
{
  "status": "ok",
  "db_path": "data/speedmon.db",
  "last_sample_ts": "2026-05-29T12:34:56Z",
  "sample_count_24h": 288
}
```

---

### 5.2 `GET /daily`

**Query parameters:**

| Param | Required | Format | Description |
|-------|----------|--------|-------------|
| `date` | Yes | `YYYY-MM-DD` | Local calendar day for aggregation |

**Response 200:**

```json
{
  "date": "2026-05-29",
  "timezone": "local",
  "points": [
    {
      "minute": "00:00",
      "download_mbps": 42.1,
      "upload_mbps": 12.3,
      "latency_ms": 18.5,
      "sample_count": 1
    }
  ],
  "summary": {
    "avg_download_mbps": 38.2,
    "min_download_mbps": 5.1,
    "max_download_mbps": 95.0
  }
}
```

**Aggregation:** Average metrics grouped by `HH:MM` for all samples where `date(ts) = date` (local). Minutes with no samples omitted or returned with `null` (frontend choice — document in implementation).

---

### 5.3 `GET /week`

**Query parameters:**

| Param | Required | Format | Description |
|-------|----------|--------|-------------|
| `end` | Yes | `YYYY-MM-DD` | Last day of 7-day window (inclusive) |

**Response 200:**

```json
{
  "end": "2026-05-29",
  "days": [
    {
      "date": "2026-05-23",
      "points": [
        { "minute": "00:00", "download_mbps": 40.0, "upload_mbps": 10.0, "latency_ms": 20.0 }
      ]
    }
  ]
}
```

Returns exactly **7** day objects, oldest first.

---

### 5.4 `GET /worst-times`

**Query parameters:**

| Param | Required | Values | Description |
|-------|----------|--------|-------------|
| `period` | Yes | `day`, `week` | Aggregation scope |
| `date` | If `period=day` | `YYYY-MM-DD` | Target day |
| `end` | If `period=week` | `YYYY-MM-DD` | Week end date |
| `limit` | No | int, default `5` | Max windows to return |

**Response 200:**

```json
{
  "period": "day",
  "windows": [
    {
      "start": "2026-05-29T14:00:00",
      "end": "2026-05-29T14:15:00",
      "avg_download_mbps": 3.2,
      "avg_upload_mbps": 0.8,
      "avg_latency_ms": 85.0,
      "sample_count": 3
    }
  ]
}
```

**Aggregation:** Partition samples into **15-minute** buckets; rank by `avg_download_mbps` ascending (slowest first). Tie-breaker: higher `avg_latency_ms`.

---

### 5.5 Error responses

| Status | Body | When |
|--------|------|------|
| 400 | `{ "detail": "..." }` | Invalid date format |
| 404 | `{ "detail": "no data" }` | No samples in range |
| 500 | `{ "detail": "..." }` | DB failure |

---

## 6. Frontend Contract

| View | API | Component |
|------|-----|-----------|
| Daily graph | `GET /daily?date=` | `DailyChart` — single `LineChart` |
| Weekly stack | `GET /week?end=` | `WeekStack` — 7 `LineChart`s |
| Worst times | `GET /worst-times?period=` | `WorstTimesTable` |
| Status | `GET /health` | Header badge |

**Refresh:** Auto-refresh every 60s when dashboard is visible.  
**Date controls:** Date picker sets `date` / `end`; default = today.

---

## 7. Security & Deployment

- Bind API to `127.0.0.1` only in v1.0.  
- No secrets in repo; `.env` gitignored.  
- Portable mode: all paths relative to install directory.

---

## 8. Testing Strategy

| Layer | Tool | Focus |
|-------|------|-------|
| Unit | pytest | Adapter filter mocks, 15-min bucketing |
| Integration | pytest + TestClient | API + seeded DB |
| E2E | Manual / VM | VPN on, 24h soak, memory |
| CI | GitHub Actions | lint + test on PR |

---

## 9. Versioning

- API version prefix optional for v1 (`/v1/daily` deferred until breaking change).  
- Git tag `v1.0.0` at release.
