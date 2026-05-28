# Release Checklist — v1.0.0

Complete before tagging `v1.0.0`.

## Pre-build

- [ ] All Phase 3–5 tickets closed or deferred with documented reason  
- [ ] `main` branch green (CI passing)  
- [ ] [known-issues.md](./known-issues.md) updated  
- [ ] [deploy.md](./deploy.md) finalized  

## Build

- [ ] `pyinstaller` poller EXE builds without errors  
- [ ] `npm run build` frontend succeeds  
- [ ] `speedmon-v1.0.0.zip` contains: EXE, API, dashboard static, scripts, docs  

## Test (clean Windows VM)

- [ ] Install from zip / USB without Python or Node installed  
- [ ] Service starts and collects samples for 1+ hour  
- [ ] Dashboard loads in &lt; 2 seconds  
- [ ] VPN on: physical adapter measurement within 5% of reference  
- [ ] Uninstall removes service and leaves no orphan processes  

## Release

- [ ] Git tag `v1.0.0` pushed  
- [ ] GitHub Release notes published  
- [ ] PM 24h post-deploy monitoring scheduled  

## Go / No-go

| Criterion | Pass? |
|-----------|-------|
| Poller stable 24h | |
| Data visible in dashboard | |
| No critical open bugs | |

**Decision:** Go / No-go — **Date:** ______ — **PM:**
