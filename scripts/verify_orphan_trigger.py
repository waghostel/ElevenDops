import asyncio
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from backend.services.firestore_service import get_firestore_service

load_dotenv(project_root / ".env")

async def delete_firestore_record(knowledge_id: str):
    print(f"Deleting Firestore record: {knowledge_id}...")
    try:
        service = get_firestore_service()
        db = service.db
        db.collection("knowledge_documents").document(knowledge_id).delete()
        print("Deleted.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_orphan_trigger.py <knowledge_id>")
    else:
        asyncio.run(delete_firestore_record(sys.argv[1]))
