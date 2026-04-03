import json

from app.services.account_service import MAX_ACCOUNTS
from app.schemas.schemas import SessionBootstrapIn


def test_max_accounts_is_two():
    assert MAX_ACCOUNTS == 2


def test_session_bootstrap_rejects_invalid_json():
    """SessionBootstrapIn should reject non-JSON strings."""
    try:
        SessionBootstrapIn(session_json="not-valid-json-at-all")
        assert False, "Should have raised"
    except Exception:
        pass


def test_session_bootstrap_accepts_valid_json():
    """SessionBootstrapIn should accept valid JSON."""
    valid = json.dumps({"cookies": [], "origins": []})
    obj = SessionBootstrapIn(session_json=valid)
    assert obj.session_json == valid
