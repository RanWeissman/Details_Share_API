from src.models.role_enum import RoleEnum
from sqlmodel import SQLModel, Field
from datetime import date

class Account(SQLModel, table=True):
    __tablename__ = "account"
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: RoleEnum = Field(default=RoleEnum.user)
    created_at: date = Field(default_factory=date.today)
    is_active: bool = Field(default=True)
