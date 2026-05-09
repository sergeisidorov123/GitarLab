from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "User Service"
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres-db:5432/courseproject"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    PASSWORD_SALT: str = "user-service-salt"

    class Config:
        env_file = ".env"

settings = Settings()
