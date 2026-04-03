DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'sessionstatus') THEN
    CREATE TYPE sessionstatus AS ENUM ('valid', 'reauth_required', 'disabled', 'unknown');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jobstatus') THEN
    CREATE TYPE jobstatus AS ENUM ('idle', 'success', 'failed', 'blocked', 'unsupported');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'citytagtype') THEN
    CREATE TYPE citytagtype AS ENUM ('friend', 'enemy');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS accounts (
  id SERIAL PRIMARY KEY,
  alias VARCHAR(80) UNIQUE NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  session_status sessionstatus NOT NULL DEFAULT 'reauth_required',
  encrypted_session TEXT,
  last_sync_at TIMESTAMP,
  last_session_check_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS perk_jobs (
  id SERIAL PRIMARY KEY,
  account_id INTEGER UNIQUE NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  auto_enabled BOOLEAN NOT NULL DEFAULT FALSE,
  next_run_at TIMESTAMP,
  last_result jobstatus NOT NULL DEFAULT 'idle',
  retry_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS city_tags (
  id SERIAL PRIMARY KEY,
  account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
  city_name VARCHAR(120) NOT NULL,
  type citytagtype NOT NULL,
  color VARCHAR(24) NOT NULL DEFAULT 'gray',
  notes TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id SERIAL PRIMARY KEY,
  account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
  action VARCHAR(120) NOT NULL,
  status VARCHAR(32) NOT NULL,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worker_logs (
  id SERIAL PRIMARY KEY,
  level VARCHAR(16) NOT NULL,
  event VARCHAR(120) NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS error_logs (
  id SERIAL PRIMARY KEY,
  source VARCHAR(120) NOT NULL,
  message TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS watched_wars (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  participants TEXT NOT NULL,
  status VARCHAR(64) NOT NULL,
  last_update_at TIMESTAMP
);
