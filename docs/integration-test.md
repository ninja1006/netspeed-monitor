# Integration & QA Guide (Issue #8)

Use this checklist before closing GitHub issue **#8**.

## 1. Automated helpers

From repo root with venv activated:

```bash
source venv/Scripts/activate

# Optional: seed a day of data (no poller wait)
py scripts/seed_db.py --date $(date +%Y-%m-%d) --samples-per-hour 12

# Terminal A — API
py -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000

# Terminal B — API smoke (all four endpoints)
py scripts/e2e_api_check.py --date YYYY-MM-DD
```

Expect: `All API checks passed.`

## 2. Full E2E (poller → API → UI)

| Step | Terminal | Command |
|------|----------|---------|
| 1 | Poller | `export SPEEDMON_DEV=1` then `py -m backend.poller` |
| 2 | API | `py -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000` |
| 3 | UI | `cd frontend && npm run dev` |

Verify in browser (http://127.0.0.1:5173):

- [ ] Health shows **ok** and sample count increases
- [ ] **Daily** chart has points for selected date
- [ ] **Week** shows 7 stacked days (empty days OK if no data)
- [ ] **Worst times** table has rows when data exists
- [ ] Date picker changes data without errors

Record result in the table below.

## 3. VPN accuracy (physical adapter)

1. Note adapter **without** VPN: poller log should show e.g. `Ethernet`.
2. Connect VPN (if available).
3. Restart poller; confirm log still selects **physical** adapter (not TAP/TUN/OpenVPN/WireGuard name).
4. Speeds should reflect physical path (~your real ISP), not VPN tunnel-only NIC.

Document in [known-issues.md](./known-issues.md) § VPN validation.

If no VPN available: note *"VPN test skipped — no VPN on test machine"* in issue #8 comment.

## 4. 24-hour soak (optional but recommended)

Production interval (no dev flag):

```bash
# Stop SPEEDMON_DEV poller first
py -m backend.poller
```

Leave running **≥ 24 hours**. Then:

- [ ] Poller still running (no crash)
- [ ] `GET /health` → `sample_count_24h` > 0, recent `last_sample_ts`
- [ ] Memory stable (Task Manager — informal check)

## 5. File bugs

Any failure → new GitHub issue with:

- Steps to reproduce
- Expected vs actual
- Log snippet (`data/poller.log`) or screenshot

## 6. Close issue #8

Comment example:

```text
Issue #8 QA complete:
- E2E poller → API → dashboard verified on Windows
- scripts/seed_db.py + scripts/e2e_api_check.py added
- VPN validation documented in docs/known-issues.md
- pytest 16/16, CI green on main
```

## E2E sign-off

| Test | Date | Tester | Pass? |
|------|------|--------|-------|
| API smoke (`e2e_api_check.py`) | 2026-06-05 | ninja1006 | Yes |
| 3-terminal UI E2E | 2026-06-05 | ninja1006 | Yes |
| VPN adapter selection | 2026-06-05 | ninja1006 | Yes (no VPN); physical NIC verified |
| 24h soak | — | — | Skipped (optional for v1 QA) |
