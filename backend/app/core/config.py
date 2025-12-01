"""
Core configuration settings for the Pet Health API
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    database_url: str = "postgresql://petuser:petpass@localhost:5432/petdb"
    database_url_async: str = "postgresql+asyncpg://petuser:petpass@localhost:5432/petdb"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    secret_key: str = "your-super-secure-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Service settings
    ai_provider: str = "ollama"  # "ollama" or "openai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:latest"
    openai_api_key: Optional[str] = None
    
    # Application settings
    debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Pet Health API"
    version: str = "1.0.0"
    description: str = "AI-powered pet health symptom tracking and analysis"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    @validator('cors_origins', pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()