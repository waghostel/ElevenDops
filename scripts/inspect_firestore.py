import asyncio
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from google.cloud import firestore
from backend.services.firestore_service import get_firestore_service

load_dotenv(project_root / ".env")

async def list_collections():
    print("Listing collections...")
    try:
        service = get_firestore_service()
        db = service.db
        collections = db.collections()
        for col in collections:
            print(f"- {col.id}")
            # Count docs
            docs = col.stream()
            count = sum(1 for _ in docs)
            print(f"  ({count} documents)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_collections())
