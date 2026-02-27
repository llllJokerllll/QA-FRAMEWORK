import os
import warnings
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment-based configuration.
    
    Security: All sensitive values MUST be provided via environment variables.
    Defaults are ONLY for local development and will trigger warnings.
    """
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database - REQUIRED in production
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # JWT - REQUIRED in production
    secret_key: Optional[str] = os.getenv("JWT_SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # QA Framework Integration
    qa_framework_api_url: str = os.getenv("QA_FRAMEWORK_API_URL", "http://localhost:8001")
    
    # Frontend
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Stripe - REQUIRED for billing
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Feature Flags
    ENABLE_BILLING: bool = os.getenv("ENABLE_BILLING", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_production_config()
        self._warn_insecure_defaults()
    
    def _validate_production_config(self):
        """Validate that all required variables are set in production."""
        if self.ENVIRONMENT == "production":
            required_vars = {
                "DATABASE_URL": self.database_url,
                "JWT_SECRET_KEY": self.secret_key,
            }
            
            if self.ENABLE_BILLING:
                required_vars.update({
                    "STRIPE_API_KEY": self.STRIPE_API_KEY,
                    "STRIPE_WEBHOOK_SECRET": self.STRIPE_WEBHOOK_SECRET,
                })
            
            missing = [k for k, v in required_vars.items() if not v]
            if missing:
                raise ValueError(
                    f"Missing required environment variables in production: {', '.join(missing)}. "
                    "Set these variables before starting the application."
                )
    
    def _warn_insecure_defaults(self):
        """Warn when using insecure default values."""
        if self.ENVIRONMENT != "production":
            warnings = []
            
            if not self.database_url:
                warnings.append("DATABASE_URL not set - using in-memory SQLite (not suitable for production)")
            
            if not self.secret_key:
                warnings.append("JWT_SECRET_KEY not set - generating temporary key (sessions will not persist)")
            
            if self.ENABLE_BILLING and not self.STRIPE_API_KEY:
                warnings.append("Billing enabled but STRIPE_API_KEY not set - billing will fail")
            
            for warning in warnings:
                warnings.warn(warning, UserWarning)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Backward compatibility - will be deprecated
settings = get_settings()
