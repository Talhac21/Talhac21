#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo ".env not found. run: cp .env.example .env"
  exit 1
fi

docker compose -f infra/docker-compose.yml up -d --build
