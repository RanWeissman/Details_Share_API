import os
from pathlib import Path

from fastapi.templating import Jinja2Templates

from src.core import api_globals
from src.core.security import Security

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
desire_path = str(PROJECT_ROOT / "src" / "templates")
print(f"test_api_g = {desire_path}")


def test_templates_is_jinja2templates_instance():
    assert isinstance(api_globals.templates, Jinja2Templates)
    loader = api_globals.templates.env.loader

    # Jinja2 FileSystemLoader uses "searchpath"
    if hasattr(loader, "searchpath"):
        search_paths = [os.path.normpath(str(p)) for p in loader.searchpath]
    else:
        search_paths = []

    expected = os.path.normpath(desire_path)
    assert expected in search_paths


def test_security_is_security_instance():
    assert isinstance(api_globals.security, Security)

    assert api_globals.security is api_globals.security