import os
import sys
from pathlib import Path
from google.cloud import storage
from datetime import timedelta
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env")

def test_minimal_signing():
    print("Testing minimal GCS signing...")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    bucket_name = "elevendops-bucket"
    blob_name = "audio/1b04bbbb-43eb-45ae-98b2-e99c02134c83.mp3"
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        print(f"Attempting to sign: gs://{bucket_name}/{blob_name}")
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET"
        )
        print("\n[SUCCESS] Signed URL generated:")
        print(url)
        
        if "Signature=" in url or "X-Goog-Signature=" in url:
            print("\n[OK] Signature found in URL!")
        else:
            print("\n[FAIL] No signature found in URL. It might be a public URL.")
            
    except Exception as e:
        print(f"\n[ERROR] Signing failed: {e}")

if __name__ == "__main__":
    test_minimal_signing()
