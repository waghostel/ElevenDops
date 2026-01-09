"""Cleanup script to delete ALL knowledge base documents from ElevenLabs.

This script is intended for removing orphaned documents that were synced
before connecting to real Firestore.

Usage:
    python scripts/cleanup--elevenlabs-knowledge.py

Requirements:
    - ELEVENLABS_API_KEY must be set in .env or environment
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# Load environment variables
load_dotenv(project_root / ".env")


def main():
    """List and delete all ElevenLabs knowledge base documents."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not found in environment.")
        print("Please set it in your .env file.")
        sys.exit(1)

    client = ElevenLabs(api_key=api_key)

    print("Fetching all knowledge base documents...")
    try:
        # List all documents
        docs = client.conversational_ai.knowledge_base.list()
        doc_list = list(docs.documents) if hasattr(docs, 'documents') else list(docs)
    except Exception as e:
        print(f"ERROR: Failed to list documents: {e}")
        sys.exit(1)

    if not doc_list:
        print("No documents found in ElevenLabs Knowledge Base. Nothing to delete.")
        return

    print(f"\nFound {len(doc_list)} document(s):\n")
    for i, doc in enumerate(doc_list, 1):
        doc_id = getattr(doc, 'id', None) or getattr(doc, 'document_id', 'unknown')
        doc_name = getattr(doc, 'name', 'Unnamed')
        print(f"  {i}. {doc_name} (ID: {doc_id})")

    # Confirm deletion
    print("\n" + "=" * 60)
    print("WARNING: This will DELETE ALL documents listed above.")
    print("This action is IRREVERSIBLE.")
    print("=" * 60)

    confirm = input("\nType 'DELETE ALL' to confirm: ")
    if confirm != "DELETE ALL":
        print("Aborted. No documents were deleted.")
        return

    # Delete each document
    print("\nDeleting documents...")
    deleted_count = 0
    failed_count = 0

    for doc in doc_list:
        doc_id = getattr(doc, 'id', None) or getattr(doc, 'document_id', None)
        doc_name = getattr(doc, 'name', 'Unnamed')

        if not doc_id:
            print(f"  SKIP: Could not get ID for '{doc_name}'")
            failed_count += 1
            continue

        try:
            client.conversational_ai.knowledge_base.documents.delete(doc_id)
            print(f"  DELETED: {doc_name}")
            deleted_count += 1
        except Exception as e:
            print(f"  FAILED: {doc_name} - {e}")
            failed_count += 1

    print("\n" + "-" * 40)
    print(f"Summary: {deleted_count} deleted, {failed_count} failed.")
    print("Done.")


if __name__ == "__main__":
    main()
