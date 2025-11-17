from typing import List
from datetime import date

from dateutil.relativedelta import relativedelta
from sqlmodel import Session,  select

from src.models.contact import Contact


class ContactRepository:
    def __init__(self, session: Session):
        self.session = session
        self.model = Contact

    def check_id_and_email(self, id_1: int, email_norm: str) -> bool:
        stmt = select(self.model).where((self.model.id == id_1) | (self.model.email == email_norm))
        return self.session.exec(stmt).first() is not None

    def add(self, obj: Contact) -> Contact:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> None:
        return self.session.get(self.model, obj_id)

    def delete_by_id_and_owner(self, contact_id: int, owner_id: int) -> bool:
        obj = self.session.get(self.model, contact_id)
        if not obj:
            return False

        if obj.owner_id != owner_id:
            return False

        self.session.delete(obj)
        self.session.commit()
        return True

    def delete_by_id(self, obj_id: int) -> bool:
        db_obj = self.session.get(self.model, obj_id)
        if not db_obj:
            return False
        self.session.delete(db_obj)
        return True

    def get_all(self) -> List[Contact]:
        return list(self.session.exec(select(self.model)).all())

    def get_contacts_above_age(self, age: int) -> List[Contact]:
        today = date.today()
        cutoff = today - relativedelta(years=age)
        stmt = select(self.model).where(self.model.date_of_birth <= cutoff)
        return list(self.session.exec(stmt).all())

    def get_contacts_between_age(
        self, min_age: int, max_age: int
    ) -> List[Contact]:
        today = date.today()
        oldest_birth = today - relativedelta(years=max_age)

        youngest_birth = today - relativedelta(years=min_age)

        stmt = select(self.model).where(
            (self.model.date_of_birth >= oldest_birth) & (self.model.date_of_birth <= youngest_birth)
        )
        return list(self.session.exec(stmt).all())
