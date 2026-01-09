import asyncio
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import KnowledgeDocumentCreate, SyncStatus

load_dotenv(project_root / ".env")

async def create_test_doc():
    print("Creating test document in Firestore...")
    try:
        db = FirestoreDataService()
        
        doc = KnowledgeDocumentCreate(
            doctor_id="test_doctor",
            disease_name="Test Disease",
            tags=["test", "script"],
            raw_content="This is a test document for reconciliation verification."
        )
        
        # We'll use the service method but we'll deliberately NOT sync to ElevenLabs here
        # (The service method might trigger a sync if called through the API, 
        # but here we are just calling the DB part)
        
        # Actually create_knowledge_document in service DOES NOT trigger sync (the ROUTE does)
        created_doc = await db.create_knowledge_document(doc)
        print(f"Created doc in Firestore with ID: {created_doc.knowledge_id}")
        print(f"Sync status: {created_doc.sync_status}")
        
        return created_doc.knowledge_id
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(create_test_doc())
