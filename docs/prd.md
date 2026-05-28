# Product Requirements Document (PRD)

## Network Speed Monitor

**Version:** 1.0.0  
**Status:** Draft — Phase 1  
**Tagline:** *Know your true speed, not your tunnel speed.*

---

## 1. Executive Summary

Network Speed Monitor is a lightweight, **Windows-only** utility that measures real internet performance on **physical network adapters**, bypassing VPN tunnels. It collects continuous speed samples and surfaces trends through a dashboard so users can identify the worst times of day or week for connectivity.

---

## 2. Problem Statement

Corporate and consumer VPNs route traffic through encrypted tunnels. Standard speed tests often reflect **tunnel** performance, not the underlying ISP or Wi-Fi link. Users cannot tell whether slowdowns come from:

- ISP congestion or throttling  
- Wi-Fi interference or dead zones  
- VPN overhead or misconfiguration  

This product monitors **physical adapters directly** (WMI + route analysis) so measurements reflect true local link quality even when a VPN is active.

---

## 3. Goals & Non-Goals

### Goals (v1.0)

- Continuous background sampling with VPN-aware adapter selection  
- Daily (24h) and weekly (7-day) visualizations  
- Worst-time analysis (15-minute windows)  
- Portable deployment (single-folder or USB)  
- Low resource footprint suitable for 24/7 operation  

### Non-Goals (v1.0)

- macOS / Linux support  
- Mobile apps  
- Multi-user cloud sync  
- Real-time push alerts (candidate for v1.1)  
- Per-application traffic analysis  

---

## 4. Target Users

| Persona | Need |
|---------|------|
| Remote worker (corporate VPN) | See ISP/Wi-Fi health independent of VPN |
| Gamer | Correlate latency drops with time of day |
| Network admin | Baseline ISP performance over a week |
| Home user | Find Wi-Fi dead zones or peak congestion |

---

## 5. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Detect and exclude virtual/VPN adapters (WMI + default route) | P0 |
| FR-02 | Poll speed on a **random 3–5 minute** interval | P0 |
| FR-03 | Persist samples to SQLite with timestamp and adapter name | P0 |
| FR-04 | API: daily graph data (minute resolution, 24h) | P0 |
| FR-05 | API: weekly view (7 stacked daily series) | P0 |
| FR-06 | API: worst 15-minute windows (day and week) | P0 |
| FR-07 | React dashboard: daily chart, 7 stacked charts, worst-times table | P0 |
| FR-08 | Run as Windows Service (nssm) for 24/7 collection | P1 |
| FR-09 | Package poller as portable EXE (PyInstaller) | P1 |
| FR-10 | Health check endpoint for monitoring | P1 |

---

## 6. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Physical speed accuracy with VPN active | Error &lt; 5% vs reference test on same adapter |
| NFR-02 | Uptime without crash or restart | 7+ days |
| NFR-03 | Idle memory (poller) | &lt; 30 MB RAM |
| NFR-04 | Idle CPU (poller) | &lt; 0.5% |
| NFR-05 | Dashboard initial load | &lt; 2 seconds on target hardware |
| NFR-06 | VPN adapter filtering accuracy | &gt; 95% on test matrix |
| NFR-07 | Data retention | 90 days default (configurable in v1.1) |

---

## 7. Success Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Measurement accuracy | Compare poller vs manual test on physical NIC with VPN on | &lt; 5% deviation |
| Stability | Continuous run without crash or unbounded memory growth | 7+ days |
| Time-to-insight | User identifies worst daily period from dashboard | Within first 24 hours of data |
| Dashboard performance | Time to interactive (TTI) | &lt; 2 seconds |
| Filtering quality | Correct physical adapter selected in VPN test scenarios | &gt; 95% |

---

## 8. User Stories

1. **As a** remote worker **I want** speed measured on my Wi-Fi/Ethernet adapter **so that** I know if my ISP is slow vs my VPN.  
2. **As a** user **I want** a 24-hour graph **so that** I see when slowdowns happen during the day.  
3. **As a** user **I want** seven stacked daily graphs **so that** I compare patterns across the week.  
4. **As a** user **I want** the slowest 15-minute windows highlighted **so that** I can avoid scheduling calls during those times.  
5. **As an** operator **I want** a portable package **so that** I can run the tool from a USB drive without installing dev tools.

---

## 9. Release Scope (v1.0)

### In scope

- Python poller (EXE), FastAPI server, React dashboard  
- SQLite schema and local `data/` storage  
- Install/uninstall scripts (nssm)  
- Deployment guide and release checklist  

### Out of scope (v1.1+)

- Email reports and threshold alerts  
- Automated weekly backup (post-launch ops)  
- Cross-machine aggregation  

---

## 10. Timeline & Milestones

| Day | Phase | Milestone |
|-----|-------|-----------|
| 1 | Concept & planning | PRD, technical spec, tickets (this document) |
| 2 | Skeleton | Repo structure, stubs, CI skeleton |
| 3 | Backend | VPN filtering, poller loop, SQLite |
| 4 | API + frontend | Endpoints, dashboard, integration tests |
| 5 | Integration | Service install, polish, regression |
| 6 | Deployment | EXE, zip, v1.0.0 tag, go/no-go |

**Total:** 5–6 days kickoff → production deployment.

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| WMI unavailable or restricted | No adapter list | Fallback to psutil + route heuristics |
| Speed test URL blocked | Missing samples | Configurable test endpoints; log and skip |
| VPN splits default route | Wrong adapter | Route-table analysis + keyword blocklist |
| 7 Recharts hurt performance | Slow dashboard | Memoization, shared scales, lazy load |
| PyInstaller false positives | Deploy blocked | Sign EXE; document AV exception |

---

<!-- ## 12. Open Questions -->

<!-- - [ ] Which speed-test method for v1 (HTTP download vs third-party CLI)?  
- [ ] Single process (poller + API) vs two services?  
- [ ] Default DB path: `%ProgramData%` vs portable `./data/`?   -->

## 12. Decisions (v1.0)

- [x] **Speed test:** HTTP download to a configurable URL (no third-party CLI in v1).
- [x] **Architecture:** Two processes — poller writes SQLite; FastAPI serves the dashboard.
- [x] **Database path:** `./data/speedmon.db` (portable, next to the install folder).

## 13. Approval

| Role | Name | Date | Sign-off |
|------|------|------|----------|
| PM | | | |
| Backend | | | |
| API | | | |
| Frontend | | | |
| DevOps/QA | | | |
