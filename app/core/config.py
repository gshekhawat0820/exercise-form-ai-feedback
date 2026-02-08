"""
Application configuration management using Pydantic Settings.

This module provides type-safe configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str
    model_name: str = "gpt-4o"
    max_video_size_mb: int = 50
    max_video_duration_sec: int = 30
    min_video_duration_sec: int = 5
    frame_count: int = 5
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()
