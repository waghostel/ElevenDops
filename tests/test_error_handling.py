import pytest
from starlette import status
from backend.utils.errors import map_exception_to_status_code, get_error_response
from backend.services.elevenlabs_service import (
    ElevenLabsSyncError,
    ElevenLabsErrorType,
    ElevenLabsTTSError,
)

def test_map_exception_to_status_code_generic():
    exc = Exception("Something went wrong")
    assert map_exception_to_status_code(exc) == status.HTTP_500_INTERNAL_SERVER_ERROR

def test_map_exception_to_status_code_value_error():
    exc = ValueError("Invalid input")
    assert map_exception_to_status_code(exc) == status.HTTP_400_BAD_REQUEST

def test_map_exception_to_status_code_elevenlabs_rate_limit():
    exc = ElevenLabsSyncError(
        "Rate limit exceeded",
        error_type=ElevenLabsErrorType.RATE_LIMIT,
        is_retryable=True
    )
    assert map_exception_to_status_code(exc) == status.HTTP_429_TOO_MANY_REQUESTS

def test_map_exception_to_status_code_elevenlabs_auth():
    exc = ElevenLabsSyncError(
        "Unauthorized",
        error_type=ElevenLabsErrorType.AUTH_ERROR,
        is_retryable=False
    )
    assert map_exception_to_status_code(exc) == status.HTTP_401_UNAUTHORIZED

def test_get_error_response_generic():
    exc = Exception("Something went wrong")
    response = get_error_response(exc)
    assert response["detail"] == "Something went wrong"
    assert response["error_code"] == "INTERNAL_SERVER_ERROR"
    assert response["retryable"] is False

def test_get_error_response_elevenlabs():
    exc = ElevenLabsSyncError(
        "Rate limit exceeded",
        error_type=ElevenLabsErrorType.RATE_LIMIT,
        is_retryable=True
    )
    response = get_error_response(exc)
    assert response["detail"] == "Rate limit exceeded"
    assert response["error_code"] == "RATE_LIMIT"
    assert response["retryable"] is True
