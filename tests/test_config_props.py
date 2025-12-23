"""Property tests for configuration module.

Property 7: Environment variable defaults
- Test defaults are used when env vars missing
Validates: Requirements 6.2

Property 8: Critical configuration validation
- Test application fails fast for missing critical config
Validates: Requirements 6.3
"""

import os
from unittest.mock import patch

import pytest
from hypothesis import given, settings as hypothesis_settings, strategies as st

from backend.config import (
    ConfigurationError,
    Settings,
    get_settings,
    initialize_config,
    validate_critical_config,
)


class TestEnvironmentDefaults:
    """Property 7: Environment variable defaults."""

    def test_default_app_env_is_development(self) -> None:
        """Test that default app_env is 'development'."""
        with patch.dict(os.environ, {}, clear=True):
            get_settings.cache_clear()
            settings = Settings()
            assert settings.app_env == "development"

    def test_default_debug_is_true(self) -> None:
        """Test that default debug is True."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.debug is True

    def test_default_backend_api_url(self) -> None:
        """Test that default backend_api_url is localhost."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.backend_api_url == "http://localhost:8000"

    def test_default_api_timeout(self) -> None:
        """Test that default api_timeout is 10 seconds."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.api_timeout == 10.0

    def test_default_streamlit_port(self) -> None:
        """Test that default streamlit_port is 8501."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.streamlit_port == 8501

    def test_default_fastapi_port(self) -> None:
        """Test that default fastapi_port is 8000."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.fastapi_port == 8000

    def test_default_cors_origins(self) -> None:
        """Test that default CORS origins include localhost."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            origins = settings.get_cors_origins_list()
            assert "http://localhost:8501" in origins

    def test_environment_variable_overrides_default(self) -> None:
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {"BACKEND_API_URL": "http://custom:9000"}):
            settings = Settings()
            assert settings.backend_api_url == "http://custom:9000"

    @given(port=st.integers(min_value=1024, max_value=65535))
    @hypothesis_settings(max_examples=10)
    def test_valid_port_numbers_accepted(self, port: int) -> None:
        """Property: Any valid port number is accepted."""
        with patch.dict(os.environ, {"STREAMLIT_PORT": str(port)}):
            settings = Settings()
            assert settings.streamlit_port == port


class TestCriticalConfigValidation:
    """Property 8: Critical configuration validation."""

    def test_development_mode_does_not_raise_for_missing_keys(self) -> None:
        """Test that development mode allows missing critical keys."""
        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=True):
            settings = Settings()
            # Should not raise
            validate_critical_config(settings)

    def test_production_mode_raises_for_missing_elevenlabs_key(self) -> None:
        """Test that production mode requires ELEVENLABS_API_KEY."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            with pytest.raises(ConfigurationError) as exc_info:
                validate_critical_config(settings)
            assert "ELEVENLABS_API_KEY" in exc_info.value.missing_vars

    def test_production_mode_raises_for_missing_gcp_project(self) -> None:
        """Test that production mode requires GOOGLE_CLOUD_PROJECT."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            with pytest.raises(ConfigurationError) as exc_info:
                validate_critical_config(settings)
            assert "GOOGLE_CLOUD_PROJECT" in exc_info.value.missing_vars

    def test_production_mode_raises_for_all_missing_critical_vars(self) -> None:
        """Test that production mode lists all missing critical vars."""
        with patch.dict(
            os.environ,
            {"APP_ENV": "production"},
            clear=True,
        ):
            settings = Settings(_env_file=None)
            with pytest.raises(ConfigurationError) as exc_info:
                validate_critical_config(settings)
            assert "ELEVENLABS_API_KEY" in exc_info.value.missing_vars
            assert "GOOGLE_CLOUD_PROJECT" in exc_info.value.missing_vars

    def test_production_mode_succeeds_with_all_critical_vars(self) -> None:
        """Test that production mode succeeds with all critical vars set."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings()
            # Should not raise
            validate_critical_config(settings)

    def test_configuration_error_has_meaningful_message(self) -> None:
        """Test that ConfigurationError has a meaningful message."""
        error = ConfigurationError(["VAR1", "VAR2"])
        assert "VAR1" in str(error)
        assert "VAR2" in str(error)
        assert "Critical configuration missing" in str(error)

    def test_initialize_config_validates_production(self) -> None:
        """Test that initialize_config validates critical config."""
        with patch.dict(
            os.environ,
            {"APP_ENV": "production"},
            clear=True,
        ):
            get_settings.cache_clear()
            with pytest.raises(ConfigurationError):
                initialize_config()


class TestSettingsMethods:
    """Tests for Settings helper methods."""

    def test_is_production_returns_true_for_production(self) -> None:
        """Test is_production returns True for production env."""
        with patch.dict(os.environ, {"APP_ENV": "production"}):
            settings = Settings()
            assert settings.is_production() is True

    def test_is_production_returns_false_for_development(self) -> None:
        """Test is_production returns False for development env."""
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            settings = Settings()
            assert settings.is_production() is False

    def test_get_cors_origins_list_parses_correctly(self) -> None:
        """Test CORS origins are parsed into a list."""
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "http://a.com, http://b.com , http://c.com"},
        ):
            settings = Settings()
            origins = settings.get_cors_origins_list()
            assert origins == ["http://a.com", "http://b.com", "http://c.com"]
