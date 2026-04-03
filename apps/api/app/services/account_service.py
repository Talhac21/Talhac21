from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import crypto
from app.models.models import Account, AuditLog, SessionStatus

MAX_ACCOUNTS = 2


def create_account(db: Session, alias: str) -> Account:
    count = db.scalar(select(func.count(Account.id))) or 0
    if count >= MAX_ACCOUNTS:
        raise ValueError("Account limit reached (max 2)")
    account = Account(alias=alias)
    db.add(account)
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
