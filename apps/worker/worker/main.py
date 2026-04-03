from datetime import UTC, datetime, timedelta
from threading import Lock

from apscheduler.schedulers.blocking import BlockingScheduler

job_lock = Lock()


def schedule_next(now: datetime | None = None) -> datetime:
    current = now or datetime.now(UTC)
    return current + timedelta(minutes=30)


def run_perk_cycle() -> None:
    if not job_lock.acquire(blocking=False):
        return
    try:
        # TODO: call API endpoint for enabled accounts and execute low-frequency perk checks
        _ = schedule_next()
    finally:
        job_lock.release()


def start() -> None:
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_perk_cycle, "interval", minutes=5, max_instances=1, coalesce=True)
    scheduler.start()


if __name__ == "__main__":
    start()
