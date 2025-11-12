import os
from typing import Optional


def _load_dotenv(dotenv_path: str = None) -> None:
    """Lightweight .env loader: parse KEY=VALUE lines and set os.environ

    This avoids adding the `python-dotenv` dependency while still allowing
    developers to keep configuration in a .env file located at the project
    root.
    """
    path = dotenv_path or os.path.join(os.getcwd(), ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Only set if not already present in environment
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # If loading fails, don't block app startup; environment variables
        # may be provided via other means in production.
        pass


# load .env if present
_load_dotenv()


class Settings:
    """Lightweight settings object that reads values from environment variables.

    This avoids a hard dependency on `pydantic` base settings API and is
    sufficient for constructing the database URL and simple configuration.
    """

    def __init__(self):
        self.DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
        self.DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")
        self.DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
        self.DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
        self.DATABASE_NAME: str = os.getenv("DATABASE_NAME", "mydb")
        # Optional full URL override (if provided, use it as-is)
        self.DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    @property
    def database_url(self) -> str:
        # If an explicit DATABASE_URL is supplied, prefer it.
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # Try to use PostgreSQL driver if available; otherwise fall back to SQLite
        try:
            import psycopg2  # type: ignore
            pg_available = True
        except Exception:
            pg_available = False

        if pg_available:
            return (
                f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )

        # Fall back to a local SQLite file for development if psycopg2 isn't installed.
        sqlite_path = os.path.join(os.getcwd(), "ourDB.db")
        print(
            "Warning: psycopg2 not available — falling back to SQLite at",
            sqlite_path,
            "\nTo use PostgreSQL install psycopg2-binary and set DATABASE_URL in .env",
        )
        return f"sqlite:///{sqlite_path}"


def get_settings() -> Settings:
    return Settings()
