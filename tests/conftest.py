import sys
from unittest.mock import MagicMock

# Mock elevenlabs module before it's imported
sys.modules["elevenlabs"] = MagicMock()
sys.modules["elevenlabs.client"] = MagicMock()

# Also mock other potential missing deps if needed
