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

### 2. Poller (stub — fake data)

Dev mode polls every **10 seconds**:

```powershell
$env:SPEEDMON_DEV = "1"
py -m backend.poller
```

Database: `data/speedmon.db`

### 3. API

```powershell
py -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Project layout

```
backend/poller/    # Background sampling
backend/api/       # FastAPI
backend/shared/    # SQLite schema + db helpers
frontend/          # React + Recharts dashboard
docs/              # PRD, technical spec, tickets
scripts/           # Install / deploy helpers (Phase 5)
data/              # Runtime DB (gitignored)
```

## Documentation

See [docs/README.md](docs/README.md) for PRD, technical spec, and sprint tickets.

## License

Private / team project — see repository owner.
