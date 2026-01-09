"""Rate limiting middleware using slowapi.

This module provides rate limiting functionality to protect API endpoints
from abuse, brute force attacks, and DoS attacks.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance using client IP as the rate limit key
limiter = Limiter(key_func=get_remote_address)

# Default rate limits for different endpoint categories
# These can be applied using @limiter.limit() decorator
RATE_LIMITS = {
    "default": "60/minute",      # General API endpoints
    "audio": "10/minute",        # ElevenLabs API (quota protection)
    "agent": "20/minute",        # AI API calls
    "session": "5/minute",       # Session creation
}
