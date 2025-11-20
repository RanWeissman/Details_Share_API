
from fastapi.testclient import TestClient
from starlette.responses import Response

import src.main as main
from src.main import app, logger


def test_debug_routes_returns_html():

    client = TestClient(app)
    response = client.get("/api/debug/routes")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "").lower()

    body = response.text
    assert "/api/debug/routes" in body
    assert "debug_routes" in body


def test_log_request_time_header_added():
    client = TestClient(app)
    response = client.get("/api/debug/routes")

    assert response.status_code == 200
    assert "X-Process-Time" in response.headers

    value = response.headers["X-Process-Time"]
    parts = value.split()
    assert len(parts) == 2
    time_part, unit = parts
    assert unit == "sec"
    float(time_part)


def test_cors_allows_localhost_origin():
    client = TestClient(app)
    response = client.get(
        "/api/debug/routes",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_favicon_uses_fileresponse(monkeypatch):
    def fake_file_response(path: str):
        return Response(content=b"ICON", media_type="image/x-icon")

    monkeypatch.setattr(main, "FileResponse", fake_file_response)

    client = TestClient(app)
    response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.content == b"ICON"
    assert response.headers.get("content-type") == "image/x-icon"


def test_lifespan_logs_startup_and_shutdown(caplog):
    from logging import INFO

    with caplog.at_level(INFO, logger=logger.name):
        with TestClient(app) as client:
            response = client.get("/api/debug/routes")
            assert response.status_code == 200

    messages = [record.getMessage() for record in caplog.records]
    assert any("DB initialize" in msg for msg in messages)
    assert any("Shutdown complete" in msg for msg in messages)
