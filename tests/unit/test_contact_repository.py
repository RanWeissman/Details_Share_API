from datetime import date

from sqlmodel import Session

from src.models.contact import Contact
from src.database.contact_repository import ContactRepository


def make_contact(
    id_: int,
    name: str,
    email: str,
    dob: date,
    owner_id: int = 1,
    is_active: bool = True,
) -> Contact:
    return Contact(
        id=id_,
        name=name,
        email=email,
        date_of_birth=dob,
        owner_id=owner_id,
        is_active=is_active,
    )


def test_add_returned_and_get_by_id(contact_repo: ContactRepository, session: Session):
    today = date.today()
    id_1 = 1
    name_1 = "Ran"
    email_1 = "ran@example.com"
    owner_id_1 = 10
    c = make_contact(
        id_=id_1,
        name=name_1,
        email=email_1,
        dob=today,
        owner_id=owner_id_1,
    )

    saved_contact = contact_repo.add(c)

    assert saved_contact.id == id_1
    assert saved_contact.name == name_1

    from_db = contact_repo.get_by_id(id_1)
    assert from_db is not None
    assert from_db.email == email_1
    assert from_db.owner_id == owner_id_1


def test_check_id_and_email_true_if_id_exists(contact_repo: ContactRepository):
    today = date.today()
    same_id = 1
    c = make_contact(
        id_=same_id,
        name="A",
        email="a@example.com",
        dob=today,
        owner_id=1,
    )
    contact_repo.add(c)

    exists = contact_repo.check_id_and_email(id_1=same_id, email_norm="other@example.com")
    assert exists is True


def test_check_id_and_email_true_if_email_exists(contact_repo: ContactRepository):
    today = date.today()
    same_email = "b@example.com"
    c = make_contact(
        id_=1,
        name="B",
        email=same_email,
        dob=today,
        owner_id=1,
    )
    contact_repo.add(c)

    exists = contact_repo.check_id_and_email(id_1=999, email_norm=same_email)
    assert exists is True


def test_check_id_and_email_false_if_not_exists(contact_repo: ContactRepository):
    exists = contact_repo.check_id_and_email(id_1=123, email_norm="none@example.com")
    assert exists is False

def test_get_all_returns_all_contacts(contact_repo: ContactRepository):
    today = date.today()
    c1 = make_contact(1, "C1", "c1@example.com", today, owner_id=1)
    c2 = make_contact(2, "C2", "c2@example.com", today, owner_id=2)
    c3 = make_contact(3, "C3", "c3@example.com", today, owner_id=2)

    contact_repo.add(c1)
    contact_repo.add(c2)
    contact_repo.add(c3)

    all_contacts = contact_repo.get_all()
    ids = {c.id for c in all_contacts}

    assert len(all_contacts) == 3
    assert ids == {1, 2, 3}


def test_delete_by_id_not_same_owner(contact_repo: ContactRepository, session: Session):
    today = date.today()
    same_id = 1
    c = make_contact(same_id, "Del", "del@example.com", today, owner_id=1)
    contact_repo.add(c)

    deleted = contact_repo.delete_by_id_and_owner(contact_id=same_id, owner_id=2)
    assert deleted is False
    remaining = session.get(Contact, same_id)
    assert remaining is not None

def test_delete_by_id_not_same_id(contact_repo: ContactRepository, session: Session):
    today = date.today()
    same_owner = 1
    c = make_contact(1, "Del", "del@example.com", today, owner_id=same_owner)
    contact_repo.add(c)

    deleted = contact_repo.delete_by_id_and_owner(contact_id=2, owner_id=same_owner)
    assert deleted is False
    remaining = session.get(Contact, 1)
    assert remaining is not None

def test_delete_by_id_and_owner_success(contact_repo: ContactRepository, session: Session):
    today = date.today()
    id_same = 1
    owner_same = 10
    c = make_contact(id_same, "Del", "del@example.com", today, owner_id=owner_same)
    contact_repo.add(c)

    deleted = contact_repo.delete_by_id_and_owner(contact_id=id_same, owner_id=owner_same)
    assert deleted is True

    remaining = session.get(Contact, id_same)
    assert remaining is None

def test_delete_by_id_and_owner_non_existing(contact_repo: ContactRepository):
    deleted = contact_repo.delete_by_id_and_owner(contact_id=12345, owner_id=1)
    assert deleted is False


def test_get_contacts_above_age(contact_repo: ContactRepository):
    today = date.today()
    owner_id = 1
    c30 = make_contact(
        id_=1,
        name="C30",
        email="c30@example.com",
        dob=today.replace(year=today.year - 30),
        owner_id=owner_id,
    )
    c20 = make_contact(
        id_=2,
        name="C20",
        email="c20@example.com",
        dob=today.replace(year=today.year - 20),
        owner_id=owner_id,
    )
    c10 = make_contact(
        id_=3,
        name="C10",
        email="c10@example.com",
        dob=today.replace(year=today.year - 10),
        owner_id=owner_id,
    )

    contact_repo.add(c30)
    contact_repo.add(c20)
    contact_repo.add(c10)

    result = contact_repo.get_contacts_above_age(age=18)
    ids = {c.id for c in result}

    assert ids == {1, 2}


def test_get_contacts_between_age(contact_repo: ContactRepository):
    today = date.today()
    owner_id = 1

    c40 = make_contact(
        id_=1,
        name="C40",
        email="c40@example.com",
        dob=today.replace(year=today.year - 40),
        owner_id=owner_id,
    )
    c25 = make_contact(
        id_=2,
        name="C25",
        email="c25@example.com",
        dob=today.replace(year=today.year - 25),
        owner_id=owner_id,
    )
    c15 = make_contact(
        id_=3,
        name="C15",
        email="c15@example.com",
        dob=today.replace(year=today.year - 15),
        owner_id=owner_id,
    )

    contact_repo.add(c40)
    contact_repo.add(c25)
    contact_repo.add(c15)

    result = contact_repo.get_contacts_between_age(min_age=18, max_age=30)
    ids = {c.id for c in result}

    assert ids == {2}

