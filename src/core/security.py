from datetime import datetime, timedelta, timezone
import os

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from src.core.db_global import get_session
from src.database.account_repository import AccountsRepository
from src.models.account import Account


class Security:
    """Security helper class: hashing + JWT management + FastAPI dependencies.

    Note: We don't instantiate it here to avoid import-time cycles. A single
    `security` instance will be created in `src.core.deps` and module-level
    wrapper functions below will delegate to it at call time.
    """

    def __init__(self) -> None:
        self._pwd = CryptContext(schemes=["argon2"], deprecated="auto")
        self._secret_key = os.getenv("SECRET_KEY", "my_secret_key")
        self._algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self._access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )

    def get_password_hash(self, password: str) -> str:
        return self._pwd.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._pwd.verify(plain_password, hashed_password)

    def create_access_token(self, sub: str, extra: dict = None, minutes: int = None) -> str:
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=minutes or self._access_token_expire_minutes)
        payload = {"sub": str(sub), "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
        if extra:
            payload.update(extra)
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def get_current_contact(self, request: Request, session: Session = Depends(get_session)) -> Account:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="Not authenticated",
                headers={"Location": "/pages/account/login"},
            )

        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="Invalid or expired token",
                headers={"Location": "/pages/account/login"},
            )

        contact_id = payload.get("id") or payload.get("sub")
        if contact_id is None:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="Invalid token payload",
                headers={"Location": "/pages/account/login"},
            )

        try:
            cid = int(contact_id)
        except Exception:
            cid = contact_id

        repo = AccountsRepository(session)
        contact = repo.get_by_id(cid)

        if not contact or not getattr(contact, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                detail="contact inactive or not found",
                headers={"Location": "/pages/account/login"},
            )

        return contact

    def auth_required(self, current_contact: Account = Depends(get_session)) -> None:
        pass
