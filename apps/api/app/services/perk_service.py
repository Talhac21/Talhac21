from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import Account, AuditLog, PerkJob, SessionStatus


class PerkRunner:
    def __init__(self, retries: int = 3) -> None:
        self.retries = retries

    def run(self, db: Session, account: Account, job: PerkJob) -> tuple[bool, str, datetime | None]:
        if account.session_status != SessionStatus.valid:
            return False, "session-invalid", None

        now = datetime.now(UTC)
        for attempt in range(1, self.retries + 1):
            try:
                # TODO: Replace with robust page-data based perk parser for production
                job.last_result = "success"
                job.retry_count = attempt - 1
                job.next_run_at = now + timedelta(minutes=30)
                db.add(
                    AuditLog(
                        account_id=account.id,
                        action="perk.run",
                        status="ok",
                        details={"attempt": attempt},
                    )
                )
                db.commit()
                return True, "ok", job.next_run_at
            except Exception as exc:  # pragma: no cover - safety path
                job.retry_count = attempt
                db.add(
                    AuditLog(
                        account_id=account.id,
                        action="perk.run",
                        status="retry",
                        details={"attempt": attempt, "error": str(exc)},
                    )
                )
                db.commit()
        return False, "failed-after-retries", None
