from src.models.role import Role
from sqlmodel import SQLModel, Field
from datetime import date

class Account(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: Role = Field(default=Role.user)
    created_at: date = Field(default_factory=date.today)
    is_active: bool = Field(default=True)
