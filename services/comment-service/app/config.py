from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Comment Service"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres-db:5432/courseproject"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # User service URL for authentication
    USER_SERVICE_URL: str = "http://user-service:8002"

    class Config:
        env_file = ".env"


settings = Settings()