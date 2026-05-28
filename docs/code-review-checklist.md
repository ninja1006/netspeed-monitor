# Code Review Checklist (PM)

Use on every PR before merge.

## General

- [ ] PR description links to ticket number  
- [ ] No secrets, `.env`, or `data/*.db` committed  
- [ ] Changes scoped to ticket (no unrelated refactors)  

## Backend / Poller

- [ ] Physical adapter only — VPN/virtual adapters excluded  
- [ ] Handles: no network, adapter removed mid-run, speed test timeout  
- [ ] Random sleep 180–300s (not fixed interval)  
- [ ] DB writes use parameterized queries  
- [ ] Errors logged; process does not exit on single failure  

## API

- [ ] Response shapes match [technical-spec.md](./technical-spec.md)  
- [ ] Date parsing validates input (400 on bad format)  
- [ ] 15-minute worst-time logic has unit test  
- [ ] API binds to localhost in production config  

## Frontend

- [ ] Loading and error states for all fetches  
- [ ] Seven week charts memoized or optimized  
- [ ] No hardcoded production URLs (use env/config)  

## DevOps

- [ ] CI passes  
- [ ] New dependencies documented in `requirements.txt` / `package.json`  

## Sign-off

| Reviewer | Date | Approve (Y/N) |
|----------|------|---------------|
| PM | | |
