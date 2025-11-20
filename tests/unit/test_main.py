# tests/unit/test_main.py

from fastapi.testclient import TestClient
from starlette.responses import Response

import src.main as main
from src.main import app, logger


def test_debug_routes_returns_html():
    """
    בודק שה־endpoint /api/debug/routes מחזיר HTML
    ושיש בו לפחות את השורה של עצמו.
    """
    client = TestClient(app)
    resp = client.get("/api/debug/routes")

    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "").lower()

    body = resp.text
    # לפי המימוש: "['GET']  /api/debug/routes  -> debug_routes"
    assert "/api/debug/routes" in body
    assert "debug_routes" in body


def test_log_request_time_header_added():
    """
    בודק שהמידלוור log_request_time מוסיף כותרת X-Process-Time
    עם פורמט '<float> sec'.
    """
    client = TestClient(app)
    resp = client.get("/api/debug/routes")

    assert resp.status_code == 200
    assert "X-Process-Time" in resp.headers

    value = resp.headers["X-Process-Time"]
    # פורמט: "<זמן> sec"
    parts = value.split()
    assert len(parts) == 2
    time_part, unit = parts
    assert unit == "sec"
    # לוודא שאפשר להמיר ל-float
    float(time_part)


def test_cors_allows_localhost_origin():
    """
    בודק שה-CORS Middleware מאפשר Origin מה-Whitelist
    (כמו http://localhost:3000) ומחזיר Access-Control-Allow-Origin.
    """
    client = TestClient(app)
    resp = client.get(
        "/api/debug/routes",
        headers={"Origin": "http://localhost:3000"},
    )

    # אם ה-origin מורשה, אמור להיות header תואם
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_favicon_uses_fileresponse(monkeypatch):
    """
    בודק את /favicon.ico בלי להסתמך על קובץ אמיתי בדיסק,
    בעזרת monkeypatch על FileResponse.
    """

    # נחליף את main.FileResponse בפונקציה שמחזירה Response פשוט
    def fake_file_response(path: str):
        return Response(content=b"ICON", media_type="image/x-icon")

    monkeypatch.setattr(main, "FileResponse", fake_file_response)

    client = TestClient(app)
    resp = client.get("/favicon.ico")

    assert resp.status_code == 200
    assert resp.content == b"ICON"
    assert resp.headers.get("content-type") == "image/x-icon"


def test_lifespan_logs_startup_and_shutdown(caplog):
    """
    בודק שה-lifespan כותב לוגים של התחלה וסיום:
    "DB initialize..." ו-"Shutdown complete".
    משתמשים ב-TestClient כ-context manager כדי להבטיח
    גם startup וגם shutdown.
    """
    from logging import INFO

    with caplog.at_level(INFO, logger=logger.name):
        with TestClient(app) as client:
            resp = client.get("/api/debug/routes")
            assert resp.status_code == 200

    messages = [record.getMessage() for record in caplog.records]
    assert any("DB initialize" in msg for msg in messages)
    assert any("Shutdown complete" in msg for msg in messages)
