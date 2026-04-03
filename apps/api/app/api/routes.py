from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Account, AuditLog, CityTag, ErrorLog, PerkJob, SessionStatus, WatchedWar, WorkerLog
from app.schemas.schemas import AccountCreate, AccountOut, DashboardCard, DashboardOut, PerkRunResult, SessionBootstrapIn
from app.services.account_service import bootstrap_session, check_session_health, create_account
from app.services.perk_service import PerkRunner

router = APIRouter()


def _serialize_log(log: AuditLog | WorkerLog | ErrorLog) -> dict:
    return {
        "id": log.id,
        "created_at": log.created_at.isoformat() if log.created_at else None,
        **({"action": getattr(log, "action"), "status": getattr(log, "status"), "details": getattr(log, "details")} if isinstance(log, AuditLog) else {}),
        **({"event": getattr(log, "event"), "level": getattr(log, "level"), "payload": getattr(log, "payload")} if isinstance(log, WorkerLog) else {}),
        **({"source": getattr(log, "source"), "message": getattr(log, "message"), "payload": getattr(log, "payload")} if isinstance(log, ErrorLog) else {}),
    }


def admin_guard(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token != settings.api_admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@router.post("/accounts", response_model=AccountOut, dependencies=[Depends(admin_guard)])
def add_account(payload: AccountCreate, db: Session = Depends(get_db)):
    try:
        return create_account(db, payload.alias)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/accounts", response_model=list[AccountOut], dependencies=[Depends(admin_guard)])
def list_accounts(db: Session = Depends(get_db)):
    return list(db.scalars(select(Account).order_by(Account.id.asc())).all())


@router.post("/accounts/{account_id}/bootstrap", response_model=AccountOut, dependencies=[Depends(admin_guard)])
def save_bootstrap(account_id: int, payload: SessionBootstrapIn, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    return bootstrap_session(db, account, payload.session_json)


@router.post("/accounts/{account_id}/session/health", dependencies=[Depends(admin_guard)])
def session_health(account_id: int, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    status = check_session_health(db, account)
    return {"account_id": account_id, "session_status": status.value}


@router.post("/accounts/{account_id}/enable", dependencies=[Depends(admin_guard)])
def toggle_account(account_id: int, enabled: bool, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    account.enabled = enabled
    if not enabled:
        account.session_status = SessionStatus.disabled
    db.add(
        AuditLog(
            account_id=account.id,
            action="account.toggle",
            status="ok",
            details={"enabled": enabled},
        )
    )
    db.commit()
    return {"ok": True, "enabled": enabled}


@router.post(
    "/accounts/{account_id}/perk/run-now",
    response_model=PerkRunResult,
    dependencies=[Depends(admin_guard)],
)
def run_perk_now(account_id: int, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    job = db.scalar(select(PerkJob).where(PerkJob.account_id == account_id))
    if not job:
        job = PerkJob(account_id=account_id, auto_enabled=False)
        db.add(job)
        db.commit()
        db.refresh(job)
    success, message, next_run = PerkRunner().run(db, account, job)
    return PerkRunResult(success=success, message=message, next_run_at=next_run)


@router.get("/dashboard", response_model=DashboardOut, dependencies=[Depends(admin_guard)])
def dashboard(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    cards: list[DashboardCard] = []
    accounts = list(db.scalars(select(Account).order_by(Account.id.asc())).all())
    for acc in accounts:
        job = db.scalar(select(PerkJob).where(PerkJob.account_id == acc.id))
        remaining = None
        if job and job.next_run_at:
            remaining = max(int((job.next_run_at.replace(tzinfo=timezone.utc) - now).total_seconds()), 0)
        cards.append(
            DashboardCard(
                account_id=acc.id,
                alias=acc.alias,
                enabled=acc.enabled,
                session_status=acc.session_status.value,
                auto_perk_enabled=bool(job.auto_enabled) if job else False,
                next_run_at=job.next_run_at if job else None,
                last_result=job.last_result.value if job else "idle",
                time_remaining_seconds=remaining,
            )
        )

    logs = list(db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(15)).all())
    return DashboardOut(accounts=cards, recent_logs=[_serialize_log(x) for x in logs], generated_at=now)


@router.get("/tags", dependencies=[Depends(admin_guard)])
def list_tags(db: Session = Depends(get_db)):
    return list(db.scalars(select(CityTag).order_by(CityTag.id.desc())).all())


@router.get("/wars", dependencies=[Depends(admin_guard)])
def list_wars(db: Session = Depends(get_db)):
    return list(db.scalars(select(WatchedWar).order_by(WatchedWar.id.desc())).all())


@router.get("/logs", dependencies=[Depends(admin_guard)])
def list_logs(db: Session = Depends(get_db)):
    return {
        "audit": [
            _serialize_log(x)
            for x in db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(50)).all()
        ],
        "worker": [
            _serialize_log(x)
            for x in db.scalars(select(WorkerLog).order_by(WorkerLog.id.desc()).limit(50)).all()
        ],
        "errors": [
            _serialize_log(x)
            for x in db.scalars(select(ErrorLog).order_by(ErrorLog.id.desc()).limit(50)).all()
        ],
    }
