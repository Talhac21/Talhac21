#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
STAMP="$(date -u +%Y%m%d_%H%M%S)"

docker compose -f infra/docker-compose.yml exec -T db pg_dump -U "${POSTGRES_USER:-rr_user}" "${POSTGRES_DB:-rr_panel}" > "backups/db_${STAMP}.sql"
docker compose -f infra/docker-compose.yml exec -T db psql -U "${POSTGRES_USER:-rr_user}" -d "${POSTGRES_DB:-rr_panel}" -At -F $'\t' -c "SELECT id, alias, session_status, encrypted_session FROM accounts;" > "backups/encrypted_sessions_${STAMP}.tsv"

echo "Backup created at ${STAMP}"
