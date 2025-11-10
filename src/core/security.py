from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
import os

from fastapi import Request, HTTPException, status

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


def get_current_user(request: Request) -> dict:
    """
    Dependency: מאמת JWT שמגיע מה-cookie בשם 'access_token'.
    אם אין / לא תקין / פג תוקף -> redirect לדף login.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/pages/account/login"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Invalid or expired token",
            headers={"Location": "/pages/account/login"},
        )

    return payload