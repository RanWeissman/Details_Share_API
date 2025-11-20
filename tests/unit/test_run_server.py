import runpy
import uvicorn


def test_run_server_invokes_uvicorn_run_with_correct_args(monkeypatch):
    called = {}

    def fake_run(app, host=None, port=None, reload=None):
        called["app"] = app
        called["host"] = host
        called["port"] = port
        called["reload"] = reload

    monkeypatch.setattr(uvicorn, "run", fake_run)

    runpy.run_module("src.run_server", run_name="__main__")

    assert called["app"] == "src.main:app"
    assert called["host"] == "127.0.0.1"
    assert called["port"] == 8000
    assert called["reload"] is True