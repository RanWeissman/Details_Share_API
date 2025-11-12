import uvicorn
from importlib import import_module

from src.core.settings import get_settings


def _prepare_app():
    """Load settings and initialize the DB singleton so tables are created
    before the ASGI server starts. This mirrors the startup lifespan but
    ensures the same behavior when running via `python -m src.run_server`.
    """
    # load settings (reads .env)
    settings = get_settings()

    # initialize DB core (creates tables) if not already created
    try:
        db_core = import_module("src.database.db_core")
        if not getattr(db_core.DBCore, "_instance", False):
            db_core.DBCore()
    except Exception as exc:
        # print a friendly message but continue; the FastAPI lifespan will also try
        print("Warning: failed to initialize DB at startup:", exc)


if __name__ == "__main__":
    _prepare_app()
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)