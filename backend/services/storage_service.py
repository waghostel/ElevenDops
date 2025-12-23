import logging
import os
import shutil
from pathlib import Path
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
        self._blob_public_base_url = None
        
        try:
            if settings.use_mock_storage:
                logger.info("Using Local Mock Storage (file system)")
                self._mock_storage_dir = Path("temp_storage") / self._bucket_name
                self._mock_storage_dir.mkdir(parents=True, exist_ok=True)
                # For mock storage, we'll construct a simple file URL or local path
                # Ideally, we should serve these files via FastAPI StaticFiles for frontend access
                # For now, we'll assume a specific route /api/storage/{filename} or similar will be added,
                # Or just return a file:// URI which won't work in browser but works for logic.
                # BETTER: Let's assume the frontend will request via a backend proxy endpoint we haven't built yet,
                # OR we just return a placeholder URL for display.
                self._blob_public_base_url = f"http://localhost:{settings.fastapi_port}/api/storage/files"
                logger.info(f"Mock storage directory: {self._mock_storage_dir.absolute()}")
                
            elif settings.use_gcs_emulator:
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
            
            if not settings.use_mock_storage:
                self._ensure_bucket_exists()
                
            logger.info("Storage client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Storage client: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist (for emulator)."""
        settings = get_settings()
        
        # Skip for mock storage
        if settings.use_mock_storage:
            return

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
        
        if settings.use_mock_storage:
            # Save to local filesystem
            # Handle subdirectories in filename
            file_path = self._mock_storage_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(data)
                
            logger.info(f"Saved mock file: {file_path}")
            # Return a constructed URL
            # Note: filename might contain "/", so we'll need to handle that in the route later if we build it
            return f"{self._blob_public_base_url}/{filename}"
        
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
        settings = get_settings()
        
        if settings.use_mock_storage:
            file_path = self._mock_storage_dir / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Deleted mock file: {file_path}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to delete mock file {file_path}: {e}")
                    return False
            return False

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
        settings = get_settings()
        
        if settings.use_mock_storage:
             file_path = self._mock_storage_dir / filename
             return file_path.exists()

        try:
            blob = self._bucket.blob(filename)
            return blob.exists()
        except Exception as e:
            logger.error(f"Failed to check file existence {filename}: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if storage is accessible."""
        settings = get_settings()
        
        if settings.use_mock_storage:
            # Just check if directory is writable
            return self._mock_storage_dir.exists() and os.access(self._mock_storage_dir, os.W_OK)

        try:
            list(self._client.list_buckets(max_results=1))
            return True
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False


def get_storage_service() -> StorageService:
    """Get the Storage service instance."""
    return StorageService()
