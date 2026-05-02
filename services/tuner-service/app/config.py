from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Tuner Service"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    SAMPLE_RATE: int = 44100
    
    class Config:
        env_file = ".env"

settings = Settings()