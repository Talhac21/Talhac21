import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from threading import Lock

from sqlalchemy import create_engine, text

job_lock = Lock()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://rr_user:rr_password@db:5432/rr_panel")
POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "60"))
PERK_INTERVAL_MINUTES = int(os.getenv("PERK_INTERVAL_MINUTES", "30"))

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


@contextmanager
def tx():
    with engine.begin() as conn:
        yield conn


def log_worker(level: str, event: str, payload: dict) -> None:
    with tx() as conn:
        conn.execute(
            text(
                "INSERT INTO worker_logs(level, event, payload, created_at) VALUES (:level, :event, :payload, CURRENT_TIMESTAMP)"
            ),
            {"level": level, "event": event, "payload": json.dumps(payload)},
        )


def schedule_next(now: datetime | None = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    return current + timedelta(minutes=PERK_INTERVAL_MINUTES)


def fetch_due_accounts(conn) -> list[dict]:
    rows = conn.execute(
        text(
            """
            SELECT a.id as account_id, a.alias, a.session_status, a.enabled, pj.id as job_id, pj.auto_enabled, pj.next_run_at
            FROM accounts a
            JOIN perk_jobs pj ON pj.account_id = a.id
            WHERE a.enabled = TRUE
              AND a.session_status = 'valid'
              AND pj.auto_enabled = TRUE
              AND (pj.next_run_at IS NULL OR pj.next_run_at <= CURRENT_TIMESTAMP)
            ORDER BY a.id ASC
            """
        )
    )
    return [dict(row._mapping) for row in rows]


def mark_job(conn, job_id: int, status: str, error: str | None, next_run: datetime | None) -> None:
    conn.execute(
        text(
            """
            UPDATE perk_jobs
            SET last_result = :status,
                retry_count = 0,
                last_error = :error,
                next_run_at = :next_run,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :job_id
            """
        ),
        {
            "status": status,
            "error": error,
            "next_run": next_run,
            "job_id": job_id,
        },
    )


def run_perk_cycle() -> int:
    if not job_lock.acquire(blocking=False):
        return 0

    processed = 0
    try:
        with tx() as conn:
            due = fetch_due_accounts(conn)
            for item in due:
                processed += 1
                mark_job(conn, item["job_id"], "unsupported", "worker requires API orchestration", schedule_next())
                conn.execute(
                    text(
                        "INSERT INTO audit_logs(account_id, action, status, details, created_at) VALUES (:account_id, 'perk.worker.schedule', 'warn', :details, CURRENT_TIMESTAMP)"
                    ),
                    {
                        "account_id": item["account_id"],
                        "details": json.dumps(
                            {
                                "result": "unsupported",
                                "reason": "worker requires API orchestration",
                            }
                        ),
                    },
                )
            conn.execute(
                text(
                    "INSERT INTO worker_logs(level, event, payload, created_at) VALUES ('INFO', 'worker.cycle', :payload, CURRENT_TIMESTAMP)"
                ),
                {"payload": json.dumps({"processed": processed})},
            )
        return processed
    finally:
        job_lock.release()


def start() -> None:
    log_worker("INFO", "worker.start", {"poll_seconds": POLL_SECONDS})
    while True:
        try:
            run_perk_cycle()
        except Exception as exc:  # pragma: no cover
            log_worker("ERROR", "worker.cycle.error", {"error": str(exc)})
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    start()
