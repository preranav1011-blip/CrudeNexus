"""Configuration management for CrudeNexus backend"""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file"""
    
    # Application
    app_name: str = "CrudeNexus"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./crudenexus.db")
    
    # LLM Configuration (Ollama)
    llm_enabled: bool = os.getenv("LLM_ENABLED", "True").lower() == "true"
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "qwen:8b")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    llm_timeout: int = int(os.getenv("LLM_TIMEOUT", "30"))
    
    # GDELT Configuration
    gdelt_keywords: list = [
        "crude oil", "crude-oil", "oil prices",
        "Strait of Hormuz", "Hormuz",
        "Suez Canal", "Suez",
        "Red Sea", "Persian Gulf",
        "sanctions", "embargo",
        "tanker", "shipping", "port disruption",
        "geopolitical", "conflict",
        "India", "Indian",
    ]
    gdelt_lookback_hours: int = 24
    
    # India-specific settings
    india_crude_demand_mbd: float = 4.5  # Million barrels per day
    india_major_ports: list = [
        "Mundra",
        "Jawaharlal Nehru Port",
        "Cochin Port",
        "Paradip Port",
        "Kandla Port",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# LLM Configuration dictionary
LLM_CONFIG = {
    "enabled": settings.llm_enabled,
    "provider": settings.llm_provider,
    "model": settings.llm_model,
    "base_url": settings.llm_base_url,
    "timeout": settings.llm_timeout,
}
