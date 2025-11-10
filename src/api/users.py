from datetime import date

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from starlette.responses import Response

from src.core.deps import get_session, templates
from src.core.security import get_current_user
from src.database import user_repository as ur
from src.models.user import User
router = APIRouter(
    dependencies=[Depends(get_current_user)]
    )

@router.get("/pages/users/create", name="users_create_page")
def create_user_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "users/add/user_add.html",
        {"request": request}
    )

@router.post("/api/users/create", name="api_users_create")
def users_create(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        id: int = Form(...),
        date_of_birth: date = Form(...),
        session: Session = Depends(get_session)
) -> Response:
    error = "User with this ID or Email already exists!"
    status_code = status.HTTP_400_BAD_REQUEST
    user_repo = ur.UsersRepository(session)
    email_norm = email.strip().casefold()

    if not user_repo.check_id_and_email(User, id, email):  # if not exists
        user = User(id=id, name=name, email=email_norm, date_of_birth=date_of_birth)
        user_repo.add(user)
        error = None
        status_code = status.HTTP_201_CREATED

    return templates.TemplateResponse(
        "users/add/user_add_result.html",
        {
            "request": request,
            "error": error,
            "name": name,
            "email": email,
            "id": id,
            "date_of_birth": date_of_birth,
        },
        status_code=status_code,
    )

@router.get("/pages/users/delete", name="users_delete_page")
def delete_user_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "users/delete/delete_user.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/users/delete", name="api_users_delete")
def delete_user(
    request: Request,
    id: int = Form(...),
    session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.UsersRepository(session)
    success = user_repo.delete_by_id(User, id)
    status_code = status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND

    return templates.TemplateResponse(
        "users/delete/delete_result.html",
        {"request": request, "success": success, "id": id},
        status_code=status_code,
    )

@router.get("/pages/users/all", name="api_users_show_all")
def get_all_users(
        request: Request,
        session: Session = Depends(get_session)
) -> Response:
    user_repo = ur.UsersRepository(session)
    users = user_repo.get_all(User)
    return templates.TemplateResponse(
        "users/show_users.html",
        {"request": request, "users": users},
        status_code=status.HTTP_200_OK,
    )

@router.get("/api/users/all", name="json_users_show_all")
def get_users_json(
        session: Session = Depends(get_session)
) -> JSONResponse:
    user_repo = ur.UsersRepository(session)
    users = user_repo.get_all(User)
    users_data = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "date_of_birth": u.date_of_birth.isoformat(),
        }
        for u in users
    ]
    return JSONResponse(content=users_data)

####################################################################### Filtering Endpoints
@router.get("/pages/filters/menu", name="filters_menu_page")
def filter_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "filters/users_filter_page.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.get("/pages/filters/age/above", name="filter_age_above_page")
def users_above_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "filters/filter_users_age_above.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.get("/pages/filters/age/between", name="filter_age_between_page")
def users_between_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "filters/filter_users_age_between.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/filters/age/above", name="api_age_above")
def users_above_show(
        request: Request,
        age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.UsersRepository(session)
    users = user_repo.get_users_above_age(User, age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "age": age, "users": users},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/filters/age/between", name="api_age_between")
def users_between_show(
        request: Request,
        min_age: int = Form(...),
        max_age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.UsersRepository(session)
    users = user_repo.get_users_between_age(User, min_age, max_age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "min_age": min_age, "max_age": max_age, "users": users},
        status_code=status.HTTP_200_OK,
    )
