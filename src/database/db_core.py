from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

from src.core.settings import get_settings

settings = get_settings()

DB_URL = settings.database_url

class DBCore:
    _instance: bool = False

    def __init__(self, db_url: str = None) -> None:
        if DBCore._instance:
            raise ValueError("DBCore is a singleton class. Use the existing instance.")
        url = db_url or DB_URL

        # initialize attributes early so partial initialization doesn't break __del__
        self._engine = None
        self._sessionMaker = None

        try:
            ## create engine
            # For PostgreSQL we don't need the SQLite-only `check_same_thread` arg.
            self._engine = create_engine(
                url,
                echo=False,
                pool_pre_ping=True,
            )

            # Import models to ensure they are registered in SQLModel metadata
            from src.models.contact import Contact  # noqa: F401
            from src.models.account import Account  # noqa: F401

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
        except Exception:
            # make sure we don't leave the class marked as initialized on failure
            DBCore._instance = False
            # re-raise so callers can handle/log the error if desired
            raise

    def __del__(self) -> None:
        # guard against partially-constructed instances
        try:
            if getattr(self, "_engine", None) is not None:
                self._engine.dispose()
        except Exception:
            # best-effort cleanup; ignore exceptions during interpreter shutdown
            pass
        DBCore._instance = False

    def get_session(self):
        if self._sessionMaker is not None:
            return self._sessionMaker()
        return None
