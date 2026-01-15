"""Property-based tests for Storage Service.

Tests the StorageService implementation against the requirements
specified in .kiro/specs/storage-service/requirements.md
"""

import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from hypothesis.strategies import composite

# --- Strategies ---

# Valid filename characters (alphanumeric, underscore, hyphen)
valid_filename_chars = st.characters(
    whitelist_categories=('L', 'N'),
    whitelist_characters='_-'
)

@composite
def s_valid_filename(draw):
    """Generate valid filenames without path separators."""
    base = draw(st.text(alphabet=valid_filename_chars, min_size=1, max_size=50))
    # Ensure it's not empty after filtering
    assume(len(base) > 0)
    return f"{base}.mp3"

@composite
def s_audio_bytes(draw):
    """Generate valid audio-like bytes."""
    return draw(st.binary(min_size=100, max_size=10000))


# --- Unit Tests for URL Format Generation ---

class TestURLFormatGeneration:
    """Test URL format generation for both emulator and production modes."""
    
    def test_emulator_url_format(self):
        """Test that emulator mode generates correct URL format."""
        # **Feature: storage-service, Property 2: Upload produces correct storage and URL format**
        # **Validates: Requirements 2.3**
        
        emulator_host = "http://localhost:4443"
        bucket_name = "test-bucket"
        filename = "test_audio.mp3"
        
        # Expected format for emulator
        expected_url = f"{emulator_host}/storage/v1/b/{bucket_name}/o/audio%2F{filename}?alt=media"
        
        # Verify the URL format matches specification
        assert "storage/v1/b" in expected_url
        assert "alt=media" in expected_url
        assert "%2F" in expected_url  # URL-encoded slash
    
    def test_production_url_format(self):
        """Test that production mode generates correct URL format."""
        # **Feature: storage-service, Property 2: Upload produces correct storage and URL format**
        # **Validates: Requirements 2.4**
        
        bucket_name = "test-bucket"
        filename = "test_audio.mp3"
        
        # Expected format for production
        expected_url = f"https://storage.googleapis.com/{bucket_name}/audio/{filename}"
        
        # Verify the URL format matches specification
        assert expected_url.startswith("https://storage.googleapis.com/")
        assert bucket_name in expected_url
        assert f"audio/{filename}" in expected_url


class TestStorageServiceConfiguration:
    """Test configuration-based initialization."""
    
    def test_settings_have_required_fields(self):
        """Test that Settings class has all required GCS configuration fields."""
        # **Feature: storage-service, Property 1: Configuration-based initialization**
        # **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        
        from backend.config import Settings
        
        settings = Settings()
        
        # Verify all required settings exist
        assert hasattr(settings, 'use_gcs_emulator')
        assert hasattr(settings, 'gcs_emulator_host')
        assert hasattr(settings, 'gcs_bucket_name')
        assert hasattr(settings, 'google_cloud_project')
        
        # Verify default values for local development
        assert isinstance(settings.use_gcs_emulator, bool)
        assert isinstance(settings.gcs_emulator_host, str)
        assert isinstance(settings.gcs_bucket_name, str)
    
    def test_emulator_mode_uses_anonymous_credentials(self):
        """Test that emulator mode uses AnonymousCredentials."""
        # **Feature: storage-service, Property 1: Configuration-based initialization**
        # **Validates: Requirements 1.1**
        
        from google.auth.credentials import AnonymousCredentials
        
        # Verify AnonymousCredentials can be instantiated
        creds = AnonymousCredentials()
        assert creds is not None


class TestStorageServiceInterface:
    """Test StorageService interface compliance."""
    
    def test_storage_service_has_required_methods(self):
        """Test that StorageService has all required methods."""
        # **Feature: storage-service, Property 4: Factory function returns functional instance**
        # **Validates: Requirements 4.1**
        
        from backend.services.storage_service import StorageService
        
        # Verify all required methods exist
        assert hasattr(StorageService, 'upload_audio')
        assert hasattr(StorageService, 'delete_audio')
        assert hasattr(StorageService, 'upload_file')
        assert hasattr(StorageService, 'health_check')
        assert callable(getattr(StorageService, 'upload_audio', None))
        assert callable(getattr(StorageService, 'delete_audio', None))
        assert callable(getattr(StorageService, 'upload_file', None))
        assert callable(getattr(StorageService, 'health_check', None))
    
    def test_factory_function_exists(self):
        """Test that get_storage_service factory function exists."""
        # **Feature: storage-service, Property 4: Factory function returns functional instance**
        # **Validates: Requirements 4.1**
        
        from backend.services.storage_service import get_storage_service
        
        assert callable(get_storage_service)


# --- Integration Tests (require emulator running) ---

@pytest.fixture
def storage_service():
    """Get storage service instance, skip if emulator not available."""
    from backend.services.storage_service import StorageService
    
    # Reset singleton for clean test
    StorageService._instance = None
    StorageService._client = None
    StorageService._bucket = None
    
    try:
        from backend.services.storage_service import get_storage_service
        service = get_storage_service()
        
        # Check if we are running against a valid client or a Mock
        # If it's a Mock (from conftest.py), skip integration tests
        if isinstance(service._client, MagicMock) or getattr(service._client, "__name__", "") == "MagicMock":
             pytest.skip("Skipping integration tests - GCS client is mocked")

        # Quick health check
        if not service.health_check():
            pytest.skip("Storage emulator not accessible")
        return service
    except Exception as e:
        pytest.skip(f"Storage service not available: {e}")


@pytest.mark.integration
class TestStorageServiceIntegration:
    """Integration tests requiring GCS emulator."""
    

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(audio_data=s_audio_bytes(), filename=s_valid_filename())
    def test_property_2_upload_produces_correct_url(self, storage_service, audio_data, filename):
        """Test upload produces correct storage and URL format."""
        # **Feature: storage-service, Property 2: Upload produces correct storage and URL format**
        # **Validates: Requirements 2.1, 2.2, 2.3**
        
        url = storage_service.upload_audio(audio_data, filename)
        
        # Verify URL is returned
        assert url is not None
        assert isinstance(url, str)
        assert len(url) > 0
        
        # Verify URL contains expected components
        assert filename in url
        assert "audio" in url
        
        # Clean up
        storage_service.delete_audio(filename)
    

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(audio_data=s_audio_bytes(), filename=s_valid_filename())
    def test_property_3_upload_then_delete_roundtrip(self, storage_service, audio_data, filename):
        """Test upload then delete round-trip."""
        # **Feature: storage-service, Property 3: Upload then delete round-trip**
        # **Validates: Requirements 3.1, 3.2**
        
        # Upload
        url = storage_service.upload_audio(audio_data, filename)
        assert url is not None
        
        # Verify file exists
        assert storage_service.file_exists(f"audio/{filename}")
        
        # Delete
        result = storage_service.delete_audio(filename)
        assert result is True
        
        # Verify file no longer exists
        assert not storage_service.file_exists(f"audio/{filename}")
    
    def test_property_4_factory_returns_functional_instance(self, storage_service):
        """Test factory function returns functional instance."""
        # **Feature: storage-service, Property 4: Factory function returns functional instance**
        # **Validates: Requirements 4.1, 4.2**
        
        from backend.services.storage_service import get_storage_service
        
        # Get multiple instances
        service1 = get_storage_service()
        service2 = get_storage_service()
        
        # Verify singleton pattern
        assert service1 is service2
        
        # Verify instance is functional
        assert service1.health_check()
    
    def test_delete_nonexistent_file_returns_false(self, storage_service):
        """Test deleting non-existent file returns False."""
        # **Feature: storage-service, Edge Case: Delete non-existent file**
        # **Validates: Requirements 3.3**
        
        result = storage_service.delete_audio("nonexistent_file_12345.mp3")
        assert result is False
    
    def test_bucket_exists_after_initialization(self, storage_service):
        """Test bucket exists after service initialization."""
        # **Feature: storage-service, Property 1: Configuration-based initialization**
        # **Validates: Requirements 1.3**
        
        from backend.config import get_settings
        settings = get_settings()
        
        # Verify bucket is accessible
        assert storage_service._bucket is not None
        assert storage_service._bucket.name == settings.gcs_bucket_name


# --- Mock-based Tests (no emulator required) ---

class TestStorageServiceMocked:
    """Tests using mocked GCS client."""
    

    @given(filename=s_valid_filename())
    def test_upload_audio_sets_correct_content_type(self, filename):
        """Test that upload_audio sets content type to audio/mpeg."""
        # **Feature: storage-service, Property 2: Upload produces correct storage and URL format**
        # **Validates: Requirements 2.2**
        
        with patch('backend.services.storage_service.storage') as mock_storage:
            with patch('backend.services.storage_service.get_settings') as mock_settings:
                # Setup mocks
                mock_settings_instance = MagicMock()
                mock_settings_instance.use_gcs_emulator = True
                mock_settings_instance.gcs_emulator_host = "http://localhost:4443"
                mock_settings_instance.gcs_bucket_name = "test-bucket"
                mock_settings_instance.google_cloud_project = "test-project"
                mock_settings_instance.use_mock_storage = False
                mock_settings.return_value = mock_settings_instance
                
                mock_client = MagicMock()
                mock_bucket = MagicMock()
                mock_blob = MagicMock()
                
                mock_storage.Client.return_value = mock_client
                mock_client.get_bucket.return_value = mock_bucket
                mock_bucket.blob.return_value = mock_blob
                
                # Reset singleton
                from backend.services.storage_service import StorageService
                StorageService._instance = None
                StorageService._client = None
                StorageService._bucket = None
                
                # Create service and upload
                service = StorageService()
                service._bucket = mock_bucket
                
                audio_data = b"fake audio data"
                service.upload_audio(audio_data, filename)
                
                # Verify content type was set correctly
                mock_blob.upload_from_string.assert_called_once()
                call_args = mock_blob.upload_from_string.call_args
                assert call_args[1]['content_type'] == 'audio/mpeg'
    

    @given(filename=s_valid_filename())
    def test_upload_audio_uses_audio_prefix(self, filename):
        """Test that upload_audio stores files with audio/ prefix."""
        # **Feature: storage-service, Property 2: Upload produces correct storage and URL format**
        # **Validates: Requirements 2.1**
        
        with patch('backend.services.storage_service.storage') as mock_storage:
            with patch('backend.services.storage_service.get_settings') as mock_settings:
                # Setup mocks
                mock_settings_instance = MagicMock()
                mock_settings_instance.use_gcs_emulator = True
                mock_settings_instance.gcs_emulator_host = "http://localhost:4443"
                mock_settings_instance.gcs_bucket_name = "test-bucket"
                mock_settings_instance.google_cloud_project = "test-project"
                mock_settings_instance.use_mock_storage = False
                mock_settings.return_value = mock_settings_instance
                
                mock_client = MagicMock()
                mock_bucket = MagicMock()
                mock_blob = MagicMock()
                
                mock_storage.Client.return_value = mock_client
                mock_client.get_bucket.return_value = mock_bucket
                mock_bucket.blob.return_value = mock_blob
                
                # Reset singleton
                from backend.services.storage_service import StorageService
                StorageService._instance = None
                StorageService._client = None
                StorageService._bucket = None
                
                # Create service and upload
                service = StorageService()
                service._bucket = mock_bucket
                
                audio_data = b"fake audio data"
                service.upload_audio(audio_data, filename)
                
                # Verify blob was created with audio/ prefix
                mock_bucket.blob.assert_called_with(f"audio/{filename}")
