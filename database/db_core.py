from typing import Optional
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine


DB_URL = "sqlite:///ourDB.db"

class DBCore:
    _engine: Optional[Engine] = None
    _sessionMaker: Optional[sessionmaker] = None

    def __init__(self, db_url: Optional[str] = None) -> None:
        url = db_url or DB_URL

        if DBCore._engine is None:
            ## create engine
            DBCore._engine = create_engine(
                url,
                connect_args={"check_same_thread": False}  # Needed for SQLite
            )
            ## create tables
            SQLModel.metadata.create_all(DBCore._engine)
            ## create session factory
            DBCore._sessionMaker = sessionmaker(
                bind=DBCore._engine,
                class_=Session,
                autoflush=False,
                autocommit=False,
            )

        self._engine = DBCore._engine
        self._sessionMaker=DBCore._sessionMaker

    def __del__(self) -> None:
        self._engine.dispose()

    # def get_session(self) -> Optional[Session]:
    def get_session(self):
        if self._sessionMaker is not None:
            return self._sessionMaker()
        return None

    @classmethod
    def dispose(cls) -> None:
        if cls._engine is not None:
            cls._engine.dispose()
        cls._engine = None
        cls._sessionMaker = None
