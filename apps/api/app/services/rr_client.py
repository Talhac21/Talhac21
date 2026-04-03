import json
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

from app.core.config import settings


@dataclass
class SessionCheckResult:
    status: str
    message: str


@dataclass
class PerkStatusResult:
    status: str
    next_run_at: datetime | None
    details: dict


class RRClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def _cookies_from_storage(self, storage_state: str) -> dict[str, str]:
        parsed = json.loads(storage_state)
        cookies = {}
        for item in parsed.get("cookies", []):
            name = item.get("name")
            value = item.get("value")
            if name and value:
                cookies[name] = value
        return cookies

    def validate_session(self, storage_state: str) -> SessionCheckResult:
        try:
            cookies = self._cookies_from_storage(storage_state)
        except json.JSONDecodeError:
            return SessionCheckResult(status="invalid", message="storage_state is not valid JSON")

        if not cookies:
            return SessionCheckResult(status="invalid", message="no cookies found in storage_state")

        try:
            with httpx.Client(base_url=settings.rr_base_url, timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get("/", cookies=cookies)
        except httpx.HTTPError as exc:
            return SessionCheckResult(status="unknown", message=f"network error: {exc}")

        if resp.status_code >= 400:
            return SessionCheckResult(status="invalid", message=f"rr returned status {resp.status_code}")

        text = resp.text.lower()
        if "logout" in text or "profile" in text:
            return SessionCheckResult(status="valid", message="session appears authenticated")
        if "login" in text or "sign in" in text:
            return SessionCheckResult(status="invalid", message="login page detected")
        return SessionCheckResult(status="unknown", message="could not confidently determine auth state")

    def fetch_perk_status(self, storage_state: str) -> PerkStatusResult:
        validation = self.validate_session(storage_state)
        if validation.status != "valid":
            return PerkStatusResult(status="blocked", next_run_at=None, details={"reason": validation.message})

        return PerkStatusResult(
            status="unsupported",
            next_run_at=None,
            details={
                "reason": "perk page parsing is disabled in v1 without stable selectors",
                "checked_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def run_perk(self, storage_state: str) -> PerkStatusResult:
        perk_status = self.fetch_perk_status(storage_state)
        if perk_status.status == "blocked":
            return perk_status
        return PerkStatusResult(
            status="unsupported",
            next_run_at=None,
            details={"reason": "manual perk execution endpoint is not safely available in v1"},
        )
