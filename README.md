# Rival Regions Control Panel (v1)

Production-minded monorepo for a **small-scale control panel** supporting **up to 2 user-owned accounts**.

## Scope and safety
- No proxy rotation, anti-detection, CAPTCHA bypass, or restriction bypass.
- No combat/farm/refill automation in v1.
- Manual browser-based session bootstrap only.
- Encrypted cookie/session storage at rest.

## Monorepo layout
- `apps/web` — Next.js App Router + TypeScript admin panel
- `apps/api` — FastAPI backend
- `apps/worker` — APScheduler worker for low-frequency jobs
- `packages/shared` — shared constants/types
- `infra` — Caddy config
- `docs` — architecture and deployment docs
- `scripts` — startup and backup scripts

## Quick start
1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start stack:
   ```bash
   ./scripts/start.sh
   ```
3. Open:
   - Web: `http://localhost:3000`
   - API docs: `http://localhost:8000/docs`

## Key features in v1
- Account management with encrypted session bootstrap records.
- Dashboard with account/session/perk summary.
- Auto-perk scheduler with lock, retries/backoff, and audit logs.
- Friend/enemy city tags CRUD.
- Read-only wars watchlist.
- Calculators (perk, region cost, production, mercenary).
- Structured logs + health endpoint.
- Telegram notifications for critical events.

## Testing
- API + worker scheduler tests are included.
- Run with:
  ```bash
  docker compose run --rm api pytest
  docker compose run --rm worker pytest
  ```

## Notes
- Session bootstrap intentionally requires explicit human login in Playwright.
- Re-auth states are explicit and halt scheduling for affected accounts.
- Feature flags can disable unfinished modules safely.
