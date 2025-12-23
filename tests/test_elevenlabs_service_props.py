"""Property tests for ElevenLabs Service."""

import pytest
from unittest.mock import MagicMock, patch
from backend.services.elevenlabs_service import (
    ElevenLabsService, 
    ElevenLabsSyncError, 
    ElevenLabsDeleteError,
    ElevenLabsErrorType,
    _should_retry
)

# Using mocks for ElevenLabs service properties since we can't call real API in tests without cost/auth.

@pytest.fixture
def mock_elevenlabs_client():
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        instance = MockClient.return_value
        yield instance

@pytest.mark.asyncio
async def test_error_classification():
    """Test _classify_error helper method."""
    service = ElevenLabsService()
    
    # Rate Limit
    error = Exception("429 Too Many Requests")
    type_, retry = service._classify_error(error)
    assert type_ == ElevenLabsErrorType.RATE_LIMIT
    assert retry is True

    # Auth Error
    error = Exception("401 Unauthorized")
    type_, retry = service._classify_error(error)
    assert type_ == ElevenLabsErrorType.AUTH_ERROR
    assert retry is False

    # Server Error
    error = Exception("500 Internal Server Error")
    type_, retry = service._classify_error(error)
    assert type_ == ElevenLabsErrorType.SERVER_ERROR
    assert retry is True

    # Network Error
    error = Exception("Connection timed out")
    type_, retry = service._classify_error(error)
    assert type_ == ElevenLabsErrorType.NETWORK
    assert retry is True

    # Unknown
    error = Exception("Random Error")
    type_, retry = service._classify_error(error)
    assert type_ == ElevenLabsErrorType.UNKNOWN
    assert retry is False

@pytest.mark.asyncio
async def test_retry_on_transient_error(mock_elevenlabs_client):
    """Test that create_document retries on transient errors."""
    service = ElevenLabsService()
    
    # Mock behavior: Fail twice with 500, then succeed
    mock_response = MagicMock()
    mock_response.id = "el_doc_success"
    
    # Note: tenacity retry behavior might need patching sleep to be fast
    # but with wait_exponential min=1 it might take a few seconds.
    # We can patch 'tenacity.nap.time.sleep' to speed it up if needed, 
    # but explicit patching of wait is cleaner. 
    # However, for simplicity here, we'll just let it run or patch sleep.
    
    mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.side_effect = [
        Exception("500 Server Error"),
        Exception("502 Bad Gateway"), 
        mock_response
    ]
    
    with patch("time.sleep"): # Fast forward sleep
        doc_id = service.create_document("text", "name")
    
    assert doc_id == "el_doc_success"
    assert mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.call_count == 3

@pytest.mark.asyncio
async def test_no_retry_on_permanent_error(mock_elevenlabs_client):
    """Test that create_document does not retry on permanent errors."""
    service = ElevenLabsService()
    
    mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.side_effect = Exception("401 Unauthorized")
    
    with pytest.raises(ElevenLabsSyncError) as exc_info:
        service.create_document("text", "name")
    
    assert exc_info.value.error_type == ElevenLabsErrorType.AUTH_ERROR
    assert mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.call_count == 1

@pytest.mark.asyncio
async def test_max_retries_exceeded(mock_elevenlabs_client):
    """Test failure after max retries."""
    service = ElevenLabsService()
    
    mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.side_effect = Exception("500 Server Error")
    
    # tenacity defaults: stop_after_attempt(3)
    with pytest.raises(ElevenLabsSyncError) as exc_info:
         with patch("time.sleep"):
             service.create_document("text", "name")
             
    assert exc_info.value.error_type == ElevenLabsErrorType.SERVER_ERROR
    assert mock_elevenlabs_client.conversational_ai.knowledge_base.documents.create_from_file.call_count == 3

@pytest.mark.asyncio
async def test_should_retry_helper():
    """Test _should_retry function."""
    # Retryable error
    err = ElevenLabsSyncError("msg", is_retryable=True)
    assert _should_retry(err) is True
    
    # Non-retryable error
    err = ElevenLabsSyncError("msg", is_retryable=False)
    assert _should_retry(err) is False
    
    # Other exception
    err = Exception("foo")
    assert _should_retry(err) is False
