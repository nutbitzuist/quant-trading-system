"""
Application Configuration
Environment variables and settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    app_name: str = "Quant Trading System"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # API settings
    api_prefix: str = "/api"
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Data settings
    data_cache_ttl: int = 3600  # 1 hour
    
    # SET100 Universe
    default_universe: str = "SET100"
    
    # Model settings
    regime_lookback_days: int = 50
    volatility_lookback_days: int = 20
    
    # Database (optional for future)
    database_url: Optional[str] = None
    
    # External APIs (optional)
    setsmart_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
