# app/repositories/user_repository.py
from __future__ import annotations
from typing import List
from datetime import date
from sqlmodel import select, or_
from database.databselayer import DatabaseLayer
from models.user import User

class UserRepository:
    def __init__(self, db: DatabaseLayer[User]):
        self.db = db

    def add(self, user: User) -> User:
        return self.db.add(user)

    def delete_by_id(self, user_id: int) -> bool:
        return self.db.delete(User, user_id)

    def list_all(self) -> List[User]:
        return self.db.get_all(User)

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get_by_id(User, user_id)

    def exists_by_id(self, user_id: int) -> bool:
        with self.db.get_session() as s:
            return s.get(User, user_id) is not None

    def exists_by_email(self, email: str) -> bool:
        with self.db.get_session() as s:
            return s.exec(select(User).where(User.email == email)).first() is not None

    def exists_email(self, email: str) -> bool:
        with self.db.get_session() as s:
            stmt = select(User).where((User.email == email))
            return s.exec(stmt).first() is not None

    def get_users_above_age(self, age: int) -> List[User]:
        with self.db.get_session() as s:
            today = date.today()
            cutoff = date(today.year - age, today.month, today.day)
            stmt = select(User).where(User.date_of_birth <= cutoff)
            return list(s.exec(stmt).all())

    def get_users_between_age(self, min_age: int, max_age: int) -> List[User]:
        with self.db.get_session() as s:
            today = date.today()
            max_birth = date(today.year - min_age, today.month, today.day)
            min_birth = date(today.year - max_age, today.month, today.day)
            stmt = select(User).where(
                (User.date_of_birth >= min_birth) &
                (User.date_of_birth <= max_birth)
            )
            return list(s.exec(stmt).all())
