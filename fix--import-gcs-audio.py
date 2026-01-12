
import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from backend.config import get_settings
from backend.services.storage_service import get_storage_service
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import AudioMetadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_DOCTOR_ID = "dr_demo_001"

async def main():
    print("🔧 FIX: Repairing Audio Metadata...")
    settings = get_settings()
    
    if settings.use_mock_storage:
        print("⚠️  Warning: Using mock storage.")
    
    storage = get_storage_service()
    firestore_service = FirestoreDataService()
    
    # 1. Get all GCS files
    print("☁️  Listing GCS files...")
    blobs = list(storage._bucket.list_blobs(prefix="audio/"))
    gcs_files = [b.name for b in blobs if not b.name.endswith("/")]
    print(f"   found {len(gcs_files)} files.")

    # 2. Get all Firestore records
    print("🔥 Listing Firestore records...")
    docs = list(firestore_service._db.collection("audio_files").stream())
    print(f"   found {len(docs)} records.")
    
    fs_paths = set()
    fs_ids = set()
    
    orphans = []
    wrong_owner = []
    
    # Analyze existing records
    for d in docs:
        data = d.to_dict()
        audio_id = d.id
        fs_ids.add(audio_id)
        fs_paths.add(data.get("audio_url", ""))
        
        # Check ownership
        current_owner = data.get("doctor_id")
        if current_owner == "default" or current_owner is None:
            wrong_owner.append({
                "id": audio_id,
                "current": current_owner,
                "data": data
            })

    # Identify Orphans (GCS files not in FS)
    for gcs_path in gcs_files:
        filename = os.path.basename(gcs_path)
        audio_id = os.path.splitext(filename)[0]
        
        if gcs_path not in fs_paths and audio_id not in fs_ids:
            orphans.append({
                "path": gcs_path,
                "id": audio_id
            })
            
    # Report Findings
    if not orphans and not wrong_owner:
        print("✅ No issues found. System is healthy.")
        return

    if wrong_owner:
        print(f"\n⚠️  Found {len(wrong_owner)} records with incorrect owner (e.g. 'default').")
        print(f"   Sample: {wrong_owner[0]['id']} owned by '{wrong_owner[0]['current']}'")
        
    if orphans:
        print(f"\n⚠️  Found {len(orphans)} orphaned files (in GCS but not in DB).")

    # Confirmation
    print(f"\nPlan:")
    if wrong_owner:
        print(f"   1. Transfer {len(wrong_owner)} records to '{TARGET_DOCTOR_ID}'")
    if orphans:
        print(f"   2. Import {len(orphans)} orphans to '{TARGET_DOCTOR_ID}'")
        
    confirm = input("\n❓ Execute repair? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Aborted.")
        return

    # Execute Repairs
    print("\n🚀 Executing...")
    
    # 1. Update Owners
    updated_count = 0
    if wrong_owner:
        batch = firestore_service._db.batch()
        for i, item in enumerate(wrong_owner):
            ref = firestore_service._db.collection("audio_files").document(item["id"])
            batch.update(ref, {"doctor_id": TARGET_DOCTOR_ID})
            updated_count += 1
            
            # Commit every 500 (Firestore limit)
            if (i + 1) % 400 == 0:
                batch.commit()
                batch = firestore_service._db.batch()
                print(f"   ...committed batch")
        
        if updated_count > 0:
            batch.commit()
            print(f"   ✅ Updated {updated_count} records to '{TARGET_DOCTOR_ID}'")

    # 2. Import Orphans
    imported_count = 0
    for item in orphans:
        audio_id = item["id"]
        path = item["path"]
        
        metadata = AudioMetadata(
            audio_id=audio_id,
            knowledge_id="imported_from_gcs", 
            voice_id="unknown_voice",
            script="[Imported from GCS - Metadata Lost]",
            audio_url=path,
            duration_seconds=None,
            created_at=datetime.utcnow(),
            doctor_id=TARGET_DOCTOR_ID
        )
        
        try:
            await firestore_service.save_audio_metadata(metadata)
            print(f"   [+] Imported {audio_id}")
            imported_count += 1
        except Exception as e:
            print(f"   [!] Failed to import {audio_id}: {e}")
            
    if imported_count > 0:
        print(f"   ✅ Imported {imported_count} orphans.")
        
    print("\n🎉 Repair Complete! Check 'All My Audio' in the app.")

if __name__ == "__main__":
    asyncio.run(main())
