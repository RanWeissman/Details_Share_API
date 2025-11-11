# src/main.py
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
from fastapi.responses import HTMLResponse

from src import app_logging
from src.api.contacts import contacts_router
from src.api.accounts import accounts_router

####################################################################### Logging Configuration
app_logging.configure_logging()
logger = app_logging.get_logger("main logger: ")
####################################################################### Lifespan Event Handler
@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("DB initialize - This is how we do it !!")
    base = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
    logger.info(f"App is running at {base} (docs: {base}/docs)")
    try:
        yield
    finally:
        logger.info("Shutdown complete")
####################################################################### FastAPI App Initialization
app = FastAPI(lifespan=lifespan)
####################################################################### Include Routers
app.include_router(accounts_router)
app.include_router(contacts_router)
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

####################################################################### Debugging Endpoints
@app.get("/api/debug/routes")
def debug_routes() -> HTMLResponse:
    lines = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            lines.append(f"{sorted(r.methods)}  {r.path}  -> {r.endpoint.__name__}")
    html = "<br>".join(lines)
    return HTMLResponse(content=html)


"""
python -m src.run_server
"""