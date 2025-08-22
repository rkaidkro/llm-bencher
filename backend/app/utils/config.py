"""
Configuration management for the LLM Testing Interface.

This module provides a centralized configuration system that loads settings
from environment variables and provides type-safe access to configuration values.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field, validator
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./llm_interface.db",
        description="Database connection URL"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # LLM Services Configuration
    default_llm_service: str = Field(
        default="ollama", 
        description="Default LLM service to use"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio API base URL"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Logging Configuration
    log_format: str = Field(default="json", description="Log format")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    # Benchmark Configuration
    benchmark_results_dir: str = Field(
        default="../reports",
        description="Directory for benchmark results"
    )
    max_concurrent_benchmarks: int = Field(
        default=3,
        description="Maximum concurrent benchmark executions"
    )
    
    # Development Configuration
    environment: str = Field(default="development", description="Environment name")
    
    @validator('allowed_origins', pre=True)
    def parse_allowed_origins(cls, v):
        """Parse allowed origins from string or list."""
        if isinstance(v, str):
            # Handle JSON string format
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    @validator('log_file')
    def ensure_log_directory_exists(cls, v):
        """Ensure log directory exists."""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('benchmark_results_dir')
    def ensure_benchmark_directory_exists(cls, v):
        """Ensure benchmark results directory exists."""
        benchmark_path = Path(v)
        benchmark_path.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def get_database_url() -> str:
    """Get the database URL from settings."""
    return settings.database_url


def get_llm_service_url(service_name: str) -> Optional[str]:
    """Get the base URL for a specific LLM service."""
    service_urls = {
        "ollama": settings.ollama_base_url,
        "lm_studio": settings.lm_studio_base_url,
    }
    return service_urls.get(service_name.lower())


def is_development() -> bool:
    """Check if running in development mode."""
    return settings.environment.lower() == "development"


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return settings.debug
