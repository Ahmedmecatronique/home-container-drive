from pydantic_settings import BaseSettings
from typing import List
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security - Generate a random secret key if not provided
    secret_key: str = secrets.token_urlsafe(32)
    api_username: str = "admin"
    api_password: str = "admin"
    
    # Storage
    storage_path: str = "./storage"
    max_upload_size: int = 104857600  # 100MB
    
    # CORS
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
