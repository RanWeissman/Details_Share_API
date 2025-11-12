from typing import Generator

from fastapi.templating import Jinja2Templates
from sqlmodel import Session

# delay importing db_module.DBCore at module import time to avoid creating
# a DB connection during test/import; create it lazily in get_session.
import importlib

templates = Jinja2Templates(directory="src/templates")

_db_instance = None


def _get_db_module():
    return importlib.import_module("src.database.db_core")


def get_session() -> Generator[Session, None, None]:
    global _db_instance
    if _db_instance is None:
        db_module = _get_db_module()
        _db_instance = db_module.DBCore()

    s = _db_instance.get_session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
