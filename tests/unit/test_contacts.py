from datetime import date
from typing import Dict, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.main import app as fastapi_app
from src.core.db_global import get_session
from src.core.api_globals import security
from src.models.contact import Contact
from src.database.contact_repository import ContactRepository

app: FastAPI = fastapi_app


@pytest.fixture(autouse=True)
def override_get_session(engine):
    def _get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _get_session_override
    yield
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture(autouse=True)
def override_auth_dependencies():
    def fake_auth_required():
        return None

    class FakeAccount:
        id = 1
        username = "test-user"

    def fake_get_current_contact():
        return FakeAccount()

    app.dependency_overrides[security.auth_required] = fake_auth_required
    app.dependency_overrides[security.get_current_contact] = fake_get_current_contact

    yield

    app.dependency_overrides.pop(security.auth_required, None)
    app.dependency_overrides.pop(security.get_current_contact, None)


@pytest.fixture
def client():
    return TestClient(app)


def create_contact_in_db(
    engine,
    contact_id: int,
    name: str,
    email: str,
    dob: date,
    owner_id: int = 1,
):
    with Session(engine) as session:
        c = Contact(
            id=contact_id,
            name=name,
            email=email,
            date_of_birth=dob,
            owner_id=owner_id,
        )
        session.add(c)
        session.commit()


def test_create_contact_page(client: TestClient):
    response = client.get("/pages/contacts/create")
    assert response.status_code == 200
    assert "<form" in response.text


def test_delete_contact_page(client: TestClient):
    response = client.get("/pages/contacts/delete")
    assert response.status_code == 200
    assert "Delete" in response.text or "delete" in response.text.lower()


def test_filter_menu_page(client: TestClient):
    response = client.get("/pages/filters/menu")
    assert response.status_code == 200
    assert "Filter" in response.text or "filters" in response.text


def test_filter_age_above_page(client: TestClient):
    response = client.get("/pages/filters/age/above")
    assert response.status_code == 200
    assert "age" in response.text.lower()


def test_filter_age_between_page(client: TestClient):
    response = client.get("/pages/filters/age/between")
    assert response.status_code == 200
    assert "age" in response.text.lower()


def test_contacts_create_creates_new_contact(client: TestClient, engine):
    data = {
        "name": "Alice",
        "email": "alice@example.com",
        "id_1": "111",
        "date_of_birth": "1990-01-01",
    }

    response = client.post("/api/contacts/create", data=data)
    assert response.status_code == 201
    assert "Alice" in response.text
    assert "alice@example.com" in response.text


def test_contacts_create_duplicate_id_or_email_returns_error(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=222,
        name="Bob",
        email="bob@example.com",
        dob=date(1995, 5, 5),
        owner_id=1,
    )

    data = {
        "name": "Bob 2",
        "email": "bob@example.com",
        "id_1": "222",
        "date_of_birth": "2000-01-01",
    }

    response = client.post("/api/contacts/create", data=data)
    assert response.status_code == 400
    assert "Contact with this ID or Email already exists" in response.text


def test_get_all_contacts_page_shows_contacts(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=1,
        name="Alice",
        email="alice@example.com",
        dob=date(1990, 1, 1),
    )
    create_contact_in_db(
        engine,
        contact_id=2,
        name="Bob",
        email="bob@example.com",
        dob=date(1985, 2, 2),
    )

    response = client.get("/pages/contacts/all")
    assert response.status_code == 200
    body = response.text
    assert "Alice" in body
    assert "Bob" in body
    assert "No contacts found" not in body


def test_debug_contacts_all_returns_json(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=10,
        name="Charlie",
        email="charlie@example.com",
        dob=date(1980, 3, 3),
    )
    create_contact_in_db(
        engine,
        contact_id=20,
        name="Dana",
        email="dana@example.com",
        dob=date(2000, 4, 4),
    )

    response = client.get("/api/debug/contacts")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    ids = {item["id"] for item in data}
    assert 10 in ids
    assert 20 in ids


def test_get_contacts_json_returns_all_contacts(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=1,
        name="Json Alice",
        email="jsonalice@example.com",
        dob=date(1991, 1, 1),
    )
    create_contact_in_db(
        engine,
        contact_id=2,
        name="Json Bob",
        email="jsonbob@example.com",
        dob=date(1992, 2, 2),
    )

    response = client.get("/api/contacts/all")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    emails = {c["email"] for c in data}
    assert "jsonalice@example.com" in emails
    assert "jsonbob@example.com" in emails

    for item in data:
        assert isinstance(item["date_of_birth"], str)


def test_delete_contact_success_when_owned_by_current_account(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=999,
        name="ToDelete",
        email="del@example.com",
        dob=date(1999, 9, 9),
        owner_id=1,
    )

    response = client.post("/api/contacts/delete", data={"id_1": "999"})
    assert response.status_code == 200

    with Session(engine) as session:
        repo = ContactRepository(session)
        contacts = repo.get_all()
        assert not any(contact.id == 999 for contact in contacts)


def test_delete_contact_not_found_when_not_owned_by_current_account(client: TestClient, engine):
    create_contact_in_db(
        engine,
        contact_id=1000,
        name="NotMine",
        email="notmine@example.com",
        dob=date(1990, 1, 1),
        owner_id=2,
    )

    response = client.post("/api/contacts/delete", data={"id_1": "1000"})
    assert response.status_code == 404

    with Session(engine) as session:
        repo = ContactRepository(session)
        contacts = repo.get_all()
        assert any(contact.id == 1000 for contact in contacts)


def test_contacts_above_show_uses_repo_and_renders_result(client: TestClient, monkeypatch):
    called: Dict[str, Optional[int]] = {"age": None}

    def fake_get_contacts_above_age(_self, age: int):
        called["age"] = age
        return [
            Contact(
                id=1,
                name="Old Alice",
                email="oldalice@example.com",
                date_of_birth=date(1980, 1, 1),
                owner_id=1,
            )
        ]

    monkeypatch.setattr(
        ContactRepository,
        "get_contacts_above_age",
        fake_get_contacts_above_age,
        raising=True,
    )

    response = client.post("/api/filters/age/above", data={"age": "30"})
    assert response.status_code == 200
    assert called["age"] == 30
    body = response.text
    assert "Old Alice" in body


def test_contacts_between_show_uses_repo_and_renders_result(client: TestClient, monkeypatch):
    called: Dict[str, Optional[int]] = {"min_age": None, "max_age": None}

    def fake_get_contacts_between_age(_self, min_age: int, max_age: int):
        called["min_age"] = min_age
        called["max_age"] = max_age
        return [
            Contact(
                id=2,
                name="Mid Bob",
                email="midbob@example.com",
                date_of_birth=date(1990, 6, 6),
                owner_id=1,
            )
        ]

    monkeypatch.setattr(
        ContactRepository,
        "get_contacts_between_age",
        fake_get_contacts_between_age,
        raising=True,
    )

    response = client.post(
        "/api/filters/age/between",
        data={"min_age": "20", "max_age": "40"},
    )
    assert response.status_code == 200
    assert called["min_age"] == 20
    assert called["max_age"] == 40
    body = response.text
    assert "Mid Bob" in body
