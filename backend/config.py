"""Configuration module for ElevenDops.

This module provides centralized configuration management using
pydantic-settings for environment variable loading with sensible defaults.
"""

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Provides sensible defaults for local development and logs warnings
    for missing non-critical configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application environment
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode",
    )

    # Data Service Configuration
    use_mock_data: bool = Field(
        default=False,
        description="Use MockDataService instead of Firestore (for testing without emulator)",
    )

    # Firestore Configuration
    use_firestore_emulator: bool = Field(
        default=True,
        description="Use Firestore Emulator for local development",
    )
    firestore_emulator_host: str = Field(
        default="localhost:8080",
        description="Firestore Emulator host",
    )

    # GCS Configuration
    use_gcs_emulator: bool = Field(
        default=True,
        description="Use GCS Emulator for local development",
    )
    gcs_emulator_host: str = Field(
        default="http://localhost:4443",
        description="GCS Emulator host",
    )
    gcs_bucket_name: str = Field(
        default="elevenlabs-audio",
        description="GCS bucket name",
    )

    # Backend API configuration
    backend_api_url: str = Field(
        default="http://localhost:8000",
        description="Backend API base URL",
    )
    api_timeout: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="API request timeout in seconds",
    )

    # ElevenLabs API configuration (critical for production)
    elevenlabs_api_key: str | None = Field(
        default=None,
        description="ElevenLabs API key",
    )

    # Google Cloud configuration (critical for production)
    google_cloud_project: str | None = Field(
        default=None,
        description="Google Cloud project ID",
    )

    # CORS configuration
    cors_origins: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501",
        description="Comma-separated list of allowed CORS origins",
    )

    # Server configuration
    streamlit_port: int = Field(
        default=8501,
        ge=1024,
        le=65535,
        description="Streamlit server port",
    )
    fastapi_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="FastAPI server port",
    )

    # Application metadata
    app_version: str = Field(
        default="0.1.0",
        description="Application version",
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Validate CORS origins format."""
        origins = [o.strip() for o in v.split(",") if o.strip()]
        if not origins:
            raise ValueError("At least one CORS origin must be specified")
        return ",".join(origins)

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    def log_configuration_warnings(self) -> None:
        """Log warnings for missing non-critical configuration."""
        if self.elevenlabs_api_key is None:
            logger.warning(
                "ELEVENLABS_API_KEY not set. Voice features will not work."
            )

        if self.google_cloud_project is None:
            logger.warning(
                "GOOGLE_CLOUD_PROJECT not set. Using mock data service."
            )

        if self.debug and self.is_production():
            logger.warning(
                "DEBUG mode is enabled in production. This is not recommended."
            )


class ConfigurationError(Exception):
    """Exception raised for configuration validation failures."""

    def __init__(self, missing_vars: list[str]) -> None:
        self.missing_vars = missing_vars
        message = (
            f"Critical configuration missing: {', '.join(missing_vars)}. "
            "Please set these environment variables before starting the application."
        )
        super().__init__(message)


def validate_critical_config(settings: Settings) -> None:
    """Validate critical configuration for production.

    Raises:
        ConfigurationError: If critical settings are missing in production.
    """
    if not settings.is_production():
        # In development, just log warnings
        settings.log_configuration_warnings()
        return

    # In production, critical settings are required
    missing = []

    if settings.elevenlabs_api_key is None:
        missing.append("ELEVENLABS_API_KEY")

    if settings.google_cloud_project is None:
        missing.append("GOOGLE_CLOUD_PROJECT")

    if missing:
        raise ConfigurationError(missing)

    # Log warnings for non-critical issues
    settings.log_configuration_warnings()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance loaded from environment.
    """
    return Settings()


def initialize_config() -> Settings:
    """Initialize and validate application configuration.

    This should be called at application startup.

    Returns:
        Validated Settings instance.

    Raises:
        ConfigurationError: If critical settings are missing in production.
    """
    settings = get_settings()
    validate_critical_config(settings)
    return settings
