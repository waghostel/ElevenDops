
import os
import sys

# Add root dir to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

print(f"CWD: {os.getcwd()}")
print(f"Root: {root_dir}")
print("Testing imports...")
try:
    import elevenlabs
    print(f"elevenlabs: {elevenlabs.__version__}")
except Exception as e:
    print(f"Failed to import elevenlabs: {e}")

try:
    import streamlit
    print(f"streamlit: {streamlit.__version__}")
except Exception as e:
    print(f"Failed to import streamlit: {e}")

try:
    from backend.middleware.rate_limit import limiter
    print("backend.middleware.rate_limit imported successfully")
except Exception as e:
    print(f"Failed to import backend module: {e}")
