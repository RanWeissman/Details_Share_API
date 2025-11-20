from datetime import date

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from starlette.responses import Response

from src.core.api_globals import templates, security
from src.core.db_global import get_session
from src.database.contact_repository import ContactRepository
from src.models.contact import Contact
from src.models.account import Account

contacts_router = APIRouter(
    dependencies=[Depends(security.auth_required)],
)

@contacts_router.get("/pages/contacts/create", name="contacts_create_page")
def create_contact_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "contacts/add/contact_add.html",
    )

@contacts_router.post("/api/contacts/create", name="api_contacts_create")
def contacts_create(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        id_1: int = Form(...),
        date_of_birth: date = Form(...),
        session: Session = Depends(get_session),
        current_account: Account = Depends(security.get_current_contact)
) -> Response:
    error = "Contact with this ID or Email already exists!"
    status_code = status.HTTP_400_BAD_REQUEST
    contact_repo = ContactRepository(session)
    email_norm = email.strip().casefold()

    if not contact_repo.check_id_and_email(id_1, email):  # if not exists
        contact = Contact(
            id=id_1,
            name=name,
            email=email_norm,
            date_of_birth=date_of_birth,
            owner_id = current_account.id
        )

        contact_repo.add(contact)
        error = None
        status_code = status.HTTP_201_CREATED

    return templates.TemplateResponse(
        request,
        "contacts/add/contact_add_result.html",
        {
            "error": error,
            "name": name,
            "email": email_norm,
            "id": id_1,
            "date_of_birth": date_of_birth,
        },
        status_code=status_code,
    )

@contacts_router.get("/pages/contacts/delete", name="contacts_delete_page")
def delete_contact_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "contacts/delete/delete_contact.html",
        status_code=status.HTTP_200_OK,
    )

@contacts_router.post("/api/contacts/delete", name="api_contacts_delete")
def delete_contact(
    request: Request,
    id_1: int = Form(...),
    session: Session = Depends(get_session),
    current_account: Account = Depends(security.get_current_contact)

) -> Response:
    contact_repo = ContactRepository(session)

    success = contact_repo.delete_by_id_and_owner(
        contact_id=id_1,
        owner_id=current_account.id,
    )

    status_code = status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND

    return templates.TemplateResponse(
        request,
        "contacts/delete/delete_result.html",
        {"success": success, "id": id_1},
        status_code=status_code,
    )

@contacts_router.get("/pages/contacts/all", name="api_contacts_show_all")
def get_all_contacts(
        request: Request,
        session: Session = Depends(get_session)
) -> Response:
    contact_repo = ContactRepository(session)
    contacts = contact_repo.get_all()
    return templates.TemplateResponse(
        request,
        "contacts/show_contacts.html",
        {"contacts": contacts},
        status_code=status.HTTP_200_OK,
    )

@contacts_router.get("/api/contacts/all", name="json_contacts_show_all")
def get_contacts_json(
        session: Session = Depends(get_session)
) -> JSONResponse:
    contact_repo = ContactRepository(session)
    contacts = contact_repo.get_all()
    contacts_data = [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "date_of_birth": c.date_of_birth.isoformat(),
        }
        for c in contacts
            ]
    return JSONResponse(content=contacts_data)

####################################################################### Filtering Endpoints
@contacts_router.get("/pages/filters/menu", name="filters_menu_page")
def filter_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "contacts/filters/contacts_filter_page.html",
        status_code=status.HTTP_200_OK,
    )

@contacts_router.get("/pages/filters/age/above", name="filter_age_above_page")
def contacts_above_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "contacts/filters/filter_contacts_age_above.html",
        status_code=status.HTTP_200_OK,
    )

@contacts_router.get("/pages/filters/age/between", name="filter_age_between_page")
def contacts_between_page(request: Request) -> Response:
    return templates.TemplateResponse(
        request,
        "contacts/filters/filter_contacts_age_between.html",
        status_code=status.HTTP_200_OK,
    )

@contacts_router.post("/api/filters/age/above", name="api_age_above")
def contacts_above_show(
        request: Request,
        age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    contact_repo = ContactRepository(session)
    contacts = contact_repo.get_contacts_above_age(age)
    return templates.TemplateResponse(
        request,
        "contacts/filters/contacts_filter_result.html",
        {"age": age, "contacts": contacts},
        status_code=status.HTTP_200_OK,
    )

@contacts_router.post("/api/filters/age/between", name="api_age_between")
def contacts_between_show(
        request: Request,
        min_age: int = Form(...),
        max_age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    contact_repo = ContactRepository(session)
    contacts = contact_repo.get_contacts_between_age(min_age, max_age)
    return templates.TemplateResponse(
        request,
        "contacts/filters/contacts_filter_result.html",
        {"min_age": min_age, "max_age": max_age, "contacts": contacts},
        status_code=status.HTTP_200_OK,
    )


@contacts_router.get("/api/debug/contacts", name="debug_contacts_all")
def debug_contacts_all(
    session: Session = Depends(get_session),
) -> JSONResponse:
    contact_repo = ContactRepository(session)
    contacts = contact_repo.get_all()

    data = [
        {
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "date_of_birth": c.date_of_birth.isoformat(),
            "owner_id": c.owner_id,
        }
        for c in contacts
    ]
    return JSONResponse(content=data)
