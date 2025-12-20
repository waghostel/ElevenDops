import logging
from google.cloud import storage
from google.auth.credentials import AnonymousCredentials
from backend.config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """GCS client that works with both fake-gcs-server and production."""
    
    _instance = None
    _client = None
    _bucket = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is not None:
            return
            
        settings = get_settings()
        self._bucket_name = settings.gcs_bucket_name
        
        try:
            if settings.use_gcs_emulator:
                logger.info(f"Connecting to GCS Emulator at {settings.gcs_emulator_host}")
                self._client = storage.Client(
                    credentials=AnonymousCredentials(),
                    project=settings.google_cloud_project or "elevenlabs-local",
                )
                # Override the API endpoint for emulator
                self._client._http._base_url = settings.gcs_emulator_host
            else:
                logger.info("Connecting to production GCS")
                if settings.google_cloud_project:
                    self._client = storage.Client(project=settings.google_cloud_project)
                else:
                    self._client = storage.Client()
            
            self._ensure_bucket_exists()
            logger.info("Storage client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Storage client: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist (for emulator)."""
        settings = get_settings()
        try:
            self._bucket = self._client.get_bucket(self._bucket_name)
            logger.info(f"Bucket '{self._bucket_name}' exists")
        except Exception:
            if settings.use_gcs_emulator:
                logger.info(f"Creating bucket '{self._bucket_name}' in emulator")
                self._bucket = self._client.create_bucket(self._bucket_name)
            else:
                raise
    
    def upload_file(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
        """Upload file and return public URL."""
        settings = get_settings()
        
        blob = self._bucket.blob(filename)
        blob.upload_from_string(data, content_type=content_type)
        
        # Generate URL based on environment
        if settings.use_gcs_emulator:
            # URL format for fake-gcs-server
            encoded_filename = filename.replace("/", "%2F")
            return f"{settings.gcs_emulator_host}/storage/v1/b/{self._bucket_name}/o/{encoded_filename}?alt=media"
        else:
            # Production GCS URL
            return f"https://storage.googleapis.com/{self._bucket_name}/{filename}"
    
    def upload_audio(self, audio_data: bytes, filename: str) -> str:
        """Upload audio file and return URL."""
        return self.upload_file(audio_data, f"audio/{filename}", content_type="audio/mpeg")
    
    def delete_file(self, filename: str) -> bool:
        """Delete a file from storage."""
        try:
            blob = self._bucket.blob(filename)
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False
    
    def delete_audio(self, filename: str) -> bool:
        """Delete audio file from storage.
        
        Args:
            filename: Filename to delete (without path prefix)
            
        Returns:
            True if deletion succeeded, False if file not found or error
        """
        return self.delete_file(f"audio/{filename}")
    
    def file_exists(self, filename: str) -> bool:
        """Check if a file exists in storage."""
        try:
            blob = self._bucket.blob(filename)
            return blob.exists()
        except Exception as e:
            logger.error(f"Failed to check file existence {filename}: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if storage is accessible."""
        try:
            list(self._client.list_buckets(max_results=1))
            return True
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False


def get_storage_service() -> StorageService:
    """Get the Storage service instance."""
    return StorageService()
