from datetime import datetime, timezone

from sqlalchemy import create_engine, text

import worker.main as wm


def setup_db(engine):
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE accounts (id INTEGER PRIMARY KEY, alias TEXT, session_status TEXT, enabled BOOLEAN)"))
        conn.execute(
            text(
                "CREATE TABLE perk_jobs (id INTEGER PRIMARY KEY, account_id INTEGER, auto_enabled BOOLEAN, next_run_at TIMESTAMP, last_result TEXT, retry_count INTEGER, last_error TEXT, updated_at TIMESTAMP)"
            )
        )
        conn.execute(text("CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, account_id INTEGER, action TEXT, status TEXT, details TEXT, created_at TIMESTAMP)"))
        conn.execute(text("CREATE TABLE worker_logs (id INTEGER PRIMARY KEY, level TEXT, event TEXT, payload TEXT, created_at TIMESTAMP)"))


def test_schedule_next_is_30_minute_step():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert wm.schedule_next(now).isoformat().startswith("2026-01-01T12:30:00")


def test_invalid_session_blocks_worker(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    setup_db(engine)
    monkeypatch.setattr(wm, "engine", engine)

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO accounts(id, alias, session_status, enabled) VALUES (1, 'a', 'reauth_required', 1)"))
        conn.execute(text("INSERT INTO perk_jobs(id, account_id, auto_enabled, next_run_at, last_result, retry_count, last_error, updated_at) VALUES (1,1,1,NULL,'idle',0,NULL,CURRENT_TIMESTAMP)"))

    processed = wm.run_perk_cycle()
    assert processed == 0


def test_lock_prevents_duplicate_runs(monkeypatch):
    engine = create_engine("sqlite+pysqlite:///:memory:")
    setup_db(engine)
    monkeypatch.setattr(wm, "engine", engine)

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO accounts(id, alias, session_status, enabled) VALUES (1, 'a', 'valid', 1)"))
        conn.execute(text("INSERT INTO perk_jobs(id, account_id, auto_enabled, next_run_at, last_result, retry_count, last_error, updated_at) VALUES (1,1,1,NULL,'idle',0,NULL,CURRENT_TIMESTAMP)"))

    assert wm.job_lock.acquire(blocking=False)
    try:
        processed = wm.run_perk_cycle()
        assert processed == 0
    finally:
        wm.job_lock.release()
