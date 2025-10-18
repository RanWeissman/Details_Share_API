from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:///ourDB.db"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False}, echo=False)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
