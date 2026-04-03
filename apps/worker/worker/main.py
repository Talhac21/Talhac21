import logging
import os
from datetime import UTC, datetime, timedelta
from threading import Lock

import httpx
from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

job_lock = Lock()

API_BASE = os.environ.get("API_BASE_URL", "http://api:8000")
ADMIN_TOKEN = os.environ.get("API_ADMIN_TOKEN", "")


def schedule_next(now: datetime | None = None) -> datetime:
    current = now or datetime.now(UTC)
    return current + timedelta(minutes=30)


def _api_headers() -> dict[str, str]:
    return {"X-Admin-Token": ADMIN_TOKEN}


def run_perk_cycle() -> None:
    """Poll the API for enabled accounts and execute perk jobs."""
    if not job_lock.acquire(blocking=False):
        logger.info("Perk cycle already running, skipping")
        return
    try:
        logger.info("Starting perk cycle")
        with httpx.Client(base_url=API_BASE, headers=_api_headers(), timeout=30) as client:
            # 1. Fetch dashboard to get accounts + jobs
            try:
                resp = client.get("/dashboard")
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.error("Failed to fetch dashboard: %s", exc)
                return

            accounts = data.get("accounts", [])
            jobs = {j["account_id"]: j for j in data.get("jobs", [])}

            now = datetime.now(UTC)

            for account in accounts:
                account_id = account["id"]
                alias = account.get("alias", f"account-{account_id}")
                session_status = account.get("session_status", "")
                job = jobs.get(account_id, {})
                auto_enabled = job.get("auto_enabled", False)

                # Skip if auto_enabled is off
                if not auto_enabled:
                    logger.debug("Account %s: auto_perk disabled, skipping", alias)
                    continue

                # Skip if session not valid
                if session_status != "valid":
                    logger.warning("Account %s: session status=%s, skipping", alias, session_status)
                    continue

                # Check next_run_at — skip if not due yet
                next_run_raw = job.get("next_run_at")
                if next_run_raw:
                    try:
                        next_run = datetime.fromisoformat(next_run_raw)
                        if next_run.tzinfo is None:
                            next_run = next_run.replace(tzinfo=UTC)
                        if now < next_run:
                            logger.debug(
                                "Account %s: not due yet (next_run_at=%s)", alias, next_run_raw
                            )
                            continue
                    except (ValueError, TypeError):
                        pass  # invalid date, run anyway

                # Execute perk
                logger.info("Running perk for account %s (id=%d)", alias, account_id)
                try:
                    perk_resp = client.post(f"/accounts/{account_id}/perk/run-now")
                    perk_resp.raise_for_status()
                    result = perk_resp.json()
                    logger.info(
                        "Perk result for %s: success=%s message=%s next_run=%s",
                        alias,
                        result.get("success"),
                        result.get("message"),
                        result.get("next_run_at"),
                    )
                except Exception as exc:
                    logger.error("Perk execution failed for %s: %s", alias, exc)

        logger.info("Perk cycle completed")

    except Exception as exc:
        logger.error("Unexpected error in perk cycle: %s", exc)
    finally:
        job_lock.release()


def start() -> None:
    logger.info("Worker starting — API=%s, polling every 5 minutes", API_BASE)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_perk_cycle, "interval", minutes=5, max_instances=1, coalesce=True)
    scheduler.start()


if __name__ == "__main__":
    start()
