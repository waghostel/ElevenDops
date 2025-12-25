"""Error handling utilities for backend API."""

from typing import Dict, Any
from starlette import status

from backend.services.elevenlabs_service import (
    ElevenLabsSyncError,
    ElevenLabsErrorType,
    ElevenLabsTTSError,
    ElevenLabsAgentError,
    ElevenLabsDeleteError
)

def map_exception_to_status_code(exc: Exception) -> int:
    """Map exception to HTTP status code."""
    if isinstance(exc, (ElevenLabsSyncError, ElevenLabsTTSError, ElevenLabsAgentError, ElevenLabsDeleteError)):
        # If it has an error_type attribute (ElevenLabsSyncError does)
        if hasattr(exc, "error_type") and isinstance(exc.error_type, ElevenLabsErrorType):
            if exc.error_type == ElevenLabsErrorType.RATE_LIMIT:
                return status.HTTP_429_TOO_MANY_REQUESTS
            if exc.error_type == ElevenLabsErrorType.AUTH_ERROR:
                return status.HTTP_401_UNAUTHORIZED
            if exc.error_type == ElevenLabsErrorType.VALIDATION:
                return status.HTTP_400_BAD_REQUEST
            if exc.error_type == ElevenLabsErrorType.SERVER_ERROR:
                return status.HTTP_502_BAD_GATEWAY
            if exc.error_type == ElevenLabsErrorType.NETWORK:
                return status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Default for service errors if no specific type match or unknown
        return status.HTTP_502_BAD_GATEWAY

    if isinstance(exc, ValueError):
        return status.HTTP_400_BAD_REQUEST
        
    return status.HTTP_500_INTERNAL_SERVER_ERROR

def get_error_response(exc: Exception) -> Dict[str, Any]:
    """Generate standardized error response dict."""
    error_code = "INTERNAL_SERVER_ERROR"
    detail = str(exc)
    retryable = False
    
    # Extract more specific info from ElevenLabs errors
    if isinstance(exc, (ElevenLabsSyncError, ElevenLabsTTSError, ElevenLabsAgentError, ElevenLabsDeleteError)):
        error_code = "ELEVENLABS_ERROR"
        if hasattr(exc, "error_type") and isinstance(exc.error_type, ElevenLabsErrorType):
            error_code = exc.error_type.name
        
        if hasattr(exc, "is_retryable"):
            retryable = exc.is_retryable

    elif isinstance(exc, ValueError):
        error_code = "VALIDATION_ERROR"
        
    return {
        "detail": detail,
        "error_code": error_code,
        "retryable": retryable
    }
