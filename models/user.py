from sqlmodel import SQLModel, Field
from datetime import date


class User(SQLModel, table=True):
    id: int or None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    date_of_birth: date
    is_active: bool = Field(default=True)
    created_at: date = Field(default_factory=date.today)
