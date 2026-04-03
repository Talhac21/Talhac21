# Architecture

## Components
- Next.js UI (`apps/web`) for operator control panel.
- FastAPI (`apps/api`) for account/session management, logs, and calculators.
- APScheduler worker (`apps/worker`) for low-frequency auto perk jobs.
- PostgreSQL for durable state.
- Caddy reverse proxy.

## Security controls
- Encrypted session cookie blobs (Fernet).
- Admin token gate for API routes in v1.
- Explicit `reauth_required` session state.
- Per-account enable/disable and hard cap of 2 accounts.
- Audit/worker logs for traceability.

## Scheduling behavior
- Poll-style scheduler every 5 minutes.
- Max instance lock to avoid overlap.
- Retry/backoff behavior in perk service.
- Scheduler pauses if session status is not valid.
