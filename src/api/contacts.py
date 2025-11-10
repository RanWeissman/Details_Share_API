from datetime import date

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from starlette.responses import Response

from src.core.deps import get_session, templates
from src.core.security import get_current_user
from src.database import contact_repository as ur
from src.models.contact import Contact
router = APIRouter(
    dependencies=[Depends(get_current_user)]
    )

@router.get("/pages/contacts/create", name="contacts_create_page")
def create_user_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "contacts/add/user_add.html",
        {"request": request}
    )

@router.post("/api/contacts/create", name="api_contacts_create")
def contacts_create(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        id_1: int = Form(...),
        date_of_birth: date = Form(...),
        session: Session = Depends(get_session)
) -> Response:
    error = "User with this ID or Email already exists!"
    status_code = status.HTTP_400_BAD_REQUEST
    user_repo = ur.ContactRepository(session)
    email_norm = email.strip().casefold()

    if not user_repo.check_id_and_email(Contact, id_1, email):  # if not exists
        user = Contact(id=id_1, name=name, email=email_norm, date_of_birth=date_of_birth)
        user_repo.add(user)
        error = None
        status_code = status.HTTP_201_CREATED

    return templates.TemplateResponse(
        "contacts/add/user_add_result.html",
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

@router.get("/pages/contacts/delete", name="contacts_delete_page")
def delete_user_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "contacts/delete/delete_user.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/contacts/delete", name="api_contacts_delete")
def delete_user(
    request: Request,
    id_1: int = Form(...),
    session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.ContactRepository(session)
    success = user_repo.delete_by_id(Contact, id_1)
    status_code = status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND

    return templates.TemplateResponse(
        "contacts/delete/delete_result.html",
        {"request": request, "success": success, "id": id_1},
        status_code=status_code,
    )

@router.get("/pages/contacts/all", name="api_contacts_show_all")
def get_all_contacts(
        request: Request,
        session: Session = Depends(get_session)
) -> Response:
    user_repo = ur.ContactRepository(session)
    contacts = user_repo.get_all(Contact)
    return templates.TemplateResponse(
        "contacts/show_contacts.html",
        {"request": request, "contacts": contacts},
        status_code=status.HTTP_200_OK,
    )

@router.get("/api/contacts/all", name="json_contacts_show_all")
def get_contacts_json(
        session: Session = Depends(get_session)
) -> JSONResponse:
    user_repo = ur.ContactRepository(session)
    contacts = user_repo.get_all(Contact)
    contacts_data = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "date_of_birth": u.date_of_birth.isoformat(),
        }
        for u in contacts
    ]
    return JSONResponse(content=contacts_data)

####################################################################### Filtering Endpoints
@router.get("/pages/filters/menu", name="filters_menu_page")
def filter_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "filters/contacts_filter_page.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.get("/pages/filters/age/above", name="filter_age_above_page")
def contacts_above_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "contacts/filters/filter_contacts_age_above.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.get("/pages/filters/age/between", name="filter_age_between_page")
def contacts_between_page(request: Request) -> Response:
    return templates.TemplateResponse(
        "contacts/filters/filter_contacts_age_between.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/filters/age/above", name="api_age_above")
def contacts_above_show(
        request: Request,
        age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.ContactRepository(session)
    contacts = user_repo.get_contacts_above_age(Contact, age)
    return templates.TemplateResponse(
        "contacts/filters/contacts_filter_result.html",
        {"request": request, "age": age, "contacts": contacts},
        status_code=status.HTTP_200_OK,
    )

@router.post("/api/filters/age/between", name="api_age_between")
def contacts_between_show(
        request: Request,
        min_age: int = Form(...),
        max_age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = ur.ContactRepository(session)
    contacts = user_repo.get_contacts_between_age(Contact, min_age, max_age)
    return templates.TemplateResponse(
        "contacts/filters/contacts_filter_result.html",
        {"request": request, "min_age": min_age, "max_age": max_age, "contacts": contacts},
        status_code=status.HTTP_200_OK,
    )
