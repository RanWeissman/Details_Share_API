
from fastapi.templating import Jinja2Templates
from src.core.security import Security

templates = Jinja2Templates(directory="src/templates")

security = Security()
