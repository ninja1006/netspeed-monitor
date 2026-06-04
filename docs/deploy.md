# Deployment Guide

Windows deployment for Network Speed Monitor v1.0.

## 1. Prerequisites

- Windows 10 or 11 (64-bit)
- Python 3.11+ with project venv (`venv\Scripts\python.exe`)
- **Administrator** rights for service install
- [NSSM](https://nssm.cc/) — install via `winget install NSSM.NSSM` or place `nssm.exe` in `scripts\nssm\`

## 2. First-time setup

From project root:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd frontend
npm install
```

## 3. Install poller as Windows service (production)

**Stop any manual poller** (`py -m backend.poller` in a terminal) before installing.

Do **not** set `SPEEDMON_DEV` on the service — production uses **3–5 minute** random intervals.

1. Open **Command Prompt or PowerShell as Administrator**
2. Run:

```bat
cd /d "D:\iroi-working\workplace\netspeed testing project"
scripts\install-service.bat
```

3. Verify:

```powershell
sc query SpeedMonPoller
Get-Content data\poller-service.log -Tail 15
```

Service name: **SpeedMonPoller**  
Log file: `data\poller-service.log`  
Database: `data\speedmon.db`

## 4. Run API and dashboard (manual, v1)

The service covers the **poller only**. Start API and UI when needed:

**API** — `scripts\run-api.bat` or:

```powershell
py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

**Dashboard**:

```powershell
cd frontend
npm run dev
```

Open http://127.0.0.1:5173

## 5. Uninstall service

Administrator CMD:

```bat
cd /d "D:\iroi-working\workplace\netspeed testing project"
scripts\uninstall-service.bat
```

Confirm removed: `sc query SpeedMonPoller` → service not found.

## 6. Post-deploy verification

- [x] `sc query SpeedMonPoller` → **RUNNING** (after install)
- [x] `sc qc SpeedMonPoller` → **START_TYPE: AUTO_START** (survives reboot)
- [x] `uninstall-service.bat` removes service cleanly (`sc query` → 1060)
- [x] `data\poller-service.log` shows `Sample saved` (production `dev_mode=False`)
- [ ] Reboot smoke test — run when convenient: after login, `sc query SpeedMonPoller` → RUNNING
- [ ] `GET http://127.0.0.1:8000/health` → `sample_count_24h` increases (API running)
- [ ] Dashboard charts show data for dates with samples

### Issue #9 sign-off (2026-06-05)

| Test | Result |
|------|--------|
| Install (`install-service.bat`) | Pass — SpeedMonPoller RUNNING |
| Uninstall (`uninstall-service.bat`) | Pass — service removed (sc 1060) |
| Re-install | Pass |
| Auto-start config | Pass — `SERVICE_AUTO_START` / `START_TYPE: 2 AUTO_START` |
| Adapter | Ethernet (physical), ~2–7 Mbps samples |
| Reboot | Pending next restart (config verified) |

## 7. Portable / USB mode

Copy the whole project folder (including `venv` and `data\speedmon.db`). Paths are relative to the install directory. Re-run `install-service.bat` on the target machine as Admin.

## 8. Release packaging

See [release-checklist.md](./release-checklist.md) and Issue #10 (PyInstaller + `speedmon-v1.0.0.zip`).
