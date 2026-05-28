# Contributing

## Branch naming

- `feature/<short-description>` — new work  
- `fix/<short-description>` — bug fixes  

Example: `feature/poller-vpn-filter`

## Pull requests

1. Link the GitHub issue (e.g. `Closes #3`).  
2. Keep changes scoped to one ticket.  
3. Ensure CI passes (pytest + frontend build).  
4. Request PM review using [docs/code-review-checklist.md](docs/code-review-checklist.md).

## Local checks before PR

```powershell
.\venv\Scripts\Activate.ps1
pytest backend/tests -v
cd frontend
npm run build
```

## Commit messages

- `feat:` new feature  
- `fix:` bug fix  
- `docs:` documentation only  
- `chore:` tooling, CI, deps  

Example: `feat: stub poller with fake SQLite samples`
