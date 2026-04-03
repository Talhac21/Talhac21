from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    alias: str = Field(min_length=3, max_length=80)


class AccountOut(BaseModel):
    id: int
    alias: str
    enabled: bool
    session_status: str
    last_sync_at: datetime | None
    last_session_check_at: datetime | None

    model_config = {"from_attributes": True}


class SessionBootstrapIn(BaseModel):
    session_json: str = Field(min_length=10)


class PerkRunResult(BaseModel):
    success: bool
    message: str
    next_run_at: datetime | None


class DashboardCard(BaseModel):
    account_id: int
    alias: str
    enabled: bool
    session_status: str
    auto_perk_enabled: bool
    next_run_at: datetime | None
    last_result: str
    time_remaining_seconds: int | None


class DashboardOut(BaseModel):
    accounts: list[DashboardCard]
    recent_logs: list[dict[str, Any]]
    generated_at: datetime
