from backend.config import get_settings
import os
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

print("--- DIAGNOSTIC START ---")
print(f"Current working dir: {os.getcwd()}")
print(f"Env file exists: {os.path.exists('.env')}")

# Check raw env var
raw_val = os.getenv("FIRESTORE_DATABASE_ID")
print(f"Raw os.getenv('FIRESTORE_DATABASE_ID'): '{raw_val}'")
print(f"Raw os.getenv('USE_MOCK_DATA'): '{os.getenv('USE_MOCK_DATA')}'")
print(f"Raw os.getenv('GOOGLE_CLOUD_PROJECT'): '{os.getenv('GOOGLE_CLOUD_PROJECT')}'")

# Check Pydantic settings
try:
    settings = get_settings()
    print(f"Settings.firestore_database_id: '{settings.firestore_database_id}'")
    print(f"Settings.google_cloud_project: '{settings.google_cloud_project}'")
    print(f"Settings.use_mock_data: {settings.use_mock_data}")
except Exception as e:
    print(f"Error loading settings: {e}")

print("--- DIAGNOSTIC END ---")
