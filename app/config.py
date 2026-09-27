from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Ensure the local data directory exists for SQLite
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "TRAC-Tel"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/trac_tel.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()