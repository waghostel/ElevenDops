import os
import logging
from google.cloud import firestore
from backend.config import get_settings

logger = logging.getLogger(__name__)


class FirestoreService:
    """Firestore client that works with both emulator and production."""
    
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db is not None:
            return
            
        settings = get_settings()
        
        if settings.use_firestore_emulator:
            # Set emulator host before creating client
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host
            logger.info(f"Connecting to Firestore Emulator at {settings.firestore_emulator_host}")
        else:
            # Remove emulator host if set (for production)
            os.environ.pop("FIRESTORE_EMULATOR_HOST", None)
            logger.info("Connecting to production Firestore")
        
        try:
            # project argument is required, even for emulator
            project = settings.google_cloud_project or "elevenlabs-local"
            self._db = firestore.Client(project=project)
            logger.info(f"Firestore client initialized for project {project}")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise
    
    @property
    def db(self) -> firestore.Client:
        """Get the Firestore client instance."""
        return self._db
    
    def health_check(self) -> bool:
        """Check if Firestore is accessible."""
        try:
            # Try to access a collection (doesn't need to exist)
            # Use a short timeout if possible, but the python client might not expose it easily per request
            # limit(1).get() is a lightweight check
            self._db.collection("_health_check").limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return False


def get_firestore_service() -> FirestoreService:
    """Get the Firestore service instance."""
    return FirestoreService()
