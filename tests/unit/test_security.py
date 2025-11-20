import pytest
from sqlmodel import Session
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone

from src.core.security import Security
from src.models.account import Account
from src.database.account_repository import AccountsRepository


@pytest.fixture
def security():
    return Security()


@pytest.fixture
def assert_auth_failure(security: Security, session: Session):
    def _assert(request: 'DummyRequest', expected_detail: str):
        with pytest.raises(HTTPException) as exc_info:
            security.get_current_contact(request, session)  # type: ignore

        exc = exc_info.value
        assert exc.status_code == 303
        assert exc.detail == expected_detail
        assert exc.headers.get("Location") == "/pages/account/login"

    return _assert

class DummyRequest:
    """Minimal stand-in for FastAPI Request: only .cookies is needed."""
    def __init__(self, cookies: dict):
        self.cookies = cookies


def test_get_password_hash_and_verify(security: Security):
    password = "my_secret_password"
    hashed_pass = security.get_password_hash(password)

    assert isinstance(hashed_pass, str)
    assert hashed_pass != password
    assert security.verify_password(password, hashed_pass) is True
    assert security.verify_password("wrong_password", hashed_pass) is False

def test_create_access_token_contains_sub_and_extra(security: Security):
    sub = "123"
    role = "user"
    token = security.create_access_token(
        sub=sub,
        extra={"role": role},
        minutes=1,
    )

    decoded = jwt.decode(
        token,
        security._secret_key,
        algorithms=[security._algorithm],
    )

    assert decoded["sub"] == sub
    assert decoded["role"] == role
    assert "exp" in decoded
    assert "iat" in decoded
    assert decoded["exp"] > decoded["iat"]


def test_get_current_contact_returns_account_on_valid_token(
    security: Security,
    session: Session,
    accounts_repo: AccountsRepository,
):
    acc = accounts_repo.create_account(
        username="ran",
        email="ran@example.com",
        hashed_password="hashed_pw",
    )

    token = security.create_access_token(
        sub=str(acc.id),
        extra={"id": acc.id},
        minutes=5,
    )

    request = DummyRequest(cookies={"access_token": token})

    current = security.get_current_contact(request, session) # type: ignore

    assert isinstance(current, Account)
    assert current.id == acc.id
    assert current.username == "ran"



def test_get_current_contact_raises_if_no_cookie(security: Security, assert_auth_failure):
    request = DummyRequest(cookies={})
    assert_auth_failure(request, expected_detail="Not authenticated")

def test_get_current_contact_raises_on_invalid_token(security: Security, assert_auth_failure):
    request = DummyRequest(cookies={"access_token": "not_a_real_jwt"})
    assert_auth_failure(request, expected_detail="Invalid or expired token")


def test_get_current_contact_raises_if_contact_not_found(security: Security, assert_auth_failure):
    token = security.create_access_token(sub="9999", extra={"id": 9999}, minutes=5)
    request = DummyRequest(cookies={"access_token": token})
    assert_auth_failure(request, expected_detail="contact inactive or not found")


def test_get_current_contact_raises_if_contact_inactive(
    security: Security,
    session: Session,
    accounts_repo: AccountsRepository,
    assert_auth_failure,
):
    inactive = Account(
        username="inactive",
        email="inactive@example.com",
        hashed_password="pw",
        is_active=False,
    )
    accounts_repo.add(inactive)

    token = security.create_access_token(sub=str(inactive.id), extra={"id": inactive.id}, minutes=5)
    request = DummyRequest(cookies={"access_token": token})
    assert_auth_failure(request, expected_detail="contact inactive or not found")


def test_auth_required_does_nothing_when_current_contact_provided(security: Security):
    dummy_account = Account(
        username="some_user",
        email="u@example.com",
        hashed_password="pw",
    )

    result = security.auth_required(current_contact=dummy_account) #ignire: ignore

    assert result is None

def test_get_current_contact_raises_if_token_payload_missing_id_and_sub(
    security: Security,
    assert_auth_failure,
):
    now = datetime.now(timezone.utc)
    payload = {
        "foo": "bar",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=5)).timestamp()),
    }
    token = jwt.encode(payload, security._secret_key, algorithm=security._algorithm)

    request = DummyRequest(cookies={"access_token": token})

    assert_auth_failure(request, expected_detail="Invalid token payload")


def test_get_current_contact_handles_non_int_id_in_token(
    security: Security,
    assert_auth_failure,
):
    token = security.create_access_token(
        sub="not-an-int",
        minutes=5,
    )

    request = DummyRequest(cookies={"access_token": token})
    assert_auth_failure(request, expected_detail="contact inactive or not found")