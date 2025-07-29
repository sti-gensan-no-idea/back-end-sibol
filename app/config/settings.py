from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "Sibol API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "A back-end for Sibol.")
    APP_KEY: str = os.getenv("APP_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRY: int = int(os.getenv("ACCESS_TOKEN_EXPIRY", 30))
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "your-ai-api-key")
    AR_MODEL_STORAGE_URL: str = os.getenv("AR_MODEL_STORAGE_URL", "https://storage.example.com/ar-models")
    PAYFUSION_SECRET_KEY: str = os.getenv("PAYFUSION_SECRET_KEY", "")
    PAYFUSION_WEBHOOK_SECRET: str = os.getenv("PAYFUSION_WEBHOOK_SECRET", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()