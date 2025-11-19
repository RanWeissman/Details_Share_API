import pytest
from sqlmodel import Session

from src.database.db_core import DBCore

from tests.conftest import TEST_DB_URL

def test_dc_creates_engine_and_session_maker():
    # internal attributes should exist and not be None
    db_core = DBCore(db_url=TEST_DB_URL)
    assert hasattr(db_core, "_engine")
    assert hasattr(db_core, "_sessionMaker")
    assert db_core._engine is not None
    assert db_core._sessionMaker is not None
    assert DBCore._instance is True

def test_dc_check_session_instance_and_from_engine():
    # השתמש בשם שונה, לדוגמה: current_session
    db_core = DBCore(db_url=TEST_DB_URL)
    current_session = db_core.get_session()

    assert isinstance(current_session, Session)
    assert current_session.bind is db_core._engine

    # השתמש בשם שונה, לדוגמה: session_two
    session_two = db_core.get_session()

    assert isinstance(session_two, Session)
    assert session_two is not current_session
    assert session_two.bind is db_core._engine

def test_dc_singleton_instance():
    _first = DBCore(db_url=TEST_DB_URL)
    with pytest.raises(ValueError) as exc_info:
        DBCore(db_url=TEST_DB_URL)
    assert "singleton" in str(exc_info.value).lower()


def test_dc_engine_same_url():
    db_core = DBCore(db_url=TEST_DB_URL)

    assert str(db_core._engine.url) == TEST_DB_URL


def test_dc_del_resets_singleton_flag():
    db_core = DBCore(db_url=TEST_DB_URL)
    assert DBCore._instance is True

    # explicitly call __del__ (easier to control than relying on GC)
    db_core.__del__()

    assert DBCore._instance is False

def test_db_get_session_returns_none_when_sessionmaker_missing():
    # Create a DBCore instance *without* calling __init__
    db_core = object.__new__(DBCore)
    db_core._sessionMaker = None # Note: assuming the internal attribute is _sessionMaker

    result_session = db_core.get_session()

    assert result_session is None