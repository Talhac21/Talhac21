#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8000}"
TOKEN="${API_ADMIN_TOKEN:-replace-with-token}"

curl -fsS "${API_URL}/health" >/dev/null
curl -fsS -H "x-admin-token: ${TOKEN}" "${API_URL}/dashboard" >/dev/null

echo "smoke test passed"
