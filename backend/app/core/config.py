from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "euTnDB"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://tndb:tndb@localhost:5432/tndb"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80", "http://localhost:8001"]
    
    DATA_DIR: str = "./data"
    UPLOAD_DIR: str = "./data/uploads"
    GENOME_DIR: str = "./data/genomes"
    BLAST_DB_DIR: str = "./data/blast_db"
    EXPORT_DIR: str = "./data/exports"
    
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024

    # Default admin account — only used on first startup
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@tndb.org"
    ADMIN_PASSWORD: str = ""

    SMTP_HOST: str = ""
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "euTnDB"
    SMTP_USE_SSL: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
