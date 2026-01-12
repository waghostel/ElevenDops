"""Configuration module for ElevenDops.

This module provides centralized configuration management using
pydantic-settings for environment variable loading with sensible defaults.
"""

import logging
import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator, ValidatorFunctionWrapHandler
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any

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

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Any) -> Any:
        """Strip whitespace from all string environment variables before parsing."""
        if isinstance(v, str):
            stripped = v.strip()
            if stripped != v:
                logger.debug(f"Stripped whitespace from environment variable")
            return stripped
        return v

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
    firestore_database_id: str = Field(
        default="elevendops-db-test",
        description="Firestore database ID (use '(default)' for the default database)",
    )

    # GCS Configuration
    use_mock_storage: bool = Field(
        default=False,
        description="Use local file system mock instead of GCS (for testing)",
    )
    use_gcs_emulator: bool = Field(
        default=True,
        description="Use GCS Emulator for local development",
    )
    gcs_emulator_host: str = Field(
        default="http://localhost:4443",
        description="GCS Emulator host",
    )
    gcs_bucket_name: str = Field(
        default="elevendops-bucket-test",
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
    use_mock_elevenlabs: bool = Field(
        default=False,
        description="Use mock ElevenLabs service (for testing without API key)",
    )

    # Google Cloud configuration (critical for production)
    google_cloud_project: str | None = Field(
        default=None,
        description="Google Cloud project ID",
    )
    
    # Google AI configuration
    google_api_key: str | None = Field(
        default=None,
        description="Google API key for Gemini models",
    )

    # LangSmith configuration
    langsmith_api_key: str | None = Field(
        default=None,
        description="LangSmith API key for tracing and debugging",
    )
    langsmith_project: str = Field(
        default="elevendops-langgraph-debug",
        description="LangSmith project name for trace organization",
    )
    langsmith_tracing_enabled: bool = Field(
        default=True,
        description="Enable LangSmith tracing (requires API key)",
    )
    langsmith_trace_level: Literal["debug", "info", "error"] = Field(
        default="info",
        description="LangSmith trace verbosity level",
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

    @model_validator(mode='after')
    def enforce_emulator_priority(self) -> 'Settings':
        """Ensure emulators take precedence over mock mode."""
        if self.use_firestore_emulator:
            if self.use_mock_data:
                logger.warning("Overriding use_mock_data=True because use_firestore_emulator is True")
            self.use_mock_data = False
            
        if self.use_gcs_emulator:
            if self.use_mock_storage:
                logger.warning("Overriding use_mock_storage=True because use_gcs_emulator is True")
            self.use_mock_storage = False
            
        return self

    @model_validator(mode='after')
    def ensure_localhost_cors_in_production(self) -> 'Settings':
        """Ensure localhost origins are included in CORS for internal communication.
        
        In Cloud Run, the frontend (Streamlit) communicates with the backend (FastAPI)
        via localhost. This validator ensures localhost origins are always included.
        """
        localhost_origins = ["http://localhost:8000", "http://127.0.0.1:8000"]
        current_origins = self.get_cors_origins_list()
        
        # Add localhost origins if not present
        origins_to_add = [o for o in localhost_origins if o not in current_origins]
        if origins_to_add:
            updated_origins = current_origins + origins_to_add
            self.cors_origins = ",".join(updated_origins)
            
        return self

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    def is_langsmith_configured(self) -> bool:
        """Check if LangSmith is properly configured and ready to use.
        
        Returns:
            True if API key is set and tracing is enabled.
        """
        return (
            self.langsmith_api_key is not None 
            and self.langsmith_tracing_enabled
        )

    def configure_langsmith_environment(self) -> None:
        """Set LangSmith environment variables for the langsmith library.
        
        The langsmith library reads configuration from environment variables.
        This method sets them based on our Settings.
        """
        if self.langsmith_api_key:
            os.environ["LANGCHAIN_API_KEY"] = self.langsmith_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project
            os.environ["LANGCHAIN_TRACING_V2"] = str(self.langsmith_tracing_enabled).lower()

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

    def log_langsmith_warnings(self) -> None:
        """Log warnings for LangSmith configuration."""
        if self.langsmith_api_key is None:
            logger.warning(
                "LANGSMITH_API_KEY not set. LangGraph tracing will be disabled."
            )
        elif not self.langsmith_tracing_enabled:
            logger.info(
                "LangSmith tracing is disabled via LANGSMITH_TRACING_ENABLED."
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

    if settings.google_api_key is None:
        missing.append("GOOGLE_API_KEY")

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


# Gemini model configurations (LangChain-compatible names)
# Ref: https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai.md
GEMINI_MODELS = {
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-3-pro-preview": "gemini-3-pro-preview"
}

from pathlib import Path

def get_default_script_prompt() -> str:
    """Load default script generation prompt from config file.
    
    Returns:
        str: Default prompt text
    """
    try:
        prompt_path = Path(__file__).parent / "config" / "default_script_prompt.txt"
        if not prompt_path.exists():
            # Fallback if file doesn't exist (e.g. in tests)
            logger.warning(f"Default prompt file not found at {prompt_path}, using built-in fallback")
            return "You are a medical script writer. Generate a patient education script."
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to load default script prompt: {e}")
        return "You are a medical script writer. Generate a patient education script."
