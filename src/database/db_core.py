from typing import Optional
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

DB_URL = "sqlite:///ourDB.db"

class DBCore:
    _instance: Optional[bool] = False

    def __init__(self, db_url: Optional[str] = None) -> None:
        if DBCore._instance:
            raise ValueError("DBCore is a singleton class. Use the existing instance.")
        url = db_url or DB_URL

        ## create engine
        self._engine = create_engine(
            url,
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
        ## create tables
        SQLModel.metadata.create_all(self._engine)
        ## create session factory
        self._sessionMaker = sessionmaker(
            bind=self._engine,
            class_=Session,
            autoflush=False,
            autocommit=False,
        )
        DBCore._instance = True
    def __del__(self) -> None:
        self._engine.dispose()
        DBCore._instance = False

    def get_session(self):
        if self._sessionMaker is not None:
            return self._sessionMaker()
        return None

