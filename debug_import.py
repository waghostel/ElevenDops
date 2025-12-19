import sys
import os
print(f"CWD: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")

try:
    import backend.models.schemas
    print("Successfully imported backend.models.schemas")
except ImportError as e:
    print(f"Failed to import backend.models.schemas: {e}")

try:
    from backend.services.agent_service import AgentService
    print("Successfully imported AgentService")
except ImportError as e:
    print(f"Failed to import AgentService: {e}")
