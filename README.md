# USERS_API — FastAPI User Development - Local Web

---

## Project Structure
Matches your current layout:

```
Web_Project_db/
├─ database/
│  ├─ databselayer.py
│  └─ user_db.py
├─ models/
│  └─ user.py
├─ templates/
│  ├─ filters/
│  │  ├─ filter_users_age_above.html
│  │  ├─ filter_users_age_between.html
│  │  ├─ users_filter_page.html
│  │  └─ users_filter_result.html
│  ├─ users/
│  │  ├─ add/
│  │  │  ├─ user_add.html
│  │  │  └─ user_add_result.html
│  │  ├─ delete/
│  │  │  ├─ delete_result.html
│  │  │  └─ delete_user.html
│  │  └─ show_users.html
│  └─ homepage.html
├─ .gitignore
├─ app_logging.py
├─ main.py
├─ README.md
└─ requirements.txt
```

---
## Install dependencies**
```bash
pip pip install -r requirements.txt

```

## Run the app 
```bash
uvicorn main:app --reload
```
The server will start on: <http://127.0.0.1:8000>

---

## Routes (Endpoints)


Pages (HTML views)
```bash
GET / – Homepage

GET /pages/users/create – Create user form

GET /pages/users/delete – Delete user form

GET /pages/users/all – All users (HTML)

GET /pages/filters/menu – Filters menu

GET /pages/filters/age/above – Form: users above age

GET /pages/filters/age/between – Form: users between ages
```
API (actions / JSON)
```bash
POST /api/users/create – Create user

POST /api/users/delete – Delete user

GET /api/users/all – All users (JSON)

POST /api/filters/age/above – Results: above age

POST /api/filters/age/between – Results: between ages

GET /api/debug/routes – List loaded routes

POST /request/name – Debug endpoint
```

