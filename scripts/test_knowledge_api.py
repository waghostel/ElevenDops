import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/knowledge"

def log(msg):
    print(msg)
    with open("debug_api_test.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_knowledge_api():
    with open("debug_api_test.log", "w", encoding="utf-8") as f:
        f.write("Starting test run...\n")
    log("🚀 Starting Knowledge API Test...")
    
    # 1. List existing documents
    log("\n[1] Listing existing documents...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        docs = response.json().get("documents", [])
        log(f"    Found {len(docs)} documents.")
    except Exception as e:
        log(f"❌ Failed to list documents: {e}")
        sys.exit(1)

    # 2. Create a new document
    log("\n[2] Creating new document 'API Test Disease'...")
    payload = {
        "doctor_id": "test_doctor",
        "disease_name": "API Test Disease",
        "document_type": "protocols",
        "raw_content": "# Treatment Protocol\n\nThis is a test protocol."
    }
    
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        new_doc = response.json()
        doc_id = new_doc["knowledge_id"]
        log(f"✅ Document created with ID: {doc_id}")
        log(f"    Initial Status: {new_doc['sync_status']}")
    except Exception as e:
        log(f"❌ Failed to create document: {e}")
        try:
            log(f"Response: {response.text}")
        except:
            pass
        sys.exit(1)

    # 3. Wait for Sync (Mock or Real)
    log("\n[3] Waiting for sync to complete...")
    for i in range(10):
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/{doc_id}")
        doc = response.json()
        status = doc["sync_status"]
        log(f"    Status check {i+1}: {status}")
        
        if status == "completed":
            log("✅ Sync COMPLETED!")
            if "mock_doc_" in (doc.get("elevenlabs_document_id") or ""):
                log("    (Verified Mock ID present)")
            break
        elif status == "failed":
            log(f"❌ Sync FAILED: {doc.get('sync_error_message')}")
            break
    else:
        log("⚠️  Timed out waiting for sync.")

    # 4. List again to verify
    log("\n[4] Listing documents again...")
    response = requests.get(BASE_URL)
    docs = response.json().get("documents", [])
    found = any(d["knowledge_id"] == doc_id for d in docs)
    if found:
        log("✅ New document found in list.")
    else:
        log("❌ New document NOT found in list!")

    # 5. Delete document
    log(f"\n[5] Deleting document {doc_id}...")
    try:
        response = requests.delete(f"{BASE_URL}/{doc_id}")
        if response.status_code == 204:
            log("✅ Delete request successful (204).")
        else:
            log(f"❌ Delete failed: {response.status_code} {response.text}")
    except Exception as e:
        log(f"❌ Delete request failed: {e}")

    # 6. Verify Deletion
    log("\n[6] Verifying deletion...")
    response = requests.get(f"{BASE_URL}/{doc_id}")
    if response.status_code == 404:
        log("✅ Document not found (404) as expected.")
    else:
        log(f"❌ Document still exists! Status: {response.status_code}")

    log("\n🎉 Test Complete!")

if __name__ == "__main__":
    test_knowledge_api()
