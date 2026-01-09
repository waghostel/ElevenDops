import asyncio
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from backend.services.elevenlabs_service import ElevenLabsService
from backend.services.firestore_data_service import FirestoreDataService

load_dotenv(project_root / ".env")

async def test():
    print("Testing connections...")
    try:
        el = ElevenLabsService()
        db = FirestoreDataService()
        
        print("Fetching ElevenLabs docs...")
        docs = el.list_documents()
        print(f"Found {len(docs)} docs in ElevenLabs.")
        
        print("Fetching Firestore docs...")
        # Note: get_knowledge_documents is async
        db_docs = await db.get_knowledge_documents()
        print(f"Found {len(db_docs)} docs in Firestore.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
