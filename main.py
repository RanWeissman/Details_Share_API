from contextlib import asynccontextmanager
import time
from datetime import date
from typing import Generator

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app_logging import configure_logging, get_logger
from database.db_core import DBCore
from database.user_repository import UsersRepository
from models.user import User

####################################################################### Logging Configuration
configure_logging()
logger = get_logger("app.main logger: ")

####################################################################### Lifespan Event Handler
@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("DB initialize - This is how we do it !!")
    try:
        yield
    finally:
        logger.info("Shutdown complete")
####################################################################### Database Core Initialization
db = DBCore()

####################################################################### FastAPI App Initialization
app = FastAPI(lifespan=lifespan)

####################################################################### Jinja2 Templates Setup
templates = Jinja2Templates(directory="templates")

####################################################################### CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "https://myfrontend.com",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

####################################################################### Database Session Dependency
def get_session() -> Generator[Session, None, None]:
    s =  db.get_session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()

####################################################################### Middleware to Log Request Processing Time
@app.middleware("http")
async def log_request_time(
        request: Request,
        call_next: RequestResponseEndpoint
) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    formatted_time = f"{process_time:.4f} sec"
    logger.info("%s %s took %s", request.method, request.url.path, formatted_time)
    response.headers["X-Process-Time"] = formatted_time
    return response

####################################################################### Home Page Endpoint
@app.get("/")
def show_homepage(
        request: Request,
) -> Response:
    return templates.TemplateResponse(
        "homepage.html",
        {"request": request}
    )

####################################################################### CRUD Endpoints
@app.get("/pages/users/create", name="users_create_page")
def create_user_page(request: Request):
    return templates.TemplateResponse(
        "users/add/user_add.html",
        {"request": request}
    )

@app.post("/api/users/create", name="api_users_create")
def users_create(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        id: int = Form(...),
        date_of_birth: date = Form(...),
        session: Session = Depends(get_session)
) -> Response:
    error = f"User with this ID or Email already exists!"
    status_code = status.HTTP_400_BAD_REQUEST
    user_repo = UsersRepository(session)
    email_norm = email.strip().casefold()
    if not user_repo.check_id_and_email(User, id, email):  # if not exists
        user = User(id=id, name=name, email=email_norm, date_of_birth=date_of_birth)
        # add user to DB
        user_repo.add(user)
        #
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

@app.get("/pages/users/delete", name="users_delete_page")
def delete_user_page(
        request: Request
) -> Response:
    return templates.TemplateResponse(
        "users/delete/delete_user.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@app.post("/api/users/delete", name="api_users_delete")
def delete_user(
    request: Request,
    id: int = Form(...),
    session: Session = Depends(get_session),
) -> Response:
    user_repo = UsersRepository(session)
    # delete user from DB
    success = user_repo.delete_by_id(User, id)
    #
    status_code = status.HTTP_200_OK if success else status.HTTP_404_NOT_FOUND

    return templates.TemplateResponse(
        "users/delete/delete_result.html",
        {"request": request,"success": success, "id": id},
        status_code=status_code,
    )

####################################################################### Show All Users Endpoints
@app.get("/pages/users/all", name="api_users_show_all")
def get_all_users(
        request: Request,
        session: Session = Depends(get_session)
) -> Response:
    user_repo = UsersRepository(session)
    # get all users from DB
    users = user_repo.get_all(User)
    #
    return templates.TemplateResponse(
        "users/show_users.html",
        {"request": request, "users": users},
        status_code=status.HTTP_200_OK,

    )

@app.get("/api/users/all", name="json_users_show_all")
def get_users_json(
        session: Session = Depends(get_session)
) -> JSONResponse:
    user_repo = UsersRepository(session)
    # get all users from DB
    users = user_repo.get_all(User)
    #
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
@app.get("/pages/filters/menu", name="filters_menu_page")
def filter_page(
        request: Request,
) -> Response:
    return templates.TemplateResponse(
        "filters/users_filter_page.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@app.get("/pages/filters/age/above", name="filter_age_above_page")
def users_above_page(
        request: Request,
) -> Response:
    return templates.TemplateResponse(
        "filters/filter_users_age_above.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@app.get("/pages/filters/age/between", name="filter_age_between_page")
def users_between_page(
        request: Request,
) -> Response:
    return templates.TemplateResponse(
        "filters/filter_users_age_between.html",
        {"request": request},
        status_code=status.HTTP_200_OK,
    )

@app.post("/api/filters/age/above", name="api_age_above")
def users_above_show(
        request: Request,
        age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = UsersRepository(session)
    # get users above age from DB
    users = user_repo.get_users_above_age(User, age)
    #
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "age": age, "users": users},
        status_code=status.HTTP_200_OK,

    )

@app.post("/api/filters/age/between", name="api_age_between")
def users_between_show(
        request: Request,
        min_age: int = Form(...),
        max_age: int = Form(...),
        session: Session = Depends(get_session),
) -> Response:
    user_repo = UsersRepository(session)
    # get users between ages from DB
    users = user_repo.get_users_between_age(User, min_age, max_age)
    #
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "min_age": min_age, "max_age": max_age, "users": users},
        status_code=status.HTTP_200_OK,

    )

####################################################################### Debugging Endpoints
@app.get("/api/debug/routes")
def debug_routes() -> HTMLResponse:
    lines = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            lines.append(f"{sorted(r.methods)}  {r.path}  -> {r.endpoint.__name__}")
    html = "<br>".join(lines)
    return HTMLResponse(content=html)

