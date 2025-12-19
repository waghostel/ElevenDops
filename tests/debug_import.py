import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Importing DataServiceInterface...")
    from backend.services.data_service import DataServiceInterface
    print("Success.")

    print("Importing FirestoreDataService...")
    from backend.services.firestore_data_service import FirestoreDataService
    print("Success.")

    print("Instantiating FirestoreDataService...")
    s = FirestoreDataService()
    print("Success.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
