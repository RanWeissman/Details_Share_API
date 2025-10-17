from database.databselayer import DatabaseLayer
from userrepository import UserRepository
from models.user import User

_db: DatabaseLayer[User] = DatabaseLayer[User]()

def get_user_repo() -> UserRepository:
    return UserRepository(_db)
