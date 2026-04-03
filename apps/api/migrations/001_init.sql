-- Initial schema migration (v1)
CREATE TYPE sessionstatus AS ENUM ('valid', 'reauth_required', 'disabled');
CREATE TYPE citytagtype AS ENUM ('friend', 'enemy');

CREATE TABLE accounts (
  id SERIAL PRIMARY KEY,
  alias VARCHAR(80) UNIQUE NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  session_status sessionstatus NOT NULL DEFAULT 'reauth_required',
  encrypted_session TEXT,
  last_sync_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE perk_jobs (
  id SERIAL PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(id),
  auto_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  next_run_at TIMESTAMP,
  last_result VARCHAR(32),
  retry_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE city_tags (
  id SERIAL PRIMARY KEY,
  account_id INTEGER REFERENCES accounts(id),
  city_name VARCHAR(120) NOT NULL,
  type citytagtype NOT NULL,
  color VARCHAR(24) NOT NULL DEFAULT 'gray',
  notes TEXT
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  account_id INTEGER REFERENCES accounts(id),
  action VARCHAR(120) NOT NULL,
  status VARCHAR(32) NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE worker_logs (
  id SERIAL PRIMARY KEY,
  level VARCHAR(16) NOT NULL,
  event VARCHAR(120) NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE watched_wars (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  participants TEXT NOT NULL,
  status VARCHAR(64) NOT NULL,
  last_update_at TIMESTAMP
);
