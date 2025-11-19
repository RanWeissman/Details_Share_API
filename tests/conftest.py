import pytest
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from src.database.account_repository import AccountsRepository
from src.database.contact_repository import ContactRepository
from src.database.db_core import DBCore

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def reset_db_core_singleton():
    # Automatically reset DBCore._instance before and after each test.
    DBCore._instance = False
    yield
    DBCore._instance = False


@pytest.fixture
def engine():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )
    # create tables for all SQLModel models (including Account)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def accounts_repo(session):
    return AccountsRepository(session=session)


@pytest.fixture
def contact_repo(session):
    return ContactRepository(session=session)


