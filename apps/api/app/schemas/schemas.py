from datetime import datetime

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    alias: str = Field(min_length=3, max_length=80)


class AccountOut(BaseModel):
    id: int
    alias: str
    enabled: bool
    session_status: str
    last_sync_at: datetime | None

    class Config:
        from_attributes = True


class SessionBootstrapIn(BaseModel):
    session_json: str = Field(min_length=10)


class PerkRunResult(BaseModel):
    success: bool
    message: str
    next_run_at: datetime | None
