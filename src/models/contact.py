from sqlmodel import SQLModel, Field
from datetime import date

class Contact(SQLModel, table=True):
    id: int = Field( primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    date_of_birth: date
    is_active: bool = Field(default=True)
    created_at: date = Field(default_factory=date.today)
