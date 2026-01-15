
import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from unittest.mock import MagicMock, patch

from backend.services.storage_service import StorageService

# Property 3: Storage upload returns valid URL
# Validates: Requirements 3.1, 3.2

@given(
    filename=st.text(min_size=1, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
    use_emulator=st.booleans()
)

def test_storage_upload_returns_valid_url(filename, use_emulator):
    with patch("backend.services.storage_service.get_settings") as mock_settings:
        # Mock settings
        mock_settings.return_value.use_gcs_emulator = use_emulator
        mock_settings.return_value.gcs_emulator_host = "http://localhost:9023"
        mock_settings.return_value.gcs_bucket_name = "test-bucket"
        mock_settings.return_value.google_cloud_project = "test-project"
        mock_settings.return_value.use_mock_storage = False

        # Mock storage client injection or initialization
        with patch("google.cloud.storage.Client"):
            service = StorageService()
            # Force re-init or handle singleton? 
            # StorageService is a singleton. We might need to reset it or mock __init__ logic if it's already initialized.
            # But the test creates a new one? No, __new__ implementation returns singleton.
            # We need to bypass singleton or reset it for property testing different configs.
            
            # Hack: clear singleton for testing
            StorageService._instance = None
            service = StorageService()
            service.settings = mock_settings.return_value
            
            # Mock bucket
            service._bucket = MagicMock()
            service._bucket.blob.return_value.upload_from_string = MagicMock()
            
            data = b"content"
            url = service.upload_audio(data, filename)
            
            assert isinstance(url, str)
            assert len(url) > 0
            
            if use_emulator:
                assert url.startswith("http://localhost:9023")
                assert "test-bucket" in url
            else:
                # Production returns the storage path, not the full URL (for signing later)
                assert url == f"audio/{filename}"
