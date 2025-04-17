from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    MYSQL_URL: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    MONGO_DB: str = "ASFES"
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["*"]
    SERVER_PORT: int = 5005
    PROJECT_NAME: str = "Automatic Spot Fire Extinguishing System"
    VERSION: str = "DEV 11.1.0 | Build 17.04.2025"
    ROOTUSER_PASSWORD: Optional[str] ="root"
    
    class Config:
        env_file = ".env"

settings = Settings()
