# Kickoff Meeting Agenda

**Duration:** 30 minutes  
**Attendees:** PM, Backend, API, Frontend, DevOps/QA

---

## 1. Vision (5 min)

- Problem: VPN masks true network performance  
- Solution: Monitor physical adapters, visualize worst times  
- Tagline: *Know your true speed, not your tunnel speed.*

## 2. Success metrics (5 min)

Review [prd.md](./prd.md) §7:

- &lt; 5% measurement error with VPN on  
- 7+ days stable run  
- Worst period identifiable within 24h  
- Dashboard &lt; 2s load  

## 3. Architecture walkthrough (5 min)

Review [technical-spec.md](./technical-spec.md) diagram:

Poller → SQLite ← API ← React

## 4. Sprint plan (10 min)

| Day | Focus | Owner highlights |
|-----|-------|------------------|
| 1 | Planning (done) | PM: docs + tickets |
| 2 | Skeleton | PM + all stubs |
| 3 | Backend | Tickets 4–5 |
| 4 | API + UI | Tickets 6–7 parallel |
| 5 | Integration | Ticket 8–9 |
| 6 | Release | Ticket 10 |

Assign owners to tickets in [tickets.md](./tickets.md).

## 5. Cadence & communication (3 min)

- **Standup:** 9:30 daily — done / doing / blockers  
- **PM triage:** 9:45  
- **Code review:** 10:00 (PM)  
- **Branch naming:** `feature/<ticket-short-name>`

## 6. Blockers & questions (2 min)

Document open questions from PRD §12.

---

## Action items

| Action | Owner | Due |
|--------|-------|-----|
| Create GitHub repo + Projects board | PM | Day 1 |
| Import 10 tickets from tickets.md | PM | Day 1 |
| Read PRD + technical spec | All | Before Day 2 |
| Confirm Windows VM for QA | DevOps | Day 2 |
