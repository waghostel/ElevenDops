import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from backend.services.firestore_data_service import FirestoreDataService
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Other error: {e}")
