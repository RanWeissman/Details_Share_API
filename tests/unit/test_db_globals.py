import pytest

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


# ---------- Tests ----------

def test_get_session_happy_path_commits_and_closes(monkeypatch):
    fake_db = FakeDBCore()
    # Override the global `db` in db_global module
    monkeypatch.setattr(db_global, "db", fake_db)

    gen = db_global.get_session()

    # step 1: generator yields the session
    faked_session = next(gen)
    assert faked_session is fake_db.session
    assert fake_db.get_session_called is True

    # step 2: finish the generator normally -> should commit & close
    with pytest.raises(StopIteration):
        next(gen)

    assert faked_session.commit_called is True
    assert faked_session.rollback_called is False
    assert faked_session.close_called is True


def test_get_session_exception_path_rolls_back_and_closes(monkeypatch):
    fake_db = FakeDBCore()
    monkeypatch.setattr(db_global, "db", fake_db) # change the db to the fake db

    gen = db_global.get_session()

    faked_session = next(gen)
    assert faked_session is fake_db.session

    # Now simulate exception inside the body that uses the generator
    with pytest.raises(RuntimeError):
        gen.throw(RuntimeError("test_db_globals_exception"))

    # In exception path: rollback then re-raise, and finally close
    assert faked_session.commit_called is False
    assert faked_session.rollback_called is True
    assert faked_session.close_called is True