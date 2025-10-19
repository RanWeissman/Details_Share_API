# FastAPI User Development - Local Web

---
```bash
This FastAPI project manages users, serving HTML pages with Jinja2.
Implements basic CRUD operations, and providing user filtering option.
```
---
## Install dependencies**
```bash
pip install -r requirements.txt

```
---
## Run the app 
```bash
uvicorn main:app --reload
```
The server will start on: <http://127.0.0.1:8000>

---
`%%{init: {
  "theme": "base",
  "flowchart": { "nodeSpacing": 70, "rankSpacing": 110, "padding": 12 }
}}%%
flowchart LR
  subgraph DAL["Data Layer"]
    direction TB
    RDB[("Database")]
    CONN["Session / Engine<br/>(Transactions)"]
    SM["ORM / SQLModel<br/>(Models, Queries)"]
  end

  subgraph APP["Application (Backend)"]
    direction TB
    FP["FastAPI<br/>(ASGI, Routers, Middleware)"]
    PY["Python Logic<br/>(Services / Utilities)"]
    J2["Jinja2 Templates<br/>(SSR HTML)"]
  end

  subgraph CLIENT["Presentation (Client)"]
    BR(["Browser<br/>(HTML/CSS/JS)"])
  end

  BR -->|HTTP| FP
  FP --> PY
  FP --> J2
  PY --> SM
  SM --> CONN
  CONN --> RDB
  RDB --> CONN
  FP -->|JSON| BR
  J2 -->|HTML| BR
