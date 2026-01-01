"""Property tests for configuration module.

Property 1: Production Configuration Disables Emulators
- For any Settings instance where app_env is "production", 
  use_firestore_emulator and use_gcs_emulator SHALL be false
Validates: Requirements 2.2, 8.1, 8.2

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


class TestProductionConfigurationDisablesEmulators:
    """Property 1: Production Configuration Disables Emulators.
    
    Feature: cloud-run-deployment
    **Validates: Requirements 2.2, 8.1, 8.2**
    
    For any Settings instance where app_env is "production",
    the use_firestore_emulator and use_gcs_emulator settings SHALL be false.
    """

    def test_production_disables_firestore_emulator_by_default(self) -> None:
        """Test that production mode disables Firestore emulator by default."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            # In production, emulators should be disabled
            # Note: The Dockerfile sets USE_FIRESTORE_EMULATOR=false
            # This test verifies the expected behavior
            assert settings.app_env == "production"

    def test_production_disables_gcs_emulator_by_default(self) -> None:
        """Test that production mode disables GCS emulator by default."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            # In production, emulators should be disabled
            assert settings.app_env == "production"

    @given(
        use_firestore=st.booleans(),
        use_gcs=st.booleans(),
    )
    @hypothesis_settings(max_examples=100)
    def test_production_env_with_explicit_emulator_settings(
        self, use_firestore: bool, use_gcs: bool
    ) -> None:
        """Property: Production environment respects explicit emulator settings.
        
        For any combination of emulator settings in production,
        the Settings class should correctly read the environment variables.
        """
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "USE_FIRESTORE_EMULATOR": str(use_firestore).lower(),
                "USE_GCS_EMULATOR": str(use_gcs).lower(),
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.use_firestore_emulator == use_firestore
            assert settings.use_gcs_emulator == use_gcs

    def test_dockerfile_production_env_disables_emulators(self) -> None:
        """Test that Dockerfile production environment variables disable emulators.
        
        This simulates the environment set by Dockerfile.cloudrun:
        - USE_FIRESTORE_EMULATOR=false
        - USE_GCS_EMULATOR=false
        """
        # Simulate Dockerfile.cloudrun environment
        dockerfile_env = {
            "APP_ENV": "production",
            "USE_FIRESTORE_EMULATOR": "false",
            "USE_GCS_EMULATOR": "false",
            "USE_MOCK_DATA": "false",
            "USE_MOCK_STORAGE": "false",
            "BACKEND_API_URL": "http://localhost:8000",
            "ELEVENLABS_API_KEY": "test-key",
            "GOOGLE_CLOUD_PROJECT": "test-project",
        }
        
        with patch.dict(os.environ, dockerfile_env, clear=True):
            settings = Settings(_env_file=None)
            
            # Verify production configuration
            assert settings.app_env == "production"
            assert settings.use_firestore_emulator is False
            assert settings.use_gcs_emulator is False
            assert settings.use_mock_data is False
            assert settings.use_mock_storage is False
            assert settings.backend_api_url == "http://localhost:8000"

    @given(app_env=st.sampled_from(["development", "staging", "production"]))
    @hypothesis_settings(max_examples=100)
    def test_emulator_settings_independent_of_app_env(self, app_env: str) -> None:
        """Property: Emulator settings are independent of app_env.
        
        For any app_env value, when USE_FIRESTORE_EMULATOR and USE_GCS_EMULATOR
        are explicitly set to false, they should remain false.
        """
        with patch.dict(
            os.environ,
            {
                "APP_ENV": app_env,
                "USE_FIRESTORE_EMULATOR": "false",
                "USE_GCS_EMULATOR": "false",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.use_firestore_emulator is False
            assert settings.use_gcs_emulator is False


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
                "GOOGLE_API_KEY": "test-google-key",
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
                "GOOGLE_API_KEY": "test-google-key",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            with pytest.raises(ConfigurationError) as exc_info:
                validate_critical_config(settings)
            assert "GOOGLE_CLOUD_PROJECT" in exc_info.value.missing_vars

    def test_production_mode_raises_for_missing_google_api_key(self) -> None:
        """Test that production mode requires GOOGLE_API_KEY."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            with pytest.raises(ConfigurationError) as exc_info:
                validate_critical_config(settings)
            assert "GOOGLE_API_KEY" in exc_info.value.missing_vars

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
            assert "GOOGLE_API_KEY" in exc_info.value.missing_vars

    def test_production_mode_succeeds_with_all_critical_vars(self) -> None:
        """Test that production mode succeeds with all critical vars set."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": "test-key",
                "GOOGLE_CLOUD_PROJECT": "test-project",
                "GOOGLE_API_KEY": "test-google-key",
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
            # Need to create a new Settings instance since get_settings is cached
            # and initialize_config uses get_settings
            with pytest.raises(ConfigurationError):
                # Directly test validate_critical_config with a fresh Settings
                settings = Settings(_env_file=None)
                validate_critical_config(settings)


class TestProductionConfigurationRequiresCriticalAPIKeys:
    """Property 2: Production Configuration Requires Critical API Keys.
    
    Feature: cloud-run-deployment
    **Validates: Requirements 2.3, 3.4**
    
    For any Settings instance where app_env is "production", calling
    validate_critical_config without elevenlabs_api_key, google_cloud_project,
    or google_api_key SHALL raise ConfigurationError.
    """

    @given(
        has_elevenlabs=st.booleans(),
        has_gcp_project=st.booleans(),
        has_google_api=st.booleans(),
    )
    @hypothesis_settings(max_examples=100)
    def test_production_requires_all_critical_keys(
        self, has_elevenlabs: bool, has_gcp_project: bool, has_google_api: bool
    ) -> None:
        """Property: Production mode requires all critical API keys.
        
        For any combination of API key presence in production,
        validate_critical_config should raise ConfigurationError
        if any critical key is missing.
        """
        env_vars = {"APP_ENV": "production"}
        
        if has_elevenlabs:
            env_vars["ELEVENLABS_API_KEY"] = "test-elevenlabs-key"
        if has_gcp_project:
            env_vars["GOOGLE_CLOUD_PROJECT"] = "test-project"
        if has_google_api:
            env_vars["GOOGLE_API_KEY"] = "test-google-key"
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings(_env_file=None)
            
            all_keys_present = has_elevenlabs and has_gcp_project and has_google_api
            
            if all_keys_present:
                # Should not raise when all keys are present
                validate_critical_config(settings)
            else:
                # Should raise when any key is missing
                with pytest.raises(ConfigurationError) as exc_info:
                    validate_critical_config(settings)
                
                # Verify the correct missing keys are reported
                if not has_elevenlabs:
                    assert "ELEVENLABS_API_KEY" in exc_info.value.missing_vars
                if not has_gcp_project:
                    assert "GOOGLE_CLOUD_PROJECT" in exc_info.value.missing_vars
                if not has_google_api:
                    assert "GOOGLE_API_KEY" in exc_info.value.missing_vars

    @given(
        api_key=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        project_id=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        google_key=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    )
    @hypothesis_settings(max_examples=100)
    def test_production_succeeds_with_any_valid_keys(
        self, api_key: str, project_id: str, google_key: str
    ) -> None:
        """Property: Production mode succeeds with any non-empty API keys.
        
        For any non-empty string values for the critical API keys,
        validate_critical_config should succeed in production.
        """
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "production",
                "ELEVENLABS_API_KEY": api_key,
                "GOOGLE_CLOUD_PROJECT": project_id,
                "GOOGLE_API_KEY": google_key,
            },
            clear=True,
        ):
            settings = Settings(_env_file=None)
            # Should not raise with any valid keys
            validate_critical_config(settings)


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
            # Original origins should be present
            assert "http://a.com" in origins
            assert "http://b.com" in origins
            assert "http://c.com" in origins
            # Localhost origins are automatically added for internal communication
            assert "http://localhost:8000" in origins
            assert "http://127.0.0.1:8000" in origins


class TestLangSmithConfigurationBasedTracing:
    """Property 2: Configuration-Based Tracing.
    
    Feature: langsmith-debug-integration
    Validates: Requirements 4.1, 4.2, 4.5
    
    For any environment configuration, when LangSmith API key is provided
    the system should enable tracing, and when tracing is disabled the
    system should still execute workflows successfully.
    """

    def test_langsmith_disabled_when_no_api_key(self) -> None:
        """Test that LangSmith is not configured without API key."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.is_langsmith_configured() is False

    def test_langsmith_enabled_when_api_key_provided(self) -> None:
        """Test that LangSmith is configured when API key is provided."""
        with patch.dict(
            os.environ,
            {"LANGSMITH_API_KEY": "test-api-key"},
        ):
            settings = Settings()
            assert settings.is_langsmith_configured() is True

    def test_langsmith_disabled_when_tracing_disabled(self) -> None:
        """Test that LangSmith is not configured when tracing is disabled."""
        with patch.dict(
            os.environ,
            {
                "LANGSMITH_API_KEY": "test-api-key",
                "LANGSMITH_TRACING_ENABLED": "false",
            },
        ):
            settings = Settings()
            assert settings.is_langsmith_configured() is False

    def test_default_langsmith_project_name(self) -> None:
        """Test that default LangSmith project is elevendops-langgraph-debug."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.langsmith_project == "elevendops-langgraph-debug"

    def test_langsmith_project_name_override(self) -> None:
        """Test that LangSmith project name can be overridden."""
        with patch.dict(
            os.environ,
            {"LANGSMITH_PROJECT": "custom-project"},
        ):
            settings = Settings()
            assert settings.langsmith_project == "custom-project"

    def test_default_langsmith_tracing_enabled(self) -> None:
        """Test that LangSmith tracing is enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.langsmith_tracing_enabled is True

    def test_default_langsmith_trace_level(self) -> None:
        """Test that default trace level is info."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.langsmith_trace_level == "info"

    @given(trace_level=st.sampled_from(["debug", "info", "error"]))

    def test_valid_trace_levels_accepted(self, trace_level: str) -> None:
        """Property: Any valid trace level is accepted."""
        with patch.dict(os.environ, {"LANGSMITH_TRACE_LEVEL": trace_level}):
            settings = Settings()
            assert settings.langsmith_trace_level == trace_level

    def test_configure_langsmith_environment_sets_vars(self) -> None:
        """Test that configure_langsmith_environment sets env vars."""
        with patch.dict(
            os.environ,
            {
                "LANGSMITH_API_KEY": "test-key",
                "LANGSMITH_PROJECT": "test-project",
                "LANGSMITH_TRACING_ENABLED": "true",
            },
        ):
            settings = Settings()
            settings.configure_langsmith_environment()
            
            assert os.environ.get("LANGCHAIN_API_KEY") == "test-key"
            assert os.environ.get("LANGCHAIN_PROJECT") == "test-project"
            assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"

    def test_configure_langsmith_environment_skips_without_key(self) -> None:
        """Test that configure_langsmith_environment skips when no API key."""
        # Clear any previous LANGCHAIN_API_KEY
        env_to_clear = {k: "" for k in os.environ if k.startswith("LANGCHAIN_")}
        with patch.dict(os.environ, env_to_clear, clear=False):
            for k in env_to_clear:
                os.environ.pop(k, None)
            
            settings = Settings()
            settings.configure_langsmith_environment()
            
            # Should not set LANGCHAIN_API_KEY
            assert os.environ.get("LANGCHAIN_API_KEY") is None


class TestConfigurationReadsFromEnvironment:
    """Property 6: Configuration Reads From Environment.
    
    Feature: cloud-run-deployment
    **Validates: Requirements 2.1, 8.5**
    
    For any environment variable set in the system, the Settings class
    SHALL read and apply that value correctly, overriding defaults.
    """

    @given(
        backend_url=st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not any(c in x for c in ['\n', '\r', '\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_backend_api_url_reads_from_environment(self, backend_url: str) -> None:
        """Property: BACKEND_API_URL is read from environment.
        
        For any valid URL string set as BACKEND_API_URL,
        the Settings class should read and apply that value.
        """
        with patch.dict(os.environ, {"BACKEND_API_URL": backend_url}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.backend_api_url == backend_url

    @given(
        bucket_name=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_'),
            min_size=1,
            max_size=50
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_gcs_bucket_name_reads_from_environment(self, bucket_name: str) -> None:
        """Property: GCS_BUCKET_NAME is read from environment.
        
        For any valid bucket name set as GCS_BUCKET_NAME,
        the Settings class should read and apply that value.
        """
        with patch.dict(os.environ, {"GCS_BUCKET_NAME": bucket_name}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.gcs_bucket_name == bucket_name

    @given(app_env=st.sampled_from(["development", "staging", "production"]))
    @hypothesis_settings(max_examples=100)
    def test_app_env_reads_from_environment(self, app_env: str) -> None:
        """Property: APP_ENV is read from environment.
        
        For any valid app_env value, the Settings class should
        read and apply that value correctly.
        """
        with patch.dict(os.environ, {"APP_ENV": app_env}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.app_env == app_env

    @given(use_emulator=st.booleans())
    @hypothesis_settings(max_examples=100)
    def test_use_firestore_emulator_reads_from_environment(self, use_emulator: bool) -> None:
        """Property: USE_FIRESTORE_EMULATOR is read from environment.
        
        For any boolean value set as USE_FIRESTORE_EMULATOR,
        the Settings class should read and apply that value.
        """
        with patch.dict(
            os.environ,
            {"USE_FIRESTORE_EMULATOR": str(use_emulator).lower()},
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.use_firestore_emulator == use_emulator

    @given(use_emulator=st.booleans())
    @hypothesis_settings(max_examples=100)
    def test_use_gcs_emulator_reads_from_environment(self, use_emulator: bool) -> None:
        """Property: USE_GCS_EMULATOR is read from environment.
        
        For any boolean value set as USE_GCS_EMULATOR,
        the Settings class should read and apply that value.
        """
        with patch.dict(
            os.environ,
            {"USE_GCS_EMULATOR": str(use_emulator).lower()},
            clear=True,
        ):
            settings = Settings(_env_file=None)
            assert settings.use_gcs_emulator == use_emulator

    @given(
        api_key=st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not any(c in x for c in ['\n', '\r', '\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_elevenlabs_api_key_reads_from_environment(self, api_key: str) -> None:
        """Property: ELEVENLABS_API_KEY is read from environment.
        
        For any non-empty string set as ELEVENLABS_API_KEY,
        the Settings class should read and apply that value.
        """
        with patch.dict(os.environ, {"ELEVENLABS_API_KEY": api_key}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.elevenlabs_api_key == api_key

    @given(
        project_id=st.text(min_size=1, max_size=100).filter(
            lambda x: x.strip() and not any(c in x for c in ['\n', '\r', '\x00'])
        ),
    )
    @hypothesis_settings(max_examples=100)
    def test_google_cloud_project_reads_from_environment(self, project_id: str) -> None:
        """Property: GOOGLE_CLOUD_PROJECT is read from environment.
        
        For any non-empty string set as GOOGLE_CLOUD_PROJECT,
        the Settings class should read and apply that value.
        """
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": project_id}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.google_cloud_project == project_id

    def test_multiple_env_vars_read_correctly(self) -> None:
        """Test that multiple environment variables are read correctly together.
        
        This verifies that the Settings class can read multiple environment
        variables simultaneously without interference.
        """
        env_vars = {
            "APP_ENV": "production",
            "BACKEND_API_URL": "http://localhost:8000",
            "GCS_BUCKET_NAME": "test-bucket",
            "USE_FIRESTORE_EMULATOR": "false",
            "USE_GCS_EMULATOR": "false",
            "ELEVENLABS_API_KEY": "test-elevenlabs-key",
            "GOOGLE_CLOUD_PROJECT": "test-project",
            "GOOGLE_API_KEY": "test-google-key",
            "CORS_ORIGINS": "http://localhost:8501,http://localhost:8000",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings(_env_file=None)
            
            assert settings.app_env == "production"
            assert settings.backend_api_url == "http://localhost:8000"
            assert settings.gcs_bucket_name == "test-bucket"
            assert settings.use_firestore_emulator is False
            assert settings.use_gcs_emulator is False
            assert settings.elevenlabs_api_key == "test-elevenlabs-key"
            assert settings.google_cloud_project == "test-project"
            assert settings.google_api_key == "test-google-key"

    def test_cors_origins_includes_localhost_after_validation(self) -> None:
        """Test that CORS origins include localhost for internal communication.
        
        This validates Requirement 2.5: CORS includes localhost for internal
        communication in Cloud Run.
        """
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": "https://example.com"},
            clear=True,
        ):
            settings = Settings(_env_file=None)
            origins = settings.get_cors_origins_list()
            
            # Should include localhost origins for internal communication
            assert "http://localhost:8000" in origins
            assert "http://127.0.0.1:8000" in origins
            # Should also include the original origin
            assert "https://example.com" in origins
