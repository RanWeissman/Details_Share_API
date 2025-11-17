from typing import List, Optional
from sqlmodel import Session, select
from src.models.account import Account

class AccountsRepository:
    def __init__(self, session: Session):
        self.session = session
        self.model = Account

    def check_mail_and_username(self, email_norm: str, username: str) -> bool:
        stmt = select(self.model).where((self.model.email == email_norm) | (self.model.username == username))
        return self.session.exec(stmt).first() is not None

    def add(self, account: Account) -> Account:
        self.session.add(account)
        self.session.flush()
        self.session.refresh(account)
        return account

    def create_account(self, username: str, email: str, hashed_password: str) -> Account:
        acc = Account(username=username, email=email, hashed_password=hashed_password)
        return self.add(acc)

    def delete_by_id(self, obj_id: int) -> bool:
        acc = self.session.get(Account, obj_id)
        if not acc:
            return False
        self.session.delete(acc)
        return True

    def delete_by_username(self, username: str) -> bool:
        acc = self.get_by_username(username)
        if not acc:
            return False
        self.session.delete(acc)
        return True

    def get_all(self) -> List[Account]:
        return list(self.session.exec(select(Account)).all())


    def get_by_id(self, obj_id: int) -> Optional[Account]:
        return self.session.get(Account, obj_id)

    def get_by_username(self, username: str) -> Optional[Account]:
        return self.session.exec(
            select(Account).where(Account.username == username)
        ).first()

    def get_by_email(self, email: str) -> Optional[Account]:
        return self.session.exec(
            select(Account).where(Account.email == email)
        ).first()

    def exists_username_or_email(self, username: str, email: str) -> bool:
        """
        בודק אם קיים חשבון עם אותו username או email.
        """
        stmt = select(Account).where(
            (Account.username == username) | (Account.email == email)
        )
        return self.session.exec(stmt).first() is not None
