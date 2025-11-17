from typing import Iterator

from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from src.database import db_core

templates = Jinja2Templates(directory="src/templates")

db = db_core.DBCore()

def get_session() -> Iterator[Session]:
    s = db.get_session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()
