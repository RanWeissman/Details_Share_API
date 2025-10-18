from typing import Type, List
from datetime import date
from sqlmodel import Session, SQLModel, select

class UsersRepository:
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
        cutoff = _years_ago(date.today(), age)
        stmt = select(model).where(model.date_of_birth <= cutoff)
        return list(self.session.exec(stmt).all())

    def get_users_between_age(
        self, model: Type[SQLModel], min_age: int, max_age: int
    ) -> List[SQLModel]:
        today = date.today()
        max_birth = _years_ago(date.today(), min_age)

        min_birth = _years_ago(date.today(), max_age)

        stmt = select(model).where(
            (model.date_of_birth >= min_birth) & (model.date_of_birth <= max_birth)
        )
        return list(self.session.exec(stmt).all())

## private static function - handles february 29 case
def _years_ago(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year - years)
    except ValueError:
        return d.replace(month=2, day=28, year=d.year - years)

