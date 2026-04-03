import pytest

from app.services.account_service import create_account


def test_max_two_accounts(db_session):
    create_account(db_session, "first")
    create_account(db_session, "second")
    with pytest.raises(ValueError):
        create_account(db_session, "third")
