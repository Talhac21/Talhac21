from app.services.account_service import MAX_ACCOUNTS


def test_max_accounts_is_two():
    assert MAX_ACCOUNTS == 2
