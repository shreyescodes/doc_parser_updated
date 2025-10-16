"""
Configuration settings for the document parser application.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "postgresql://postgres:1234@localhost:5432/doc_parser"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "doc_parser"
    db_user: str = "postgres"
    db_password: str = "1234"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Storage (MinIO)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "documents"
    minio_secure: bool = False
    
    # Application Settings
    upload_dir: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions_str: str = "pdf,png,jpg,jpeg,tiff"
    
    @property
    def allowed_extensions(self) -> list:
        """Convert comma-separated extensions string to list."""
        return [ext.strip() for ext in self.allowed_extensions_str.split(",")]
    
    # OCR Settings
    tesseract_cmd: str = "/usr/bin/tesseract"
    tesseract_lang: str = "eng"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # API Settings
    api_title: str = "LP Document Parser API"
    api_description: str = "API for processing Limited Partner fiduciary documents"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()

# Ensure directories exist
Path(settings.upload_dir).mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
