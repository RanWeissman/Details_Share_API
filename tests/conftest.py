import pytest
from sqlalchemy import create_engine, StaticPool
from sqlmodel import SQLModel, Session

from src.database.account_repository import AccountsRepository
from src.database.contact_repository import ContactRepository
from src.database.db_core import DBCore

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def reset_db_core_singleton():
    DBCore._instance = False
    yield
    DBCore._instance = False


@pytest.fixture
def engine():

    engine = create_engine(
        "sqlite://",  # in-memory
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import src.models.account  # noqa: F401
    import src.models.contact  # noqa: F401

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


'''
 py -m pytest --cov=src --cov-report=term-missing
'''