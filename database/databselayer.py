from typing import Optional
from sqlmodel import SQLModel, create_engine, Session


class DatabaseLayer:
    _engine = None  # Static variable to hold the engine

    def __init__(self, db_url: Optional[str] = None):
        if DatabaseLayer._engine is None:
            if not db_url:
                db_url = "sqlite:///ourDB.db"
            DatabaseLayer._engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False}  # Needed for SQLite
            )
            SQLModel.metadata.create_all(DatabaseLayer._engine)
        self.engine = DatabaseLayer._engine

    def get_session(self) -> Session:
        return Session(self.engine)
