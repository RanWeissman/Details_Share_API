# FastAPI User Development - Local Web

---
```bash
This FastAPI project manages users, serving HTML pages with Jinja2.
Implements basic CRUD operations, and providing user filtering option.
```
---
## Install dependencies
```bash
- Python ≥ 3.9
```
```bash
pip install -r requirements.txt
```
---
## Run the server
### Option A — Without downloading (build directly from GitHub)
```bash
docker build -t details-share-api:latest https://github.com/RanWeissman/Details_Share_API.git#main
```
```bash
docker run --rm -p 8000:8000 details-share-api:latest
```

### Option B — With clone the project: 
```bash
git clone https://github.com/RanWeissman/Details_Share_API.git
```
```bash
cd Details_Share_API
```
```bash
docker compose up --build
```
### Option C — Without Docker, run locally: 
```bash
git clone https://github.com/RanWeissman/Details_Share_API.git
```
```bash
cd Details_Share_API
```
```bash
py -m pip install -r requirements.txt
```
```bash
py -m src.run_server
```
The server will start on: <http://127.0.0.1:8000>

```mermaid
---
config:
  theme: base
  flowchart:
    defaultRenderer: elk
    nodeSpacing: 70
    rankSpacing: 110
    padding: 12
  layout: dagre
---
flowchart LR
 subgraph DAL["Data Layer"]
    direction TB
        RDB[("Database")]
        CONN["Session / Engine
(Transactions)"]
        SM["ORM / SQLModel
(Models, Queries)"]
  end
 subgraph APP["Application (Backend)"]
    direction TB
        FP["FastAPI
(ASGI, Routers, Middleware)"]
        PY["Python Logic
(Services/Utilities)"]
        J2["Jinja2 Templates
(SSR HTML)"]
  end
 subgraph CLIENT["Presentation (Client)"]
        BR(["Browser
(HTML/CSS/JS)"])
  end
    BR --> FP
    FP --> PY & BR & J2
    PY --> SM & FP
    SM --> CONN & PY
    CONN --> RDB & SM
    RDB --> CONN
    J2 --> BR
    RDB ~~~ FP
    CONN@{ shape: rect}
    SM@{ shape: doc}
    FP@{ shape: rect}
    PY@{ shape: rect}
    J2@{ shape: docs}
```






