import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://qa_user:qa_password@localhost/qa_framework_db"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # JWT
    secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # QA Framework Integration
    qa_framework_api_url: str = "http://localhost:8001"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Stripe
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "sk_test_placeholder")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")
    
    class Config:
        env_file = ".env"


settings = Settings()