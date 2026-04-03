from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Account, AuditLog, CityTag, PerkJob, WatchedWar, WorkerLog
from app.schemas.schemas import AccountCreate, AccountOut, PerkRunResult, SessionBootstrapIn
from app.services.account_service import bootstrap_session, create_account
from app.services.perk_service import PerkRunner

router = APIRouter()


def admin_guard(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token != settings.api_admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/accounts", response_model=AccountOut, dependencies=[Depends(admin_guard)])
def add_account(payload: AccountCreate, db: Session = Depends(get_db)):
    try:
        return create_account(db, payload.alias)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/accounts", response_model=list[AccountOut], dependencies=[Depends(admin_guard)])
def list_accounts(db: Session = Depends(get_db)):
    return list(db.scalars(select(Account)).all())


@router.post("/accounts/{account_id}/bootstrap", response_model=AccountOut, dependencies=[Depends(admin_guard)])
def save_bootstrap(account_id: int, payload: SessionBootstrapIn, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    return bootstrap_session(db, account, payload.session_json)


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


@router.get("/dashboard", dependencies=[Depends(admin_guard)])
def dashboard(db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account)).all())
    logs = list(db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(10)).all())
    jobs = list(db.scalars(select(PerkJob)).all())
    return {
        "accounts": accounts,
        "recent_logs": logs,
        "jobs": jobs,
    }


@router.get("/tags", dependencies=[Depends(admin_guard)])
def list_tags(db: Session = Depends(get_db)):
    return list(db.scalars(select(CityTag)).all())


@router.get("/wars", dependencies=[Depends(admin_guard)])
def list_wars(db: Session = Depends(get_db)):
    return list(db.scalars(select(WatchedWar)).all())


@router.get("/logs", dependencies=[Depends(admin_guard)])
def list_logs(db: Session = Depends(get_db)):
    return {
        "audit": list(db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(50)).all()),
        "worker": list(db.scalars(select(WorkerLog).order_by(WorkerLog.id.desc()).limit(50)).all()),
    }
