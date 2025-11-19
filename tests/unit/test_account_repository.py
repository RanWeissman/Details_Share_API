from sqlmodel import Session

from src.models.account import Account
from src.database.account_repository import AccountsRepository


def test_create_account_persists_and_returns_account(accounts_repo: AccountsRepository, session: Session):
    username_1 = "ran"
    email_1 = "ran@example.com"
    returned_account = accounts_repo.create_account(
        username=username_1,
        email=email_1,
        hashed_password="hashed_pw",
    )

    assert returned_account.id is not None
    assert returned_account.username == username_1
    assert returned_account.email == email_1

    account_from_db = session.get(Account, returned_account.id)
    assert account_from_db is not None
    assert account_from_db.username == username_1


def test_add_existing_account(accounts_repo: AccountsRepository, session: Session):
    username_1 = "john"
    account_1 = Account(username=username_1, email="john@example.com", hashed_password="pwd")
    result = accounts_repo.add(account_1)

    assert result is account_1
    assert account_1.id is not None

    loaded = session.get(Account, account_1.id)
    assert loaded is not None
    assert loaded.username == username_1


def test_check_mail_and_username_returns_true_if_email_exists(accounts_repo: AccountsRepository):
    username_1 = "user1"
    email_1 = "user1@example.com"
    accounts_repo.create_account(
        username=username_1,
        email=email_1,
        hashed_password="pw",
    )
    username_2 = "other_username"
    exists = accounts_repo.check_mail_and_username(
        email_norm=email_1,
        username=username_2,
    )
    assert exists is True

    email_2 = "otheruser@example.com"
    exists = accounts_repo.check_mail_and_username(
        email_norm=email_2,
        username=username_1,
    )
    assert exists is True

    exists = accounts_repo.check_mail_and_username(
        email_norm="not_there@example.com",
        username="no_user",
    )
    assert exists is False

def test_check_mail_and_username_returns_false_if_not_exists(accounts_repo: AccountsRepository):
    exists = accounts_repo.check_mail_and_username(
        email_norm="not_there@example.com",
        username="no_user",
    )
    assert exists is False


def test_get_by_username_and_email(accounts_repo: AccountsRepository):
    acc = accounts_repo.create_account(
        username="alice",
        email="alice@example.com",
        hashed_password="pw",
    )

    by_username = accounts_repo.get_by_username("alice")
    by_email = accounts_repo.get_by_email("alice@example.com")

    assert by_username is not None
    assert by_email is not None
    assert by_username.id == acc.id
    assert by_email.id == acc.id


def test_get_all_returns_all_accounts(accounts_repo: AccountsRepository):
    accounts_repo.create_account("u1", "u1@example.com", "pw1")
    accounts_repo.create_account("u2", "u2@example.com", "pw2")

    all_accounts = accounts_repo.get_all()
    usernames = {a.username for a in all_accounts}

    assert len(all_accounts) == 2
    assert usernames == {"u1", "u2"}


def test_delete_by_id_non_existing(accounts_repo: AccountsRepository):
    deleted = accounts_repo.delete_by_id(9999)
    assert deleted is False


def test_delete_by_username_existing(accounts_repo: AccountsRepository, session: Session):
    username_1 = "to_delete2"
    accounts_repo.create_account(username_1, "del2@example.com", "pw")

    deleted = accounts_repo.delete_by_username(username_1)
    assert deleted is True

    from_db = accounts_repo.get_by_username(username_1)
    assert from_db is None


def test_exists_username_or_email(accounts_repo: AccountsRepository):
    accounts_repo.create_account("bob", "bob@example.com", "pw")

    assert accounts_repo.exists_username_or_email("bob", "other@example.com") is True
    assert accounts_repo.exists_username_or_email("other", "bob@example.com") is True
    assert accounts_repo.exists_username_or_email("nope", "nope@example.com") is False

def test_delete_by_id_existing_returns_true(accounts_repo: AccountsRepository, session: Session):
    # Arrange: create an account so delete_by_id hits the "found" branch
    acc = accounts_repo.create_account(
        username="to_delete",
        email="to_delete@example.com",
        hashed_password="pw",
    )
    deleted = accounts_repo.delete_by_id(acc.id)
    assert deleted is True


def test_delete_by_username_non_existing_returns_false(accounts_repo: AccountsRepository):
    deleted = accounts_repo.delete_by_username("no_such_user")
    assert deleted is False
