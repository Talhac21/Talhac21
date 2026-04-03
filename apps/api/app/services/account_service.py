from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import crypto
from app.models.models import Account, AuditLog, PerkJob, SessionStatus

MAX_ACCOUNTS = 2


def create_account(db: Session, alias: str) -> Account:
    # Use FOR UPDATE lock to prevent race condition on account limit check
    count = db.execute(
        select(func.count(Account.id)).with_for_update()
    ).scalar_one()
    if count >= MAX_ACCOUNTS:
        raise ValueError("Account limit reached (max 2)")
    account = Account(alias=alias)
    db.add(account)
    # Auto-create a PerkJob for the new account
    db.flush()  # get account.id
    job = PerkJob(account_id=account.id, auto_enabled=False)
    db.add(job)
    db.add(AuditLog(action="account.create", status="ok", details={"alias": alias}))
    db.commit()
    db.refresh(account)
    return account


def bootstrap_session(db: Session, account: Account, session_json: str) -> Account:
    account.encrypted_session = crypto.encrypt(session_json)
    account.session_status = SessionStatus.valid
    db.add(
        AuditLog(
            account_id=account.id,
            action="session.bootstrap",
            status="ok",
            details={"len": len(session_json)},
        )
    )
    db.commit()
    db.refresh(account)
    return account


def mark_reauth_required(db: Session, account: Account, reason: str) -> None:
    account.session_status = SessionStatus.reauth_required
    db.add(
        AuditLog(
            account_id=account.id,
            action="session.reauth_required",
            status="warn",
            details={"reason": reason},
        )
    )
    db.commit()


def toggle_auto_perk(db: Session, account_id: int, enabled: bool) -> PerkJob:
    """Enable or disable automatic perk scheduling for an account."""
    job = db.scalar(select(PerkJob).where(PerkJob.account_id == account_id))
    if not job:
        job = PerkJob(account_id=account_id, auto_enabled=enabled)
        db.add(job)
    else:
        job.auto_enabled = enabled
    db.add(
        AuditLog(
            account_id=account_id,
            action="perk.toggle",
            status="ok",
            details={"auto_enabled": enabled},
        )
    )
    db.commit()
    db.refresh(job)
    return job
