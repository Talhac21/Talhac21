from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Account, AuditLog, CityTag, PerkJob, WatchedWar, WorkerLog
from app.schemas.schemas import AccountCreate, AccountOut, PerkRunResult, PerkToggleIn, SessionBootstrapIn
from app.services.account_service import bootstrap_session, create_account, toggle_auto_perk
from app.services.perk_service import PerkRunner

router = APIRouter()


def admin_guard(x_admin_token: str = Header(default="")) -> None:
    if x_admin_token != settings.api_admin_token:
        raise HTTPException(status_code=401, detail="invalid admin token")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ── Accounts ─────────────────────────────────────────────────────────

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


# ── Perk ─────────────────────────────────────────────────────────────

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


@router.post(
    "/accounts/{account_id}/perk/toggle",
    dependencies=[Depends(admin_guard)],
)
def toggle_perk(account_id: int, payload: PerkToggleIn, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    job = toggle_auto_perk(db, account_id, payload.auto_enabled)
    return {"account_id": account_id, "auto_enabled": job.auto_enabled}


# ── Dashboard ────────────────────────────────────────────────────────

@router.get("/dashboard", dependencies=[Depends(admin_guard)])
def dashboard(db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account)).all())
    logs = list(db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(10)).all())
    jobs = list(db.scalars(select(PerkJob)).all())

    accounts_out = [AccountOut.model_validate(a) for a in accounts]
    jobs_out = [
        {
            "id": j.id,
            "account_id": j.account_id,
            "auto_enabled": j.auto_enabled,
            "next_run_at": j.next_run_at.isoformat() if j.next_run_at else None,
            "last_result": j.last_result,
            "retry_count": j.retry_count,
        }
        for j in jobs
    ]
    logs_out = [
        {
            "id": l.id,
            "account_id": l.account_id,
            "action": l.action,
            "status": l.status,
            "details": l.details,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
    return {"accounts": accounts_out, "recent_logs": logs_out, "jobs": jobs_out}


# ── Tags ─────────────────────────────────────────────────────────────

@router.get("/tags", dependencies=[Depends(admin_guard)])
def list_tags(db: Session = Depends(get_db)):
    tags = list(db.scalars(select(CityTag)).all())
    return [
        {
            "id": t.id,
            "account_id": t.account_id,
            "city_name": t.city_name,
            "type": t.type.value if t.type else t.type,
            "color": t.color,
            "notes": t.notes,
        }
        for t in tags
    ]


# ── Wars ─────────────────────────────────────────────────────────────

@router.get("/wars", dependencies=[Depends(admin_guard)])
def list_wars(db: Session = Depends(get_db)):
    wars = list(db.scalars(select(WatchedWar)).all())
    return [
        {
            "id": w.id,
            "title": w.title,
            "participants": w.participants,
            "status": w.status,
            "last_update_at": w.last_update_at.isoformat() if w.last_update_at else None,
        }
        for w in wars
    ]


# ── Logs ─────────────────────────────────────────────────────────────

@router.get("/logs", dependencies=[Depends(admin_guard)])
def list_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    account_id: int | None = Query(None),
):
    audit_q = select(AuditLog).order_by(AuditLog.id.desc())
    worker_q = select(WorkerLog).order_by(WorkerLog.id.desc())

    if account_id is not None:
        audit_q = audit_q.where(AuditLog.account_id == account_id)

    audit_q = audit_q.offset(skip).limit(limit)
    worker_q = worker_q.offset(skip).limit(limit)

    audit_rows = list(db.scalars(audit_q).all())
    worker_rows = list(db.scalars(worker_q).all())

    return {
        "audit": [
            {
                "id": a.id,
                "account_id": a.account_id,
                "action": a.action,
                "status": a.status,
                "details": a.details,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in audit_rows
        ],
        "worker": [
            {
                "id": w.id,
                "level": w.level,
                "event": w.event,
                "payload": w.payload,
                "created_at": w.created_at.isoformat() if w.created_at else None,
            }
            for w in worker_rows
        ],
    }
