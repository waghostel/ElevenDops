import asyncio
from google.cloud import firestore
import os
import time

async def check_firestore():
    print("Checking Firestore connection...")
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
    os.environ["GCLOUD_PROJECT"] = "elevendops"
    
    try:
        db = firestore.AsyncClient(project="elevendops") # Use AsyncClient if available or Client
        # google-cloud-firestore usually exposes Client (sync) and AsyncClient
        # But for simple check sync is fine if we suspect network hang
        
        print("Client initialized.")
        doc_ref = db.collection("health_check").document("test")
        print("Writing...")
        await doc_ref.set({"status": "ok", "timestamp": time.time()})
        print("Write success.")
        
        print("Reading...")
        doc = await doc_ref.get()
        print(f"Read success: {doc.to_dict()}")
        
    except Exception as e:
        print(f"Firestore check FAILED: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(check_firestore())
