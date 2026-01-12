
import asyncio
import logging
import os
import sys
from collections import Counter

# Add project root to path
sys.path.append(os.getcwd())

from backend.config import get_settings
from backend.services.storage_service import get_storage_service
from backend.services.firestore_service import get_firestore_service
from backend.services.firestore_data_service import FirestoreDataService

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def main():
    print("DIAGNOSTIC: Checking Audio Sync Status...")
    settings = get_settings()
    
    print(f"Configuration:")
    print(f"   Project: {settings.google_cloud_project}")
    print(f"   Bucket: {settings.gcs_bucket_name}")
    print(f"   Firestore DB: {settings.firestore_database_id}")
    print(f"   Use GCS Emulator: {settings.use_gcs_emulator}")
    print(f"   Use Firestore Emulator: {settings.use_firestore_emulator}")
    
    # 1. Check GCS
    print("\n[GCS] Checking Google Cloud Storage...")
    storage = get_storage_service()
    
    try:
        blobs = list(storage._bucket.list_blobs(prefix="audio/"))
        gcs_files = [b.name.replace("audio/", "") for b in blobs if not b.name.endswith("/")]
        print(f"   [OK] Found {len(gcs_files)} audio files in GCS.")
        if len(gcs_files) > 0:
            print(f"   Sample: {gcs_files[:3]}")
    except Exception as e:
        print(f"   [ER] Error checking GCS: {e}")
        return

    # 2. Check Firestore
    print("\n[FS] Checking Firestore...")
    firestore_service = FirestoreDataService()
    try:
        # We need to access the collection directly to avoid model conversion errors if schema changed
        docs = firestore_service._db.collection("audio_files").stream()
        firestore_ids = [d.id for d in docs]
        print(f"   [OK] Found {len(firestore_ids)} audio metadata records in Firestore.")
        if len(firestore_ids) > 0:
            print(f"   Sample: {firestore_ids[:3]}")
    except Exception as e:
        print(f"   [ER] Error checking Firestore: {e}")
        return

    # 3. Compare
    print("\n[CMP] Comparison:")
    
    gcs_set = set(gcs_files)
    fs_set = set([f"{id}.mp3" for id in firestore_ids]) # Assuming Firestore IDs match filenames sans extension
    
    # Let's normalize. 
    # GCS files: uuid.mp3
    # Firestore IDs: uuid
    
    gcs_ids = set([f.replace(".mp3", "") for f in gcs_files])
    fs_ids = set(firestore_ids)
    
    missing_in_fs = gcs_ids - fs_ids
    missing_in_gcs = fs_ids - gcs_ids
    
    if missing_in_fs:
        print(f"   [!!] {len(missing_in_fs)} files exist in GCS but MISSING from Firestore (Orphans).")
        print(f"   Sample Orphans: {list(missing_in_fs)[:5]}")
    else:
        print(f"   [OK] All GCS files have metadata.")
        
    if missing_in_gcs:
        print(f"   [!!] {len(missing_in_gcs)} records exist in Firestore but MISSING from GCS (Broken Links).")
    else:
        print(f"   [OK] All Firestore records have files.")
        
    if not missing_in_fs and not missing_in_gcs:
        print("\n[OK] Everything looks perfectly synced!")
    
    # 4. Check Filtering Logic (Doctor ID)
    if len(fs_ids) > 0:
        print("\n[Data] Analyzing Metadata Content...")
        doc_ids_tally = Counter()
        knowledge_ids_tally = Counter()
        
        docs = firestore_service._db.collection("audio_files").stream()
        for d in docs:
            data = d.to_dict()
            did = data.get('doctor_id', 'MISSING')
            kid = data.get('knowledge_id', 'MISSING')
            doc_ids_tally[did] += 1
            knowledge_ids_tally[kid] += 1
            
        print("   [ID] Doctor ID Distribution:")
        for did, count in doc_ids_tally.items():
            print(f"      - {did}: {count} files")
            
        print("   [ID] Knowledge ID Distribution (Top 5):")
        for kid, count in knowledge_ids_tally.most_common(5):
             print(f"      - {kid}: {count} files")
             
        # Check specific hardcoded ID
        target_id = "dr_demo_001"
        if target_id not in doc_ids_tally:
             print(f"\n   [!!] CRITICAL: No files found for app's default doctor ID '{target_id}'!")
        else:
             print(f"\n   [OK] Found {doc_ids_tally[target_id]} files for '{target_id}'.")

if __name__ == "__main__":
    asyncio.run(main())
