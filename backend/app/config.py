"""
Centralized application configuration.

Why this file exists:
    Every value here changes between environments (local dev, interview
    laptop demo, a future deployment) and none of it should be hardcoded
    in source code — especially secrets like the JWT signing key and the
    database password. pydantic-settings reads these from environment
    variables (or a local .env file) and validates them once, at startup,
    instead of every part of the app reaching into os.environ directly.

Who uses this:
    - database.py reads DATABASE_URL to create the SQLAlchemy engine
    - core/security.py reads JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
    - main.py reads CORS_ORIGINS to configure allowed frontend origins
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = (
        "mysql+pymysql://root:password@localhost:3306/attendance_db"
    )

    # --- JWT / Security ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_ENV_FILE"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 90

    # --- CORS ---
    # Comma-separated list of allowed frontend origins, e.g.
    # "http://localhost:5173,http://localhost:3000"
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- App metadata ---
    APP_NAME: str = "Mini Attendance Management System"
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINS as a list, since FastAPI's CORS middleware wants a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Single shared instance, imported wherever settings are needed:
#   from app.config import settings
settings = Settings()
