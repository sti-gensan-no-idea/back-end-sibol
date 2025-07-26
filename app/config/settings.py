# app/config/settings.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sibol")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AI_API_KEY: str = os.getenv("AI_API_KEY", "your-ai-api-key")
    AR_MODEL_STORAGE_URL: str = os.getenv("AR_MODEL_STORAGE_URL", "https://storage.example.com/ar-models")

settings = Settings()