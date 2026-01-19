"""
ApplyWise API - Core Configuration

Manages application settings using Pydantic Settings with environment variable support.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    database_url: str

    # Supabase Auth
    supabase_jwt_secret: str = ""  # Required for JWT validation

    # LLM Provider Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS - accepts comma-separated string
    allowed_origins: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Keep as string, will be split when needed."""
        return v

    def get_allowed_origins_list(self) -> List[str]:
        """Return allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
