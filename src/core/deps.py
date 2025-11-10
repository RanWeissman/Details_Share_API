# src/core/deps.py
from typing import Generator

from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from src.database import db_core as db_module

db = db_module.DBCore()

templates = Jinja2Templates(directory="src/templates")


def get_session() -> Generator[Session, None, None]:
    s = db.get_session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
