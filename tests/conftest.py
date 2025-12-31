import sys
import os
from unittest.mock import MagicMock

# Mock elevenlabs module before it's imported
sys.modules["elevenlabs"] = MagicMock()
sys.modules["elevenlabs.client"] = MagicMock()

# Also mock other potential missing deps if needed

# ============================================================================
# Hypothesis Profile Configuration
# ============================================================================
# Usage:
#   Fast mode (10 examples):   pytest --hypothesis-profile=fast
#   CI mode (25 examples):     pytest --hypothesis-profile=ci
#   Default mode (50 examples): pytest (no flag needed)
# ============================================================================
from hypothesis import settings, Verbosity, Phase

# Fast profile - for quick local development iteration
settings.register_profile(
    "fast",
    max_examples=1,
    deadline=None,  # Disable deadline to avoid flaky tests
    verbosity=Verbosity.normal,
    phases=[Phase.explicit, Phase.reuse, Phase.generate],  # Skip shrinking for speed
)

# CI profile - balanced between speed and coverage
settings.register_profile(
    "ci",
    max_examples=25,  # 需要計算有多少排列組合
    deadline=None,
    verbosity=Verbosity.normal,
)

# Default profile - full coverage for thorough testing
settings.register_profile(
    "default",
    max_examples=50,
    deadline=None,
    verbosity=Verbosity.normal,
)

# Auto-load profile based on environment or default to 'fast' for local dev
# Set HYPOTHESIS_PROFILE env var to override, or use --hypothesis-profile flag
profile_name = os.environ.get("HYPOTHESIS_PROFILE", "default")
settings.load_profile(profile_name)
