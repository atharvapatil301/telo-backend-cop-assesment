"""
Configuration module for TeloHive Venue Knowledge Assistant.

This module defines all application settings including database connections,
API keys, embedding configurations, and caching parameters.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables or .env file.
    """

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5

    CACHE_TTL: int = 3600
    ENABLE_CACHE: bool = True

    LLM_MODEL: str = "claude-3-haiku-20240307"
    LLM_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1024

    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
