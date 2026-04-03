import json
import logging
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.core.security import crypto
from app.models.models import Account, AuditLog, PerkJob, SessionStatus
from app.services.notifier import send_telegram

logger = logging.getLogger(__name__)

RR_BASE = "https://rivalregions.com"

# Known perk type IDs used by the game
PERK_TYPES: dict[str, str] = {
    "str": "1",
    "edu": "2",
    "end": "3",
}


def _build_session(account: Account) -> httpx.Client:
    """Decrypt stored session and build an httpx client with RR cookies."""
    raw = crypto.decrypt(account.encrypted_session)
    storage = json.loads(raw)

    cookies = httpx.Cookies()
    for cookie in storage.get("cookies", []):
        cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain", ""))

    client = httpx.Client(
        base_url=RR_BASE,
        cookies=cookies,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "Referer": f"{RR_BASE}/",
            "X-Requested-With": "XMLHttpRequest",
        },
        follow_redirects=True,
        timeout=15,
    )
    return client


def _check_session_alive(client: httpx.Client) -> bool:
    """Quick check: hit the main page and see if we are logged in."""
    try:
        resp = client.get("/slide/profile")
        return resp.status_code == 200 and "userMenu" not in resp.text
    except httpx.HTTPError:
        return False


def _execute_perk(client: httpx.Client, perk_type: str) -> dict:
    """Send the actual perk training request to RR.

    Returns a dict with 'ok' flag and optional detail.
    """
    perk_id = PERK_TYPES.get(perk_type, perk_type)
    try:
        resp = client.post(
            "/perks/up",
            data={"type": perk_id, "alt": "0"},
        )
        if resp.status_code == 200:
            return {"ok": True, "detail": resp.text[:200]}
        return {"ok": False, "detail": f"HTTP {resp.status_code}"}
    except httpx.HTTPError as exc:
        return {"ok": False, "detail": str(exc)}


class PerkRunner:
    def __init__(self, retries: int = 3) -> None:
        self.retries = retries

    def run(
        self, db: Session, account: Account, job: PerkJob
    ) -> tuple[bool, str, datetime | None]:
        if account.session_status != SessionStatus.valid:
            return False, "session-invalid", None

        if not account.encrypted_session:
            return False, "no-session-stored", None

        # Decrypt session and build HTTP client
        try:
            client = _build_session(account)
        except Exception as exc:
            logger.error("Session decryption failed for account %s: %s", account.id, exc)
            return False, "session-decrypt-error", None

        # Validate session is still alive
        if not _check_session_alive(client):
            account.session_status = SessionStatus.reauth_required
            db.add(
                AuditLog(
                    account_id=account.id,
                    action="perk.run",
                    status="reauth",
                    details={"reason": "session expired or invalid"},
                )
            )
            db.commit()
            send_telegram(f"⚠️ Account {account.alias}: session expired, re-auth required")
            client.close()
            return False, "session-expired", None

        now = datetime.now(UTC)
        last_error = ""
        for attempt in range(1, self.retries + 1):
            try:
                result = _execute_perk(client, "str")
                if result["ok"]:
                    job.last_result = "success"
                    job.retry_count = 0
                    job.next_run_at = now + timedelta(minutes=30)
                    account.last_sync_at = now
                    db.add(
                        AuditLog(
                            account_id=account.id,
                            action="perk.run",
                            status="ok",
                            details={"attempt": attempt, "detail": result.get("detail", "")[:100]},
                        )
                    )
                    db.commit()
                    send_telegram(f"✅ Account {account.alias}: perk applied (attempt {attempt})")
                    client.close()
                    return True, "ok", job.next_run_at

                last_error = result.get("detail", "unknown")
                logger.warning(
                    "Perk attempt %d/%d failed for account %s: %s",
                    attempt,
                    self.retries,
                    account.id,
                    last_error,
                )
            except Exception as exc:
                last_error = str(exc)
                logger.error(
                    "Perk attempt %d/%d exception for account %s: %s",
                    attempt,
                    self.retries,
                    account.id,
                    exc,
                )

            job.retry_count = attempt
            db.add(
                AuditLog(
                    account_id=account.id,
                    action="perk.run",
                    status="retry",
                    details={"attempt": attempt, "error": last_error[:200]},
                )
            )
            db.commit()

        job.last_result = "failed"
        job.next_run_at = now + timedelta(minutes=10)  # shorter retry window
        db.commit()
        send_telegram(f"❌ Account {account.alias}: perk failed after {self.retries} retries")
        client.close()
        return False, "failed-after-retries", job.next_run_at
