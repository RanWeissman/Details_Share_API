from datetime import datetime, timedelta, timezone
import os

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from src.core.deps import get_session
from src.database.account_repository import AccountsRepository
from src.models.account import Account

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




def get_current_contact(
    request: Request,
    session: Session = Depends(get_session),
) -> Account:

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

    # נשלף ה-id ששמת ב-extra בזמן היצירה של הטוקן
    contact_id = payload.get("id")
    if contact_id is None:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Invalid token payload",
            headers={"Location": "/pages/account/login"},
        )

    # מביאים את המשתמש מה-DB
    repo = AccountsRepository(session)
    contact = repo.get_by_id(contact_id)

    if not contact or not contact.is_active:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="contact inactive or not found",
            headers={"Location": "/pages/account/login"},
        )

    # כאן contact הוא אובייקט Account אמיתי
    return contact


def auth_required(current_contact: Account = Depends(get_current_contact)) -> None:
    return None
