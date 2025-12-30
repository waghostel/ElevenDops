
import sys
import os
import importlib.util

print("Sys Path:", sys.path)

try:
    import google
    print("\ngoogle imported:", google)
    print("google.__path__:", google.__path__)
except ImportError as e:
    print("\ngoogle import failed:", e)

try:
    import google.cloud
    print("\ngoogle.cloud imported:", google.cloud)
    print("google.cloud.__path__:", google.cloud.__path__)
except ImportError as e:
    print("\ngoogle.cloud import failed:", e)

try:
    import google.cloud.firestore
    print("\ngoogle.cloud.firestore imported:", google.cloud.firestore)
except ImportError as e:
    print("\ngoogle.cloud.firestore import failed:", e)

# Check specific file existence
site_packages = [p for p in sys.path if 'site-packages' in p][0]
firestore_path = os.path.join(site_packages, 'google', 'cloud', 'firestore')
print(f"\nChecking path: {firestore_path}")
print(f"Exists: {os.path.exists(firestore_path)}")
if os.path.exists(firestore_path):
    print("Listing:", os.listdir(firestore_path))
