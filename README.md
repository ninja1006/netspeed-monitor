# Network Speed Monitor

*Know your true speed, not your tunnel speed.*

Windows utility that measures internet speed on **physical network adapters** (VPN-aware) and visualizes trends via a React dashboard.

## Prerequisites

- Windows 10/11
- Python 3.11+ (`py --version`)
- Node.js 20+ (`node --version`) — for the dashboard

## Quick start

### 1. Python environment

```powershell
cd "D:\iroi-working\workplace\netspeed testing project"
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 2. Poller (VPN-aware + HTTP speed test)

Dev mode polls every **10 seconds**; production uses **3–5 minute** random intervals.

```powershell
$env:SPEEDMON_DEV = "1"
py -m backend.poller
```

Production (no `SPEEDMON_DEV`):

```powershell
py -m backend.poller
```

Optional env (see `.env.example`):

- `SPEEDMON_TEST_URL` — comma-separated download URLs  
- `SPEEDMON_TEST_MAX_BYTES` — cap bytes per sample (default 1 MiB)  
- `SPEEDMON_LOG_PATH` — rotating log file  

Database: `data/speedmon.db`

### 3. API (reads real data from SQLite)

```powershell
py -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  
- Daily: http://127.0.0.1:8000/daily?date=YYYY-MM-DD  

Run the poller first so `data/speedmon.db` has samples.

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### 5. Windows service (production poller)

Stop any manual poller first. Requires **Administrator** and [NSSM](https://nssm.cc/) (`winget install NSSM.NSSM`).

```bat
scripts\install-service.bat
```

Uses **3–5 min** intervals (no `SPEEDMON_DEV`). Logs: `data\poller-service.log`.  
Uninstall: `scripts\uninstall-service.bat` (Admin).  
Full details: [docs/deploy.md](docs/deploy.md)

## QA (Issue #8)

See [docs/integration-test.md](docs/integration-test.md) for E2E, VPN, and soak checklists.

```powershell
py scripts/seed_db.py --date 2026-06-04
py scripts/e2e_api_check.py --date 2026-06-04   # API must be running
```

## Project layout

```
backend/poller/    # Background sampling
backend/api/       # FastAPI
backend/shared/    # SQLite schema + db helpers
frontend/          # React + Recharts dashboard
docs/              # PRD, technical spec, tickets
scripts/           # install-service, uninstall-service, seed_db, run-*.bat
data/              # Runtime DB (gitignored)
```

## Documentation

See [docs/README.md](docs/README.md) for PRD, technical spec, and sprint tickets.

## License

Private / team project — see repository owner.
