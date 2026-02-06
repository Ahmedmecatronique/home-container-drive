from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
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
