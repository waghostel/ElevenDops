"""Diagnosis script for audio playback issues.

This script verifies:
1. Audio metadata exists in Firestore
2. Audio files exist in GCS
3. Signed URLs can be generated
4. Streaming endpoint works correctly
"""

import asyncio
import sys
from pathlib import Path

# Fix encoding for Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

from backend.config import get_settings
from backend.services.storage_service import get_storage_service, get_signed_url
from backend.services.data_service import get_data_service


async def diagnose_audio_playback():
    """Run comprehensive audio playback diagnosis."""
    settings = get_settings()
    
    print("=" * 60)
    print("AUDIO PLAYBACK DIAGNOSIS")
    print("=" * 60)
    
    # 1. Check configuration
    print("\n[CONFIG] CONFIGURATION:")
    print(f"  - USE_GCS_EMULATOR: {settings.use_gcs_emulator}")
    print(f"  - USE_MOCK_STORAGE: {settings.use_mock_storage}")
    print(f"  - GCS_BUCKET_NAME: {settings.gcs_bucket_name}")
    print(f"  - GOOGLE_CLOUD_PROJECT: {settings.google_cloud_project}")
    print(f"  - USE_FIRESTORE_EMULATOR: {settings.use_firestore_emulator}")
    print(f"  - FIRESTORE_DATABASE_ID: {settings.firestore_database_id}")
    print(f"  - FASTAPI_PORT: {settings.fastapi_port}")
    
    # 2. Get audio metadata from Firestore
    print("\n[FIRESTORE] FETCHING AUDIO METADATA FROM FIRESTORE:")
    data_service = get_data_service()
    
    try:
        # Get all audio files (no filter = get all)
        audio_files = await data_service.get_audio_files()
        print(f"  [OK] Found {len(audio_files)} audio file(s) in Firestore")
        
        if not audio_files:
            print("  [WARN] No audio files found in Firestore query. Procedding with other checks.")
            # return  # Continue to check health and strategy even if empty
            
        # Display first 5 audio files
        for i, audio in enumerate(audio_files[:5]):
            print(f"\n  Audio #{i+1}:")
            print(f"    - audio_id: {audio.audio_id}")
            print(f"    - audio_url (stored): {audio.audio_url}")
            print(f"    - knowledge_id: {audio.knowledge_id}")
            print(f"    - doctor_id: {audio.doctor_id}")
            print(f"    - created_at: {audio.created_at}")
            
    except Exception as e:
        print(f"  [ERROR] Error fetching audio metadata: {e}")
        return
    
    # 3. Test GCS file existence
    print("\n[GCS] VERIFYING GCS FILE EXISTENCE:")
    storage_service = get_storage_service()
    
    for i, audio in enumerate(audio_files[:3]):
        stored_url = audio.audio_url
        
        # Determine the storage path
        if stored_url.startswith("https://storage.googleapis.com/"):
            parts = stored_url.split("/")
            if len(parts) > 4:
                storage_path = "/".join(parts[4:])
            else:
                storage_path = stored_url
        elif stored_url.startswith("http"):
            storage_path = None  # It's a direct URL (mock/emulator)
        else:
            storage_path = stored_url  # It's a relative path
        
        print(f"\n  Audio #{i+1} ({audio.audio_id}):")
        print(f"    - Stored URL: {stored_url}")
        print(f"    - Resolved path: {storage_path}")
        
        if storage_path:
            try:
                exists = storage_service.file_exists(storage_path)
                print(f"    - File exists in GCS: {'[OK] YES' if exists else '[FAIL] NO'}")
            except Exception as e:
                print(f"    - File check error: {e}")
    
    # 4. Test signed URL generation
    print("\n[SIGN] TESTING SIGNED URL GENERATION:")
    test_audio = audio_files[0]
    
    try:
        signed_url = get_signed_url(test_audio.audio_url)
        print(f"  - Original URL: {test_audio.audio_url}")
        print(f"  - Signed URL: {signed_url[:100]}..." if len(signed_url) > 100 else f"  - Signed URL: {signed_url}")
        
        # Test if signed URL is accessible
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.head(signed_url)
            print(f"  - Signed URL accessible: {'[OK] YES' if response.status_code == 200 else f'[FAIL] NO (HTTP {response.status_code})'}")
            if response.status_code == 200:
                content_length = response.headers.get("content-length", "unknown")
                content_type = response.headers.get("content-type", "unknown")
                print(f"  - Content-Type: {content_type}")
                print(f"  - Content-Length: {content_length} bytes")
    except Exception as e:
        print(f"  [ERROR] Error with signed URL: {e}")
    
    # 5. Test streaming endpoint
    print("\n[STREAM] TESTING STREAMING ENDPOINT:")
    backend_url = f"http://localhost:{settings.fastapi_port}"
    stream_url = f"{backend_url}/api/audio/stream/{test_audio.audio_id}"
    print(f"  - Stream URL: {stream_url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First check if backend is running
            try:
                health_response = await client.get(f"{backend_url}/api/health")
                print(f"  - Backend health: {'[OK] Running' if health_response.status_code == 200 else f'[WARN] Status {health_response.status_code}'}")
            except httpx.ConnectError:
                print("  [ERROR] Backend not running! Start it with: uv run uvicorn backend.main:app --port 8000")
                return
            
            # Test stream endpoint
            response = await client.get(stream_url)
            print(f"  - Stream response status: {response.status_code}")
            print(f"  - Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"  - Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200 and len(response.content) > 0:
                print("  [OK] Stream endpoint working correctly!")
            elif response.status_code == 200 and len(response.content) == 0:
                print("  [FAIL] Stream returns empty content - THIS IS THE BUG!")
            else:
                print(f"  [FAIL] Stream failed: {response.text[:200]}")
                
    except Exception as e:
        print(f"  [ERROR] Stream test error: {e}")
    
    # 6. Direct generator test
    print("\n[TEST] TESTING STREAM_AUDIO METHOD DIRECTLY:")
    from backend.services.audio_service import get_audio_service
    audio_service = get_audio_service()
    
    try:
        # stream_audio is now sync, returns a sync generator directly
        result = audio_service.stream_audio(test_audio.audio_id)
        print(f"  - stream_audio returned: {type(result)}")
        
        # Check if it's a generator
        if hasattr(result, '__iter__') or hasattr(result, '__next__'):
            print("  - Result is iterable: [OK]")
            # Try to get first chunk
            total_bytes = 0
            chunk_count = 0
            for chunk in result:
                total_bytes += len(chunk)
                chunk_count += 1
                if chunk_count >= 3:  # Just test first few chunks
                    break
            print(f"  - First {chunk_count} chunks: {total_bytes} bytes")
        else:
            print(f"  - Result is NOT iterable: [FAIL] (this is the bug!)")
            
    except Exception as e:
        print(f"  [ERROR] Direct test error: {e}")
        import traceback
        traceback.print_exc()

    # 7. Verify URL Strategy
    print("\n[STRATEGY] VERIFYING URL STRATEGY:")
    try:
        from backend.services.audio_service import get_audio_service
        audio_service = get_audio_service()
        
        # This calls the logic we just refactored
        processed_audio_files = await audio_service.get_audio_files(doctor_id=test_audio.doctor_id)
        
        if processed_audio_files:
            # Find our test audio in the processed list
            sample_audio = next((a for a in processed_audio_files if a.audio_id == test_audio.audio_id), processed_audio_files[0])
            print(f"  - Final Processed URL: {sample_audio.audio_url}")
            
            if "Signature=" in sample_audio.audio_url or "X-Goog-Signature=" in sample_audio.audio_url:
                print("  - Strategy: [OK] [SIGNED URL] (Service Account detected!)")
            elif "/api/audio/stream/" in sample_audio.audio_url:
                 print(f"  - Strategy: [PROXY URL] (Fallback mode)")
                 print(f"  - Proxy Base: {settings.backend_api_url}")
            else:
                 print("  - Strategy: [UNKNOWN/OTHER]")
        else:
            print("  [WARN] No audio files returned from AudioService")
                 
    except Exception as e:
         print(f"  [ERROR] Strategy check error: {e}")
         import traceback
         traceback.print_exc()

    print("\n" + "=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(diagnose_audio_playback())
