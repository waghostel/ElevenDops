import os
from backend.config import get_settings

print("--- ENVIRONMENT VARIABLES ---")
for key in ["USE_MOCK_DATA", "USE_MOCK_STORAGE", "FIRESTORE_EMULATOR_HOST", "STORAGE_EMULATOR_HOST"]:
    print(f"{key}: {os.environ.get(key)}")

print("\n--- PYDANTIC SETTINGS ---")
try:
    s = get_settings()
    print(f"use_mock_data: {s.use_mock_data}")
    print(f"use_mock_storage: {s.use_mock_storage}")
    print(f"use_firestore_emulator: {s.use_firestore_emulator}")
    print(f"use_gcs_emulator: {s.use_gcs_emulator}")
except Exception as e:
    print(f"Error loading settings: {e}")
