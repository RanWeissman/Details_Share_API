from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

from datetime import date

from models.user import User
from databselayer import DatabaseLayer

app = FastAPI()

templates = Jinja2Templates(directory="templates")
db = DatabaseLayer("sqlite:///ourDB.db")


@app.get("/", response_class=FileResponse)
def show_homepage():
    return FileResponse("templates/homepage.html")


@app.get("/create_user_page", response_class=FileResponse)
def create_user_page():
    return FileResponse("templates/add/user_add.html")


@app.post("/create_user")
def create_user(request: Request, name: str = Form(...), email: str = Form(...), date_of_birth: date = Form(...)):
    user = User(name=name, email=email, date_of_birth=date_of_birth)
    user = db.add(user)

    return templates.TemplateResponse(
        "user_add_result.html",
        {
            "request": request,
            "name": user.name,
            "email": user.email,
            "id": user.id,
            "date_of_birth": user.date_of_birth,

        }
    )


@app.get("/delete_user_page", response_class=FileResponse)
def delete_user_page():
    return FileResponse("templates/delete/delete_user.html")


# @app.post("/delete_user", response_class=HTMLResponse)
# async def delete_user(request: Request):
#     raw = await request.body()
#     print("RAW BODY:", raw)
#     print("HEADERS:", request.headers)
#     return HTMLResponse("debug")


@app.post("/delete_user", response_class=HTMLResponse)
def delete_user(request: Request, id: int = Form(...)):
    success = db.delete(User, id)

    if not success:
        return templates.TemplateResponse(
            "delete_result.html",
            {"request": request, "success": False, "id": id},
        )

    return templates.TemplateResponse(
        "delete_result.html",
        {"request": request, "success": True, "id": id},
    )


@app.get("/get_all_users", response_class=HTMLResponse)
def get_all_users(request: Request):
    users = db.get_all(User)
    return templates.TemplateResponse(
        "show_users.html", {"request": request, "users": users}
    )


@app.get("/api/users")
def get_users_json():
    users = db.get_all(User)
    users_data = [{"id": u.id, "name": u.name, "email": u.email,
                   "date_of_birth": u.date_of_birth.isoformat()} for u in users]
    return JSONResponse(content=users_data)


@app.get("/filter_page", response_class=FileResponse)
def filter_page():
    return FileResponse("templates/filters/users_filter_page.html")


@app.get("/users_above_page", response_class=FileResponse)
def delete_user_page():
    return FileResponse("templates/filters/filter_users_age_above.html")


@app.post("/users_above_show", response_class=HTMLResponse)
def users_above_show(request: Request, age: int = Form(...)):
    users = db.get_users_above_age(User, age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "age": age, "users": users},
    )


@app.get("/users_between_page", response_class=FileResponse)
def users_between_page():
    return FileResponse("filters/filter_users_age_between.html")


@app.post("/users_between_show", response_class=HTMLResponse)
def users_between_show(request: Request, min_age: int = Form(...), max_age: int = Form(...)):
    users = db.get_users_between_age(User, min_age, max_age)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "min_age": min_age, "max_age": max_age, "users": users},
    )


@app.post("/all_Users_by_age_page", response_class=HTMLResponse)
def all_Users_by_age_page(request: Request):
    users = db.get_users_by_age(User)
    return templates.TemplateResponse(
        "filters/users_filter_result.html",
        {"request": request, "users": users},
    )


