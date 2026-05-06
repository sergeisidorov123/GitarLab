from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Catalog Service"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@catalog-db:5432/catalog"
    CORS_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()