"""
Application Settings Configuration
Handles environment variables and application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # App Information
    APP_NAME: str = Field(default="Sibol API", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    APP_DESCRIPTION: str = Field(default="A back-end for Sibol.", env="APP_DESCRIPTION")
    APP_KEY: str = Field(default="", env="APP_KEY")
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Database Configuration
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_DB_URL: str = Field(..., env="SUPABASE_DB_URL")
    
    # Database Connection Settings
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRY: int = Field(default=30, env="ACCESS_TOKEN_EXPIRY")
    REFRESH_TOKEN_EXPIRY: int = Field(default=7, env="REFRESH_TOKEN_EXPIRY")
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # SMTP Configuration
    SMTP_SERVER: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # External Services
    AI_API_KEY: str = Field(default="", env="AI_API_KEY")
    AR_MODEL_STORAGE_URL: str = Field(
        default="https://storage.example.com/ar-models", 
        env="AR_MODEL_STORAGE_URL"
    )
    
    # Payment Configuration
    PAYFUSION_SECRET_KEY: str = Field(default="", env="PAYFUSION_SECRET_KEY")
    PAYFUSION_WEBHOOK_SECRET: str = Field(default="", env="PAYFUSION_WEBHOOK_SECRET")
    PAYFUSION_API_URL: str = Field(
        default="https://api.payfusion.ph", 
        env="PAYFUSION_API_URL"
    )
    
    # Redis Configuration (for caching and sessions)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".webp"], 
        env="ALLOWED_IMAGE_EXTENSIONS"
    )
    ALLOWED_MODEL_EXTENSIONS: List[str] = Field(
        default=[".glb", ".gltf", ".obj", ".fbx"], 
        env="ALLOWED_MODEL_EXTENSIONS"
    )
    
    # API Configuration
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    API_RATE_LIMIT: str = Field(default="100/minute", env="API_RATE_LIMIT")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url(self) -> str:
        return self.SUPABASE_DB_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
settings = Settings()
