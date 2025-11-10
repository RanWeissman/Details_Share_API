import os

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session
from starlette.responses import Response

from src.core.deps import get_session, templates
from src.database.account_repository import AccountsRepository
from src.models.account import Account
from src.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()


####################################################################### Home / Menu

@router.get("/")
def show_homepage(request: Request) -> Response:
    return templates.TemplateResponse(
        "auth/homepage.html",
        {"request": request}
    )


@router.get("/menu", name="menu_after_login")
def menu_after_login(request: Request) -> Response:
    return templates.TemplateResponse(
        "menu.html",
        {"request": request}
    )


####################################################################### Signup Endpoints

@router.get("/pages/account/signup", name="account_create_page")
def account_create_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "auth/signup/signup.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )


@router.post("/api/account/signup", name="api_signup_create")
def signup_account_results(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
) -> Response:
    error = "User with this ID or Email already exists!"
    status_code = status.HTTP_400_BAD_REQUEST

    account_repo = AccountsRepository(session)
    email_norm = email.strip().casefold()
    user_norm = username.strip().casefold()
    hashed = get_password_hash(password)

    if not account_repo.check_mail_and_username(Account, email_norm, user_norm):  # if not exists
        account_repo.create_account(username=user_norm, email=email_norm, hashed_password=hashed)
        error = None
        status_code = status.HTTP_201_CREATED

    return templates.TemplateResponse(
        "auth/signup/signup_result.html",
        {
            "request": request,
            "error": error,
            "username": user_norm,
            "email": email_norm,
        },
        status_code=status_code,
    )


####################################################################### Login / Logout Endpoints

@router.get("/pages/account/login", name="account_login_page")
def account_login_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "auth/login/login.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )


@router.post("/api/account/login", name="api_account_login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user_norm = username.strip().casefold()
    repo = AccountsRepository(session)
    acc = repo.get_by_username(user_norm)

    if not acc or not verify_password(password, acc.hashed_password) or not acc.is_active:
        return templates.TemplateResponse(
            "auth/login/login_fail.html",
            {"request": request, "username": user_norm}
        )

    token = create_access_token(sub=acc.email, extra={"id": acc.id, "role": str(acc.role)})
    success_target = request.url_for("menu_after_login")
    resp = RedirectResponse(url=str(success_target), status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=bool(int(os.getenv("COOKIE_SECURE", "0"))),
        samesite="lax",
        max_age=60 * 60,
        path="/",
    )
    return resp


@router.post("/api/account/logout", name="api_account_logout")
def logout():
    resp = HTMLResponse("Logged out")
    resp.delete_cookie("access_token", path="/")
    return resp
