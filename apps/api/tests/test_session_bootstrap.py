from app.models.models import Account, SessionStatus
from app.services.account_service import bootstrap_session, create_account


class DummyResult:
    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message


class DummyClient:
    def validate_session(self, _payload: str):
        return DummyResult("valid", "ok")


def test_bootstrap_encrypts_and_sets_valid(db_session, monkeypatch):
    monkeypatch.setattr("app.services.account_service.RRClient", lambda: DummyClient())
    account = create_account(db_session, "acc1")
    updated = bootstrap_session(db_session, account, '{"cookies": [{"name":"a","value":"b"}]}')
    assert updated.encrypted_session is not None
    assert updated.encrypted_session != '{"cookies": [{"name":"a","value":"b"}]}'
    assert updated.session_status == SessionStatus.valid
