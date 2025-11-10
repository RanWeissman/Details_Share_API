from typing import Type, List
from datetime import date

from dateutil.relativedelta import relativedelta
from sqlmodel import Session, SQLModel, select

class ContactRepository:
    def __init__(self, session: Session):
        self.session = session

    def check_id_and_email(self, model: Type[SQLModel], id: int, email_norm: str) -> bool:
        stmt = select(model).where((model.id == id) | (model.email == email_norm))
        return self.session.exec(stmt).first() is not None

    def add(self, obj: SQLModel) -> SQLModel:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete_by_id(self, model: Type[SQLModel], obj_id: int) -> bool:
        db_obj = self.session.get(model, obj_id)
        if not db_obj:
            return False
        self.session.delete(db_obj)
        return True

    def get_all(self, model: Type[SQLModel]) -> List[SQLModel]:
        return list(self.session.exec(select(model)).all())

    def get_users_above_age(self, model: Type[SQLModel], age: int) -> List[SQLModel]:
        today = date.today()
        cutoff = today - relativedelta(years=age)
        stmt = select(model).where(model.date_of_birth <= cutoff)
        return list(self.session.exec(stmt).all())

    def get_users_between_age(
        self, model: Type[SQLModel], min_age: int, max_age: int
    ) -> List[SQLModel]:
        today = date.today()
        oldest_birth = today - relativedelta(years=max_age)

        youngest_birth = today - relativedelta(years=min_age)

        stmt = select(model).where(
            (model.date_of_birth >= oldest_birth) & (model.date_of_birth <= youngest_birth)
        )
        return list(self.session.exec(stmt).all())
