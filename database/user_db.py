
# repositories/user_repository.py
from typing import Type, List
from datetime import date
from sqlmodel import Session, select, SQLModel

def check_id_and_email(
        session: Session,
        model: Type[SQLModel],
        id: int,
        email: str
) -> bool:
    statement = select(model).where((model.id == id) | (model.email == email))
    result = session.exec(statement).first()
    return result is not None

def add(
        session: Session,
        obj: SQLModel
) -> SQLModel:
    session.add(obj)
    session.flush()
    session.refresh(obj)
    return obj

def delete(
        session: Session,
        model: Type[SQLModel],
        obj_id: int
) -> bool:
    db_obj = session.get(model, obj_id)
    if not db_obj:
        return False
    session.delete(db_obj)
    return True

def get_all(
        session: Session,
        model: Type[SQLModel]
) -> List[SQLModel]:
    return list(session.exec(select(model)).all())

def get_users_above_age(
        session: Session,
        model: Type[SQLModel],
        age: int
) -> List[SQLModel]:
    today = date.today()
    cutoff_date = date(today.year - age, today.month, today.day)
    statement = select(model).where(model.date_of_birth <= cutoff_date)
    return list(session.exec(statement).all())

def get_users_between_age(
        session: Session,
        model: Type[SQLModel],
        min_age: int,
        max_age: int
) -> List[SQLModel]:
    today = date.today()
    max_birth_date = date(today.year - min_age, today.month, today.day)
    min_birth_date = date(today.year - max_age, today.month, today.day)
    statement = select(model).where(
        (model.date_of_birth >= min_birth_date) &
        (model.date_of_birth <= max_birth_date)
    )
    return list(session.exec(statement).all())
