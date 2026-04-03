from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import crypto
from app.models.models import Account, AuditLog, PerkJob, SessionStatus
from app.services.rr_client import RRClient

MAX_ACCOUNTS = 2


def create_account(db: Session, alias: str) -> Account:
    count = db.scalar(select(func.count(Account.id))) or 0
    if count >= MAX_ACCOUNTS:
        raise ValueError("Account limit reached (max 2)")
    account = Account(alias=alias)
    db.add(account)
    db.flush()
    db.add(PerkJob(account_id=account.id, auto_enabled=False))
    db.add(AuditLog(action="account.create", status="ok", details={"alias": alias}))
    db.commit()
    db.refresh(account)
    return account


def bootstrap_session(db: Session, account: Account, session_json: str) -> Account:
    account.encrypted_session = crypto.encrypt(session_json)
    check = RRClient().validate_session(session_json)
    account.last_session_check_at = datetime.now(timezone.utc)
    if check.status == "valid":
        account.session_status = SessionStatus.valid
        status = "ok"
    elif check.status == "invalid":
        account.session_status = SessionStatus.reauth_required
        status = "warn"
    else:
        account.session_status = SessionStatus.unknown
        status = "warn"

    db.add(
        AuditLog(
            account_id=account.id,
            action="session.bootstrap",
            status=status,
            details={"result": check.status, "message": check.message},
        )
    )
    db.commit()
    db.refresh(account)
    return account


def check_session_health(db: Session, account: Account) -> SessionStatus:
    if not account.encrypted_session:
        account.session_status = SessionStatus.reauth_required
        db.add(
            AuditLog(
                account_id=account.id,
                action="session.healthcheck",
                status="warn",
                details={"result": "no-session"},
            )
        )
        db.commit()
        return account.session_status

    raw_session = crypto.decrypt(account.encrypted_session)
    result = RRClient().validate_session(raw_session)
    account.last_session_check_at = datetime.now(timezone.utc)
    if result.status == "valid":
        account.session_status = SessionStatus.valid
    elif result.status == "invalid":
        account.session_status = SessionStatus.reauth_required
    else:
        account.session_status = SessionStatus.unknown

    db.add(
        AuditLog(
            account_id=account.id,
            action="session.healthcheck",
            status="ok" if result.status == "valid" else "warn",
            details={"result": result.status, "message": result.message},
        )
    )
    db.commit()
    return account.session_status
