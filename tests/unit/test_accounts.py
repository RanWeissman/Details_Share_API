import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from src.api.accounts import accounts_router
from src.api.contacts import contacts_router
from src.core.db_global import get_session
from src.core.api_globals import security as global_security
from src.database.account_repository import AccountsRepository



@pytest.fixture
def app(engine):
    app = FastAPI()
    def override_get_session():
        session = Session(engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.include_router(accounts_router)
    app.include_router(contacts_router)
    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture
def client(app):

    with TestClient(app, follow_redirects=False) as c:
        yield c



def create_account_in_db(
    engine,
    username: str,
    email: str,
    password: str,
    is_active: bool = True,
):

    hashed = global_security.get_password_hash(password)

    with Session(engine) as session:
        repo = AccountsRepository(session)
        acc = repo.create_account(
            username=username,
            email=email,
            hashed_password=hashed,
        )
        acc.is_active = is_active
        session.add(acc)
        session.commit()
        session.refresh(acc)
        return acc



def test_show_homepage(client: TestClient):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Welcome" in resp.text


def test_menu_after_login_page(client: TestClient):
    resp = client.get("/menu")
    assert resp.status_code == 200
    assert "Show All Contacts" in resp.text


def test_account_create_page(client: TestClient):
    resp = client.get("/pages/account/signup")
    assert resp.status_code == 200
    assert "/api/account/signup" in resp.text


def test_account_login_page(client: TestClient):
    resp = client.get("/pages/account/login")
    assert resp.status_code == 200
    assert "/api/account/login" in resp.text



def test_signup_account_creates_new_account(client: TestClient, engine):
    data = {
        "username": "ran",
        "email": "ran@example.com",
        "password": "secret123",
    }

    resp = client.post("/api/account/signup", data=data)
    assert resp.status_code == 201

    with Session(engine) as session:
        repo = AccountsRepository(session)
        acc = repo.get_by_username("ran")
        assert acc is not None
        assert acc.email == "ran@example.com"


def test_signup_account_duplicate_username_or_email_returns_error(
    client: TestClient,
    engine,
):
    create_account_in_db(
        engine,
        username="ran",
        email="ran@example.com",
        password="secret123",
    )

    data = {
        "username": "ran",
        "email": "ran@example.com",
        "password": "another",
    }

    resp = client.post("/api/account/signup", data=data)
    assert resp.status_code == 400
    assert "Account with this ID or Email already exists" in resp.text




def test_login_success_sets_cookie_and_redirects_to_menu(client: TestClient, engine):
    create_account_in_db(
        engine,
        username="ran",
        email="ran@example.com",
        password="secret123",
        is_active=True,
    )

    resp = client.post(
        "/api/account/login",
        data={"username": "ran", "password": "secret123"},
    )

    assert resp.status_code == 303
    assert resp.headers["location"].endswith("/menu")

    set_cookie_header = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie_header


def test_login_failed_wrong_password_renders_fail_template(client: TestClient, engine):
    create_account_in_db(
        engine,
        username="ran",
        email="ran@example.com",
        password="secret123",
        is_active=True,
    )

    resp = client.post(
        "/api/account/login",
        data={"username": "ran", "password": "wrong_password"},
    )

    assert resp.status_code == 200
    assert "set-cookie" not in resp.headers


def test_login_failed_inactive_account(client: TestClient, engine):
    create_account_in_db(
        engine,
        username="ran",
        email="ran@example.com",
        password="secret123",
        is_active=False,
    )

    resp = client.post(
        "/api/account/login",
        data={"username": "ran", "password": "secret123"},
    )

    assert resp.status_code == 200
    assert "set-cookie" not in resp.headers


def test_logout_redirects_to_home_and_deletes_cookie(client: TestClient):
    client.cookies.set("access_token", "dummy_token")

    resp = client.get(
        "/account/logout",
        follow_redirects=False,
    )

    assert resp.status_code == 303
    deleted = resp.cookies.get("access_token")
    assert deleted in (None, "", "null")
