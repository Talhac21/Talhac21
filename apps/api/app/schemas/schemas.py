import json
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("session_json")
    @classmethod
    def validate_json(cls, v: str) -> str:
        try:
            json.loads(v)
        except json.JSONDecodeError as exc:
            raise ValueError("session_json must be valid JSON") from exc
        return v


class PerkRunResult(BaseModel):
    success: bool
    message: str
    next_run_at: datetime | None


class PerkToggleIn(BaseModel):
    auto_enabled: bool
