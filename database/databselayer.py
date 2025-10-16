
from sqlmodel import SQLModel, create_engine, Session, select

from typing import Type, List, Optional

from datetime import date


class DatabaseLayer:

    _engine = None  # Static variable to hold the engine

    def __init__(self, db_url: Optional[str] = None):
        if DatabaseLayer._engine is None:
            if not db_url:
                db_url = "sqlite:///ourDB.db"  # default SQLite
            DatabaseLayer._engine = create_engine(db_url)
            SQLModel.metadata.create_all(DatabaseLayer._engine)
        self.engine = DatabaseLayer._engine


    def get_session(self) -> Session:
        return Session(self.engine)

    def check_id_and_email(self, model: Type[SQLModel], id: int, email: str) -> bool:
        with self.get_session() as session:
            statement = select(model).where((model.id == id) | (model.email == email))
            result = session.exec(statement).first()
            return result is not None

    def add(self, obj: SQLModel)-> SQLModel:
        with self.get_session() as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def delete(self, model: Type[SQLModel], obj_id: int) -> bool:
        with self.get_session() as session:
            db_obj = session.get(model, obj_id)
            if not db_obj:
                return False
            session.delete(db_obj)
            session.commit()
            return True

    def get_all(self, model: Type[SQLModel]) -> List[SQLModel]:
        with self.get_session() as session:
            results = list(session.exec(select(model)).all())
            return results


    def get_users_above_age(self, model: Type[SQLModel], age: int) -> List[SQLModel]:
        with self.get_session() as session:
            today = date.today()
            cutoff_date = date(today.year - age, today.month, today.day)
            statement = select(model).where(model.date_of_birth <= cutoff_date)
            results = list(session.exec(statement).all())
            return results

    def get_users_between_age(self, model: Type[SQLModel], min_age: int, max_age: int) -> List[SQLModel]:
        with self.get_session() as session:
            today = date.today()

            max_birth_date = date(today.year - min_age, today.month, today.day)

            min_birth_date = date(today.year - max_age, today.month, today.day)
            statement = select(model).where(
                (model.date_of_birth >= min_birth_date) &
                (model.date_of_birth <= max_birth_date)
            )
            results = list(session.exec(statement).all())
            return results

