import asyncio
import os
import uuid
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import KnowledgeDocumentCreate

async def verify_firestore():
    print("--- Firestore Connectivity Verification ---")
    
    # Ensure we are pointing to the emulator
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
    os.environ["TEST_AGAINST_EMULATOR"] = "true"
    
    print(f"Using Firestore Emulator at: {os.environ['FIRESTORE_EMULATOR_HOST']}")
    
    try:
        service = FirestoreDataService()
        
        # 1. Create a dummy document
        doc_id = str(uuid.uuid4())
        doc_data = KnowledgeDocumentCreate(
            disease_name="Test Disease",
            tags=["Test"],
            raw_content=f"Test content created at {uuid.uuid4()}",
            doctor_id="test_doctor"
        )
        
        print(f"Attempting to create document: {doc_id}...")
        created_doc = await service.create_knowledge_document(doc_data)
        print(f"Successfully created document with knowledge_id: {created_doc.knowledge_id}")
        
        # 2. Retrieve the document
        print(f"Attempting to retrieve document: {created_doc.knowledge_id}...")
        fetched_doc = await service.get_knowledge_document(created_doc.knowledge_id)
        
        if fetched_doc and fetched_doc.raw_content == doc_data.raw_content:
            print("Successfully retrieved and verified document content!")
        else:
            print("Failed to verify document content.")
            return False
            
        # 3. Delete the document
        print(f"Attempting to delete document: {created_doc.knowledge_id}...")
        deleted = await service.delete_knowledge_document(created_doc.knowledge_id)
        
        if deleted:
            print("Successfully deleted document.")
        else:
            print("Failed to delete document.")
            return False
            
        print("\n--- Verification Successful! ---")
        return True
        
    except Exception as e:
        print(f"\n--- Verification Failed! ---")
        print(f"Error: {e}")
        print("\nMake sure the Firestore emulator is running:")
        print("docker-compose -f docker-compose.dev.yml up -d firestore-emulator")
        return False

if __name__ == "__main__":
    asyncio.run(verify_firestore())
