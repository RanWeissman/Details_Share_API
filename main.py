import time
from datetime import date

from fastapi import FastAPI, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from models.user import User
from database.databselayer import DatabaseLayer

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

def get_db():
    db_main = DatabaseLayer()
    try:
        yield db_main
    finally:
        pass


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    formatted_time = f"{process_time:.4f} sec"
    print(f"⏱//////////////////////////////// {request.method} {request.url.path} took {formatted_time}")
    response.headers["X-Process-Time"] = formatted_time
    return response


@app.get("/", response_class=FileResponse)
def show_homepage():
    return FileResponse("templates/homepage.html")


####################################################################### CRUD Endpoints

@app.get("/pages/users/create", response_class=FileResponse)
def create_user_page():
    return FileResponse("templates/users/add/user_add.html")


@app.post("/api/users/create", response_class=HTMLResponse)
def users_create(request: Request, name: str = Form(...), email: str = Form(...), id: int = Form(...),
                 date_of_birth: date = Form(...), db: DatabaseLayer = Depends(get_db)):
    existing_user = db.check_id_and_email(User, id, email)
    if not existing_user:
        user = User(id=id, name=name, email=email, date_of_birth=date_of_birth)
        db.add(user)
        return templates.TemplateResponse(
            "users/add/user_add_result.html",
            {
                "request": request,
                "name": user.name,
                "email": user.email,
                "id": user.id,
                "date_of_birth": user.date_of_birth,

            }
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
            status_code=400
        )


@app.get("/pages/users/delete", response_class=FileResponse)
def delete_user_page():
    return FileResponse("templates/users/delete/delete_user.html")


@app.post("/api/users/delete", response_class=HTMLResponse)
def delete_user(request: Request, id: int = Form(...), db: DatabaseLayer = Depends(get_db)):
    success = db.delete(User, id)

    if not success:
        return templates.TemplateResponse(
            "users/delete/delete_result.html",
            {"request": request, "success": False, "id": id},
        )

    return templates.TemplateResponse(
        "users/delete/delete_result.html",
        {"request": request, "success": True, "id": id},
    )


####################################################################### All Users Endpoints

@app.get("/pages/users/all", response_class=HTMLResponse)
def get_all_users(request: Request, db: DatabaseLayer = Depends(get_db)):
    users = db.get_all(User)
    return templates.TemplateResponse(
        "users/show_users.html", {"request": request, "users": users}
    )


@app.get("/api/users/all")
def get_users_json(db: DatabaseLayer = Depends(get_db)):
    users = db.get_all(User)
    users_data = [{"id": u.id, "name": u.name, "email": u.email,
                   "date_of_birth": u.date_of_birth.isoformat()} for u in users]
    return JSONResponse(content=users_data)


####################################################################### Filtering Endpoints


@app.get("/pages/filters/menu", response_class=FileResponse)
def filter_page():
    return FileResponse("templates/filters/users_filter_page.html")


@app.get("/pages/filters/age/above", response_class=FileResponse)
def users_above_page():
    return FileResponse("templates/filters/filter_users_age_above.html")


@app.post("/api/filters/age/above", response_class=HTMLResponse)
def users_above_show(request: Request, age: int = Form(...), db: DatabaseLayer = Depends(get_db)):
    users = db.get_users_above_age(User, age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "age": age, "users": users},
    )


@app.get("/pages/filters/age/between", response_class=FileResponse)
def users_between_page():
    return FileResponse("templates/filters/filter_users_age_between.html")


@app.post("/api/filters/age/between", response_class=HTMLResponse)
def users_between_show(request: Request, min_age: int = Form(...), max_age: int = Form(...),
                       db: DatabaseLayer = Depends(get_db)):
    users = db.get_users_between_age(User, min_age, max_age)
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
