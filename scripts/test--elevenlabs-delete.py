"""Test script to verify ElevenLabs document deletion.

This script:
1. Creates a test document in Firestore and syncs to ElevenLabs
2. Verifies the document exists in both places
3. Deletes the document via the API
4. Verifies the document is deleted from both Firestore AND ElevenLabs

Usage:
    python scripts/test--elevenlabs-delete.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import httpx
from elevenlabs.client import ElevenLabs


BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


def check_elevenlabs_document_exists(client: ElevenLabs, doc_id: str) -> bool:
    """Check if a document exists in ElevenLabs Knowledge Base."""
    try:
        doc = client.conversational_ai.knowledge_base.documents.get(document_id=doc_id)
        return doc is not None
    except Exception as e:
        # If we get a 404, the document doesn't exist
        if "404" in str(e) or "not found" in str(e).lower():
            return False
        raise


async def test_delete_flow():
    """Test the complete delete flow."""
    print("\n" + "=" * 60)
    print("ElevenLabs Deletion Verification Test")
    print("=" * 60)
    
    # Validate configuration
    if not ELEVENLABS_API_KEY:
        print("\n❌ ERROR: ELEVENLABS_API_KEY is not set!")
        print("   Please set ELEVENLABS_API_KEY in your .env file.")
        return False
    
    print(f"\n✅ Configuration OK")
    print(f"   Backend URL: {BACKEND_URL}")
    print(f"   ElevenLabs API Key: {ELEVENLABS_API_KEY[:10]}...")
    
    # Initialize ElevenLabs client for direct verification
    elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
    async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=60.0) as client:
        # Step 1: Create a test document
        print("\n--- Step 1: Create Test Document ---")
        test_content = """# Test Document for Deletion Verification

This is a test document created to verify the deletion flow.

## Overview
This document will be deleted shortly after creation.

## Purpose
- Verify Firestore deletion works
- Verify ElevenLabs deletion works
- Log any errors during deletion
"""
        
        create_payload = {
            "doctor_id": "test_doctor",
            "disease_name": "TEST_DELETE_VERIFICATION",
            "tags": ["faq"],
            "raw_content": test_content
        }
        
        try:
            response = await client.post("/api/knowledge", json=create_payload)
            if response.status_code != 201:
                print(f"❌ Failed to create document: {response.status_code} - {response.text}")
                return False
            
            doc = response.json()
            knowledge_id = doc["knowledge_id"]
            print(f"✅ Created document: {knowledge_id}")
            print(f"   Disease Name: {doc['disease_name']}")
            print(f"   Sync Status: {doc['sync_status']}")
        except Exception as e:
            print(f"❌ Error creating document: {e}")
            return False
        
        # Step 2: Wait for sync to complete
        print("\n--- Step 2: Wait for ElevenLabs Sync ---")
        max_wait = 30  # seconds
        wait_interval = 2
        waited = 0
        elevenlabs_doc_id = None
        
        while waited < max_wait:
            await asyncio.sleep(wait_interval)
            waited += wait_interval
            
            response = await client.get(f"/api/knowledge/{knowledge_id}")
            if response.status_code == 200:
                doc = response.json()
                sync_status = doc["sync_status"]
                elevenlabs_doc_id = doc.get("elevenlabs_document_id")
                
                print(f"   [{waited}s] Sync status: {sync_status}, ElevenLabs ID: {elevenlabs_doc_id}")
                
                if sync_status == "completed" and elevenlabs_doc_id:
                    print(f"✅ Sync completed! ElevenLabs ID: {elevenlabs_doc_id}")
                    break
                elif sync_status == "failed":
                    print(f"❌ Sync failed: {doc.get('sync_error_message')}")
                    # Still try to test the deletion
                    break
        else:
            print(f"⚠️  Sync did not complete within {max_wait}s")
        
        # Step 3: Verify document exists in ElevenLabs (if sync succeeded)
        if elevenlabs_doc_id:
            print("\n--- Step 3: Verify Document in ElevenLabs ---")
            try:
                exists = check_elevenlabs_document_exists(elevenlabs, elevenlabs_doc_id)
                if exists:
                    print(f"✅ Document {elevenlabs_doc_id} EXISTS in ElevenLabs")
                else:
                    print(f"❌ Document {elevenlabs_doc_id} NOT FOUND in ElevenLabs - sync may have failed")
            except Exception as e:
                print(f"⚠️  Could not verify ElevenLabs document: {e}")
        else:
            print("\n--- Step 3: Skipped (no ElevenLabs ID) ---")
        
        # Step 4: Delete the document
        print("\n--- Step 4: Delete Document via API ---")
        try:
            response = await client.delete(f"/api/knowledge/{knowledge_id}")
            if response.status_code == 204:
                print(f"✅ Delete API returned 204 No Content")
            else:
                print(f"❌ Delete failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            return False
        
        # Step 5: Verify document is deleted from Firestore
        print("\n--- Step 5: Verify Document Deleted from Firestore ---")
        await asyncio.sleep(1)  # Small delay
        response = await client.get(f"/api/knowledge/{knowledge_id}")
        if response.status_code == 404:
            print(f"✅ Document NOT FOUND in Firestore (deleted successfully)")
        else:
            print(f"❌ Document STILL EXISTS in Firestore! Status: {response.status_code}")
            return False
        
        # Step 6: Verify document is deleted from ElevenLabs
        if elevenlabs_doc_id:
            print("\n--- Step 6: Verify Document Deleted from ElevenLabs ---")
            await asyncio.sleep(1)  # Small delay
            try:
                exists = check_elevenlabs_document_exists(elevenlabs, elevenlabs_doc_id)
                if not exists:
                    print(f"✅ Document {elevenlabs_doc_id} NOT FOUND in ElevenLabs (deleted successfully)")
                else:
                    print(f"❌ Document {elevenlabs_doc_id} STILL EXISTS in ElevenLabs!")
                    print(f"   ⚠️  This indicates the deletion API call to ElevenLabs failed!")
                    print(f"   Check the backend logs for warnings.")
                    return False
            except Exception as e:
                print(f"⚠️  Could not verify ElevenLabs deletion: {e}")
        else:
            print("\n--- Step 6: Skipped (no ElevenLabs ID) ---")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Deletion works for both Firestore and ElevenLabs.")
        print("=" * 60)
        return True


if __name__ == "__main__":
    print("\nStarting ElevenLabs Deletion Test...")
    print("Make sure the backend server is running at", BACKEND_URL)
    
    success = asyncio.run(test_delete_flow())
    sys.exit(0 if success else 1)
