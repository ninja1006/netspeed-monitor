# Phase 1 — Task Tickets

Copy each section into GitHub Issues (or use `docs/tickets.md` as the sprint backlog until the remote repo exists).

**Sprint:** v1.0 — Days 2–6  
**Total tickets:** 10

---

## Ticket 1 — Repo skeleton & CI

| Field | Value |
|-------|-------|
| **Title** | `[PM] Repo skeleton, README, GitHub Actions CI` |
| **Role** | PM / DevOps |
| **Estimate** | 3h |
| **Phase** | 2 |

**Description:** Create folder structure (`backend/poller`, `backend/api`, `frontend`, `scripts`, `docs`), `.gitignore`, `README.md`, `CONTRIBUTING.md`, and `.github/workflows/ci.yml` (Python pytest + frontend build on PR).

**Acceptance criteria:**

- [ ] All directories exist per technical spec  
- [ ] `README` documents how to run poller, API, and UI  
- [ ] CI runs on pull request  

---

## Ticket 2 — SQLite schema & shared DB module

| Field | Value |
|-------|-------|
| **Title** | `[Backend] SQLite schema and shared db helper` |
| **Role** | Backend |
| **Estimate** | 1h |
| **Phase** | 2 |

**Description:** Add `backend/shared/schema.sql` and `db.py` with `init_db()` and `insert_sample()`.

**Acceptance criteria:**

- [ ] Schema matches technical spec  
- [ ] DB created under `data/speedmon.db` on init  
- [ ] Insert round-trip tested manually  

---

## Ticket 3 — Poller stub

| Field | Value |
|-------|-------|
| **Title** | `[Backend] Poller stub with fake data loop` |
| **Role** | Backend |
| **Estimate** | 2h |
| **Phase** | 2 |

**Description:** Stub `adapter_filter`, `speed_test`, and `poller` modules; write fake samples every 10s in dev mode.

**Acceptance criteria:**

- [ ] `python -m backend.poller` runs without error  
- [ ] Rows appear in `speed_samples`  

---

## Ticket 4 — VPN-aware adapter detection

| Field | Value |
|-------|-------|
| **Title** | `[Backend] Physical adapter detection (WMI + route fallback)` |
| **Role** | Backend |
| **Estimate** | 4h |
| **Phase** | 3 |

**Description:** Implement real adapter filtering per technical spec; handle no network and adapter removal.

**Acceptance criteria:**

- [ ] Unit tests for VPN/virtual name exclusion  
- [ ] Manual test with VPN active selects physical NIC  
- [ ] PM code review approved  

---

## Ticket 5 — Polling loop & real speed test

| Field | Value |
|-------|-------|
| **Title** | `[Backend] Poll loop (3–5 min) and speed measurement` |
| **Role** | Backend |
| **Estimate** | 4h |
| **Phase** | 3 |

**Description:** Random interval 180–300s; real speed test; error handling and rotating logs.

**Acceptance criteria:**

- [ ] Interval is random in range  
- [ ] Poller survives speed test failure  
- [ ] 24h run shows stable memory on VM  

---

## Ticket 6 — FastAPI endpoints

| Field | Value |
|-------|-------|
| **Title** | `[API] /daily, /week, /worst-times, /health` |
| **Role** | API Engineer |
| **Estimate** | 3h |
| **Phase** | 3–4 |

**Description:** Implement aggregation queries per API contract in technical spec.

**Acceptance criteria:**

- [ ] All endpoints match JSON contract  
- [ ] 15-minute worst-time buckets correct (unit test)  
- [ ] CORS enabled for local React dev  

---

## Ticket 7 — React dashboard

| Field | Value |
|-------|-------|
| **Title** | `[Frontend] Dashboard with 7 stacked charts + worst-times` |
| **Role** | Frontend |
| **Estimate** | 5h |
| **Phase** | 4 |

**Description:** Integrate Recharts; date picker; 60s auto-refresh; loading and error states.

**Acceptance criteria:**

- [ ] 7 stacked graphs render for `/week`  
- [ ] Daily chart and worst-times table work  
- [ ] Dashboard TTI &lt; 2s with seeded data  

---

## Ticket 8 — Integration & performance tests

| Field | Value |
|-------|-------|
| **Title** | `[QA] Integration and 24h soak test` |
| **Role** | DevOps/QA |
| **Estimate** | 4h |
| **Phase** | 4 |

**Description:** Seed script; poller → API → UI test; VPN VM validation; file bugs.

**Acceptance criteria:**

- [ ] E2E path verified on Windows VM  
- [ ] VPN accuracy documented  
- [ ] Bugs filed with repro steps  

---

## Ticket 9 — Windows service & install scripts

| Field | Value |
|-------|-------|
| **Title** | `[Backend] nssm service + install/uninstall bat` |
| **Role** | Backend / DevOps |
| **Estimate** | 2h |
| **Phase** | 5 |

**Acceptance criteria:**

- [ ] Service survives reboot  
- [ ] Uninstall removes service cleanly  

---

## Ticket 10 — PyInstaller package & release

| Field | Value |
|-------|-------|
| **Title** | `[DevOps] PyInstaller EXE + speedmon.zip + v1.0.0` |
| **Role** | DevOps/QA |
| **Estimate** | 4h |
| **Phase** | 5–6 |

**Acceptance criteria:**

- [ ] Portable run from USB on clean VM  
- [ ] `deploy.md` completed  
- [ ] Tag `v1.0.0` on main  

---

## Dependency graph

```
Ticket 1 → 2 → 3 → 4 → 5
              ↘ 6 ↗
                7
         8 (after 5,6,7)
         9 (after 5)
        10 (after 8,9)
```
