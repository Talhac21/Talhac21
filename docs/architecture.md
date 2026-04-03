# Architecture

## Runtime topology
- **web (Next.js)**: server-rendered dashboard/accounts/logs pages from API.
- **api (FastAPI)**: account lifecycle, encrypted session storage, dashboard, run-now, logs.
- **worker (Python loop)**: low-frequency DB poller for due auto-perk jobs.
- **db (PostgreSQL)**: accounts, perk jobs, tags, audit/worker/error logs.
- **caddy**: reverse proxy.

## Data flow
1. Admin account oluşturur (`POST /accounts`).
2. Manuel Playwright login sonrası `storage_state` JSON API’a bootstrap edilir.
3. API session’ı doğrular (`RRClient.validate_session`) ve account status günceller.
4. Dashboard API’dan gerçek account/job/log verisi okunur.
5. Worker DB’de yalnızca uygun kayıtları seçer (`enabled`, `valid`, `auto_enabled`, `due`) ve job metadata günceller.
6. Tüm aksiyonlar audit/worker loglara yazılır.

## Migration strategy
- `apps/api/app/db/session.py` içindeki `run_migrations()` startup’ta SQL migration dosyalarını `schema_migrations` tablosu üzerinden uygular.

## Safety constraints enforced
- hard limit: max 2 accounts
- explicit session states: `valid`, `reauth_required`, `disabled`, `unknown`
- invalid/unknown session durumunda worker/perk akışı block olur
- unsupported RR action açıkça `unsupported` döner (fake success yok)
