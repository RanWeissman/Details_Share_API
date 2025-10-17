# app/core/database.py
from __future__ import annotations
from typing import Type, TypeVar, Generic, Optional, List, Any
from sqlmodel import SQLModel, create_engine, Session, select

T = TypeVar("T", bound=SQLModel)

class DatabaseLayer(Generic[T]):
    _engine = None

    def __init__(self, db_url: Optional[str] = None):
        if DatabaseLayer._engine is None:
            db_url = db_url or "sqlite:///ourDB.db"
            DatabaseLayer._engine = create_engine(db_url)
            SQLModel.metadata.create_all(DatabaseLayer._engine)
        self.engine = DatabaseLayer._engine

    def get_session(self) -> Session:
        return Session(self.engine)

    def add(self, obj: T) -> T:
        with self.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def get_by_id(self, model: Type[T], obj_id: Any) -> Optional[T]:
        with self.get_session() as session:
            return session.get(model, obj_id)

    def delete(self, model: Type[T], obj_id: Any) -> bool:
        with self.get_session() as session:
            db_obj = session.get(model, obj_id)
            if not db_obj:
                return False
            session.delete(db_obj)
            session.commit()
            return True

    def get_all(self, model: Type[T]) -> List[T]:
        with self.get_session() as session:
            return list(session.exec(select(model)).all())
