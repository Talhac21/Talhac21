from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import crypto
from app.models.models import Account, AuditLog, JobStatus, PerkJob, SessionStatus
from app.services.rr_client import RRClient


class PerkRunner:
    def __init__(self, retries: int = 3) -> None:
        self.retries = retries
        self.client = RRClient()

    def run(self, db: Session, account: Account, job: PerkJob) -> tuple[bool, str, datetime | None]:
        if account.session_status != SessionStatus.valid:
            job.last_result = JobStatus.blocked
            job.last_error = "session-invalid"
            db.add(
                AuditLog(
                    account_id=account.id,
                    action="perk.run",
                    status="warn",
                    details={"result": "blocked", "reason": "session-invalid"},
                )
            )
            db.commit()
            return False, "session-invalid", None

        if not account.encrypted_session:
            job.last_result = JobStatus.blocked
            job.last_error = "session-missing"
            db.add(
                AuditLog(
                    account_id=account.id,
                    action="perk.run",
                    status="warn",
                    details={"result": "blocked", "reason": "session-missing"},
                )
            )
            db.commit()
            return False, "session-missing", None

        storage_state = crypto.decrypt(account.encrypted_session)
        last_message = "unknown"
        for attempt in range(1, self.retries + 1):
            result = self.client.run_perk(storage_state)
            job.retry_count = attempt - 1
            if result.status == "blocked":
                job.last_result = JobStatus.blocked
                job.last_error = result.details.get("reason", "blocked")
                account.session_status = SessionStatus.reauth_required
                db.add(
                    AuditLog(
                        account_id=account.id,
                        action="perk.run",
                        status="warn",
                        details={"attempt": attempt, "result": "blocked", **result.details},
                    )
                )
                db.commit()
                return False, "blocked", None

            if result.status == "unsupported":
                job.last_result = JobStatus.unsupported
                job.last_error = result.details.get("reason", "unsupported")
                db.add(
                    AuditLog(
                        account_id=account.id,
                        action="perk.run",
                        status="warn",
                        details={"attempt": attempt, "result": "unsupported", **result.details},
                    )
                )
                db.commit()
                return False, "unsupported", None

            if result.status == "success":
                next_run = result.next_run_at or datetime.now(timezone.utc) + timedelta(
                    minutes=settings.perk_interval_minutes
                )
                job.last_result = JobStatus.success
                job.last_error = None
                job.next_run_at = next_run
                account.last_sync_at = datetime.now(timezone.utc)
                db.add(
                    AuditLog(
                        account_id=account.id,
                        action="perk.run",
                        status="ok",
                        details={"attempt": attempt, "result": "success"},
                    )
                )
                db.commit()
                return True, "ok", next_run

            last_message = result.status

        job.last_result = JobStatus.failed
        job.last_error = last_message
        db.add(
            AuditLog(
                account_id=account.id,
                action="perk.run",
                status="error",
                details={"result": "failed", "message": last_message},
            )
        )
        db.commit()
        return False, "failed-after-retries", None
