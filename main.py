import time
from datetime import date
from typing import Generator

from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from models.user import User
from database.databselayer import DatabaseLayer
import database.user_db as user_db

app = FastAPI()

templates = Jinja2Templates(directory="templates")

origins = [
    "http://localhost:3000",
    "https://myfrontend.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_session() -> Generator[Session, None, None]:
    session = DatabaseLayer().get_session()
    try:
        yield session
    finally:
        session.close()


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    formatted_time = f"{process_time:.4f} sec"
    print(f"//////////////////////////////// {request.method} {request.url.path} took {formatted_time}")
    response.headers["X-Process-Time"] = formatted_time
    return response

####################################################################### Home Page Endpoint

@app.get("/", response_class=FileResponse)
def show_homepage():
    return FileResponse("templates/homepage.html")


####################################################################### CRUD Endpoints

@app.get("/pages/users/create", response_class=FileResponse)
def create_user_page():
    return FileResponse("templates/users/add/user_add.html")


@app.post("/api/users/create", response_class=HTMLResponse)
def users_create(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        id: int = Form(...),
        date_of_birth: date = Form(...),
        session: Session = Depends(get_session)
):

    if not user_db.check_id_and_email(session,User, id, email): # if not exists
        user = User(id=id, name=name, email=email, date_of_birth=date_of_birth)
        try:
            user_db.add(session, user)
            session.commit()
            session.refresh(user)
        except Exception:
            session.rollback()
            raise

        return templates.TemplateResponse(
            "users/add/user_add_result.html",
            {
                "request": request,
                "name": user.name,
                "email": user.email,
                "id": user.id,
                "date_of_birth": user.date_of_birth,
            },
            status_code=status.HTTP_201_CREATED,
        )
    else:
        return templates.TemplateResponse(
            "users/add/user_add_result.html",
            {
                "request": request,
                "error": f"User with this ID or Email already exists!",
                "name": name,
                "email": email,
                "id": id,
                "date_of_birth": date_of_birth,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@app.get("/pages/users/delete", response_class=FileResponse)
def delete_user_page():
    return FileResponse("templates/users/delete/delete_user.html")


@app.post("/api/users/delete", response_class=HTMLResponse)
def delete_user(
        request: Request,
        id: int = Form(...),
        session: Session = Depends(get_session),
):
    try:
        ok = user_db.delete(session, User, id)
        if not ok:
            return templates.TemplateResponse(
                "users/delete/delete_result.html",
                {"request": request, "success": False, "id": id},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        session.commit()
    except Exception:
        session.rollback()
        raise

    return templates.TemplateResponse(
        "users/delete/delete_result.html",
        {"request": request, "success": True, "id": id},
        status_code=status.HTTP_200_OK,
    )

####################################################################### Show All Users Endpoints


@app.get("/pages/users/all", response_class=HTMLResponse)
def get_all_users(
        request: Request,
        session:
        Session = Depends(get_session)):
    users = user_db.get_all(session, User)
    return templates.TemplateResponse(
        "users/show_users.html", {"request": request, "users": users}
    )


@app.get("/api/users/all")
def get_users_json(session: Session = Depends(get_session)):
    users = user_db.get_all(session, User)
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


@app.get("/pages/filters/menu", response_class=FileResponse)
def filter_page():
    return FileResponse("templates/filters/users_filter_page.html")


@app.get("/pages/filters/age/above", response_class=FileResponse)
def users_above_page():
    return FileResponse("templates/filters/filter_users_age_above.html")


@app.get("/pages/filters/age/between", response_class=FileResponse)
def users_between_page():
    return FileResponse("templates/filters/filter_users_age_between.html")


@app.post("/api/filters/age/above", response_class=HTMLResponse)
def users_above_show(
    request: Request,
    age: int = Form(...),
    session: Session = Depends(get_session),
):
    users = user_db.get_users_above_age(session, User, age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "age": age, "users": users},
    )


@app.post("/api/filters/age/between", response_class=HTMLResponse)
def users_between_show(
    request: Request,
    min_age: int = Form(...),
    max_age: int = Form(...),
    session: Session = Depends(get_session),
):
    users = user_db.get_users_between_age(session, User, min_age, max_age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "min_age": min_age, "max_age": max_age, "users": users},
    )


####################################################################### Debugging Endpoints

@app.get("/api/debug/routes", response_class=HTMLResponse)
def debug_routes():
    lines = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            lines.append(f"{sorted(r.methods)}  {r.path}  -> {r.endpoint.__name__}")
    return "<br>".join(lines)


@app.post("/request/name", response_class=HTMLResponse)
async def debug_function(request: Request):
    raw = await request.body()
    print("RAW BODY:", raw)
    print("HEADERS:", request.headers)
    return HTMLResponse("debug")
