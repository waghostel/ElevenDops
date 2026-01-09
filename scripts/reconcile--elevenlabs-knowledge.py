"""Reconciliation script for Firestore-ElevenLabs Knowledge Base.

Detects and fixes:
1. Orphans: Documents in ElevenLabs not tracked in Firestore.
2. Unsynced: Documents in Firestore missing from or failed in ElevenLabs.

Usage:
    python scripts/reconcile--elevenlabs-knowledge.py --audit
    python scripts/reconcile--elevenlabs-knowledge.py --fix-orphans
    python scripts/reconcile--elevenlabs-knowledge.py --fix-unsynced
"""

import os
import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Set

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from backend.services.elevenlabs_service import ElevenLabsService
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import SyncStatus, KnowledgeDocumentCreate

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(project_root / ".env")


async def run_reconciliation(mode: str):
    """Run reconciliation based on the specified mode."""
    el_service = ElevenLabsService()
    db_service = FirestoreDataService()

    logger.info("Fetching documents from ElevenLabs...")
    el_docs = el_service.list_documents()
    el_map = {d["id"]: d for d in el_docs}
    
    logger.info("Fetching documents from Firestore...")
    db_docs = await db_service.get_knowledge_documents()
    db_map = {d.knowledge_id: d for d in db_docs}
    
    # Map elevenlabs_id to firestore record
    db_el_id_to_fs = {d.elevenlabs_document_id: d for d in db_docs if d.elevenlabs_document_id}

    # 1. Detect Orphans (In ElevenLabs but not in Firestore)
    orphans = [el for el_id, el in el_map.items() if el_id not in db_el_id_to_fs]
    
    # 2. Detect Unsynced (In Firestore but missing from or failed in ElevenLabs)
    unsynced = []
    for db_id, db_doc in db_map.items():
        if db_doc.sync_status != SyncStatus.COMPLETED:
            unsynced.append(db_doc)
        elif db_doc.elevenlabs_document_id not in el_map:
            unsynced.append(db_doc)

    # --- Mode: Audit ---
    if mode == "audit":
        logger.info("\n" + "="*50)
        logger.info("AUDIT REPORT")
        logger.info("="*50)
        
        logger.info(f"ElevenLabs Total: {len(el_docs)}")
        logger.info(f"Firestore Total:  {len(db_docs)}")
        
        logger.info(f"\n[Orphans] Found {len(orphans)} documents in ElevenLabs not in Firestore.")
        for d in orphans:
            logger.info(f"  - {d['name']} (ID: {d['id']})")
            
        logger.info(f"\n[Unsynced] Found {len(unsynced)} documents in Firestore not synced correctly.")
        for d in unsynced:
            status = d.sync_status.value if hasattr(d.sync_status, 'value') else d.sync_status
            logger.info(f"  - {d.disease_name} (ID: {d.knowledge_id}, Status: {status})")
            
        logger.info("\nRun with --fix-orphans or --fix-unsynced to resolve these.")

    # --- Mode: Fix Orphans ---
    elif mode == "fix-orphans":
        if not orphans:
            logger.info("No orphans found.")
            return

        logger.warning(f"Deleting {len(orphans)} orphans from ElevenLabs...")
        for d in orphans:
            try:
                el_service.delete_document(d["id"])
                logger.info(f"  Deleted: {d['name']}")
            except Exception as e:
                logger.error(f"  Failed to delete {d['name']}: {e}")

    # --- Mode: Fix Unsynced ---
    elif mode == "fix-unsynced":
        if not unsynced:
            logger.info("No unsynced documents found.")
            return

        logger.info(f"Syncing {len(unsynced)} documents to ElevenLabs...")
        for d in unsynced:
            try:
                logger.info(f"  Syncing: {d.disease_name}...")
                # The resync logic is usually in the API, but we'll recreate the create_document logic
                tags_str = "_".join(d.tags)
                name = f"{d.disease_name}_{tags_str}"
                
                # Perform the sync
                el_id = el_service.create_document(d.raw_content, name)
                
                # Update Firestore
                await db_service.update_knowledge_sync_status(
                    knowledge_id=d.knowledge_id,
                    status=SyncStatus.COMPLETED,
                    elevenlabs_id=el_id
                )
                logger.info(f"  Success: {d.disease_name} (New ID: {el_id})")
            except Exception as e:
                logger.error(f"  Failed to sync {d.disease_name}: {e}")
                await db_service.update_knowledge_sync_status(
                    knowledge_id=d.knowledge_id,
                    status=SyncStatus.FAILED,
                    error_message=str(e)
                )


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs-Firestore Reconciliation Tool")
    parser.add_argument("--audit", action="store_true", help="Report discrepancies without fixing")
    parser.add_argument("--fix-orphans", action="store_true", help="Delete documents from ElevenLabs not in Firestore")
    parser.add_argument("--fix-unsynced", action="store_true", help="Sync Firestore documents missing from ElevenLabs")
    
    args = parser.parse_args()
    
    if not (args.audit or args.fix_orphans or args.fix_unsynced):
        parser.print_help()
        return

    mode = "audit"
    if args.fix_orphans: mode = "fix-orphans"
    elif args.fix_unsynced: mode = "fix-unsynced"
    
    asyncio.run(run_reconciliation(mode))


if __name__ == "__main__":
    main()
