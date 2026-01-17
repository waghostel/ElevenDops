
import os
import sys
import logging

import logging
from dotenv import load_dotenv

# Load env vars FIRST so Google Client can see them
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from backend.config import get_settings
from backend.services.storage_service import get_signed_url, get_storage_service

def verify_signed_url():
    print("--- Starting Signed URL Verification ---")
    settings = get_settings()
    
    print(f"USE_GCS_EMULATOR: {settings.use_gcs_emulator}")
    print(f"USE_MOCK_STORAGE: {settings.use_mock_storage}")
    print(f"GOOGLE_CLOUD_PROJECT: {settings.google_cloud_project}")
    print(f"GCS_BUCKET_NAME: {settings.gcs_bucket_name}")
    print(f"Credentials Path: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    if settings.use_gcs_emulator:
        print("\n[WARNING] Emulator is ENABLED. Signed URLs will NOT be generated (direct URLs used instead).")
        print("To test signed URLs, set USE_GCS_EMULATOR=false in .env")
        return
        
    try:
        # Initialize service (will verify credentials/bucket access)
        print("\nInitializing Storage Service...")
        service = get_storage_service()
        print("Storage Service Initialized.")
        
        # Generates a signed URL for a theoretical file
        test_path = "audio/verify_signed_url_test.mp3"
        print(f"\nGenerating signed URL for path: {test_path}")
        
        signed_url = get_signed_url(test_path)
        
        print(f"\nResulting URL:\n{signed_url}")
        
        if "Signature=" in signed_url and "GoogleAccessId=" in signed_url:
            print("\n[SUCCESS] Signed URL generated successfully containing Signature and AccessId.")
        elif "storage.googleapis.com" in signed_url:
             print("\n[WARNING] URL generated but missing Signature? Check output.")
        else:
             print("\n[ERROR] URL does not look like a GCS URL.")
             
    except Exception as e:
        print(f"\n[ERROR] Failed to verify: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_signed_url()
