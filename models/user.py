from sqlmodel import SQLModel, Field
from datetime import date


class User(SQLModel, table=True):
    id: int or None = Field(default=None, primary_key=True)
    name: str
    email: str
    date_of_birth: date
