import logging
import os
import shutil
from datetime import timedelta
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
        """Create bucket if it doesn't exist (for emulator) or use lazy reference (for real GCS)."""
        settings = get_settings()
        
        # Skip for mock storage
        if settings.use_mock_storage:
            return

        # For Real GCS: Use a lazy reference to avoid 'storage.buckets.get' permission requirement
        # This is the standard best practice when using 'Storage Object Admin' roles
        if not settings.use_gcs_emulator:
            self._bucket = self._client.bucket(self._bucket_name)
            logger.info(f"Using GCS bucket reference: '{self._bucket_name}'")
            return

        # For Emulator: Perform existence check and creation
        try:
            self._bucket = self._client.get_bucket(self._bucket_name)
            logger.info(f"Bucket '{self._bucket_name}' exists in emulator")
        except Exception:
            logger.info(f"Creating bucket '{self._bucket_name}' in emulator")
            self._bucket = self._client.create_bucket(self._bucket_name)
    
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
        """Upload audio file and return storage path or URL.
        
        For production GCS, returns the storage path (e.g., 'audio/uuid.mp3')
        which should be signed on retrieval.
        For emulator/mock, returns a direct URL for convenience.
        
        Args:
            audio_data: Audio file bytes.
            filename: Filename (without subdirectory prefix).
            
        Returns:
            Storage path (production) or direct URL (emulator/mock).
        """
        settings = get_settings()
        storage_path = f"audio/{filename}"
        
        # Upload the file
        result_url = self.upload_file(audio_data, storage_path, content_type="audio/mpeg")
        
        # For production, return just the storage path (to be signed later)
        # For emulator/mock, return the direct URL for immediate access
        if not settings.use_gcs_emulator and not settings.use_mock_storage:
            return storage_path
        return result_url
    
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

    def get_file_stream(self, storage_path: str):
        """Get a stream of the file content.
        
        Args:
            storage_path: Path to the file in storage.
            
        Yields:
            Bytes chunks of the file content.
        """
        settings = get_settings()
        
        # Handle full URL input by extracting path
        if storage_path.startswith("https://storage.googleapis.com/"):
            parts = storage_path.split("/")
            if len(parts) > 4:
                storage_path = "/".join(parts[4:])
        
        if settings.use_mock_storage:
            file_path = self._mock_storage_dir / storage_path
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk
                    
        elif settings.use_gcs_emulator:
            # For emulator, we can just download as bytes (it's local anyway)
            # or try to stream if client supports it. 
            # Simple approach: download to memory (emulator is for dev/test)
            blob = self._bucket.blob(storage_path)
            yield blob.download_as_bytes()
            
        else:
            # Production GCS: Stream download
            blob = self._bucket.blob(storage_path)
            try:
                with blob.open("rb") as f:
                    while chunk := f.read(8192):
                        yield chunk
            except Exception as e:
                logger.error(f"Error streaming file {storage_path}: {e}")
                raise


def get_storage_service() -> StorageService:
    """Get the Storage service instance."""
    return StorageService()


# Default expiration for signed URLs (1 hour)
DEFAULT_SIGNED_URL_EXPIRATION_SECONDS = 3600


def get_signed_url(
    storage_path: str, 
    expiration_seconds: int = DEFAULT_SIGNED_URL_EXPIRATION_SECONDS
) -> str:
    """Generate a signed URL for temporary access to a GCS object.
    
    This function generates time-limited URLs that provide secure access
    to private bucket objects without requiring public bucket access.
    
    Args:
        storage_path: The storage path (e.g., 'audio/uuid.mp3').
        expiration_seconds: URL validity duration in seconds (default: 1 hour).
        
    Returns:
        A signed URL for production GCS, or direct URL for emulator/mock.
        If the path is already a full URL (http/https), returns it unchanged.
    """
    settings = get_settings()
    
    # If it's a full GCS public URL, extract the path and sign it
    # This handles legacy data where audio_url was stored as a public URL
    if storage_path.startswith("https://storage.googleapis.com/"):
        # Format: https://storage.googleapis.com/BUCKET_NAME/PATH/TO/FILE
        # Splitting by / gives: ["https:", "", "storage.googleapis.com", "BUCKET_NAME", "PATH", "TO", "FILE"]
        parts = storage_path.split("/")
        if len(parts) > 4:
             # Reconstruct the path after the bucket name
            storage_path = "/".join(parts[4:])
            logger.info(f"Extracted path from full URL: {storage_path}")

    # If it's some other external URL, return as-is
    elif storage_path.startswith("http://") or storage_path.startswith("https://"):
        return storage_path
    
    service = get_storage_service()
    
    # Mock storage: return backend proxy URL
    if settings.use_mock_storage:
        return f"{service._blob_public_base_url}/{storage_path}"
    
    # Emulator: return direct emulator URL (no signing needed)
    if settings.use_gcs_emulator:
        encoded_path = storage_path.replace("/", "%2F")
        return f"{settings.gcs_emulator_host}/storage/v1/b/{service._bucket_name}/o/{encoded_path}?alt=media"
    
    # Production: generate signed URL
    try:
        blob = service._bucket.blob(storage_path)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=expiration_seconds),
            method="GET",
        )
        logger.info(f"Generated signed URL for {storage_path} (expires in {expiration_seconds}s)")
        return signed_url
    except Exception as e:
        logger.error(f"Failed to generate signed URL for {storage_path}: {e}")
        # Fallback to public URL (will fail if bucket is private, but logs the error)
        return f"https://storage.googleapis.com/{service._bucket_name}/{storage_path}"
