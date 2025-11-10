from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
import os

# החלף את ה־CryptContext:
_pwd = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return _pwd.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd.verify(plain_password, hashed_password)

SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

def create_access_token(sub: str, extra: dict = None, minutes: int = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
