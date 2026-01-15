from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Database
    database_url: str = "sqlite:///./chatbot.db"
    # For PostgreSQL, use:
    # database_url: str = "postgresql://user:password@localhost:5432/chatbot_db"
    
    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Google Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:8080"
    ]
    
    # Application
    app_name: str = "Chatbot Assistant API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
