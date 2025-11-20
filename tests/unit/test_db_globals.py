import pytest
from typing import cast, Any

from src.core import db_global


class FakeSession:
    def __init__(self):
        self.commit_called = False
        self.rollback_called = False
        self.close_called = False

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

    def close(self):
        self.close_called = True


class FakeDBCore:
    def __init__(self):
        self.session = FakeSession()
        self.get_session_called = False

    def get_session(self):
        self.get_session_called = True
        return self.session


def test_get_session_happy_path_commits_and_closes(monkeypatch):
    fake_db = FakeDBCore()
    monkeypatch.setattr(db_global, "db", fake_db)

    gen = db_global.get_session()

    fake_session = cast(FakeSession, cast(object, next(gen)))

    assert fake_session is fake_db.session
    assert fake_db.get_session_called is True

    with pytest.raises(StopIteration):
        next(gen)

    assert fake_session.commit_called is True
    assert fake_session.rollback_called is False
    assert fake_session.close_called is True


def test_get_session_exception_path_rolls_back_and_closes(monkeypatch):
    fake_db = FakeDBCore()
    monkeypatch.setattr(db_global, "db", fake_db)

    gen: Any = db_global.get_session()

    fake_session = cast(FakeSession, cast(object, next(gen)))
    assert fake_session is fake_db.session

    with pytest.raises(RuntimeError):
        gen.throw(RuntimeError("test_db_globals_exception"))

    assert fake_session.commit_called is False
    assert fake_session.rollback_called is True
    assert fake_session.close_called is True
