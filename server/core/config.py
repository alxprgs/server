from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    MONGO_URL: str
    MYSQL_URL: Optional[str] = None
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = 6379
    REDIS_PASSWORD : Optional[str] = None
    MONGO_DB: str = "ASFES"
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: list[str] = ["*"]
    SERVER_PORT: Optional[int] = 5005
    PROJECT_NAME: str = "Automatic Spot Fire Extinguishing System"
    VERSION: str = "STABLE 12.0.0 | Build 27.04.2025"
    ROOTUSER_PASSWORD: Optional[str] ="root"
    
    class Config:
        env_file = ".env"

settings = Settings()
