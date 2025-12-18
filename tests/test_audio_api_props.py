"""Property tests for Audio API routes."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis import strategies as st

from backend.api.routes.audio import router
from backend.main import app
from backend.services.audio_service import AudioService, get_audio_service
from backend.services.elevenlabs_service import ElevenLabsTTSError

client = TestClient(app)

@given(st.text(min_size=1, max_size=50000))
def test_audio_generate_error_handling(script: str):
    """**Feature: education-audio-page, Property 5: Error Response Display**
    
    Validates that API errors return proper error responses (HTTP 502 for ElevenLabs errors).
    """
    
    # Mock service to raise ElevenLabsTTSError
    mock_service = MagicMock(spec=AudioService)
    error_msg = "ElevenLabs API Error"
    mock_service.generate_audio.side_effect = ElevenLabsTTSError(error_msg)
    
    # Override dependency
    app.dependency_overrides[get_audio_service] = lambda: mock_service
    
    try:
        response = client.post(
            "/api/audio/generate",
            json={
                "knowledge_id": "test_id",
                "script": script,
                "voice_id": "test_voice"
            }
        )
        
        assert response.status_code == 502
        assert response.json()["detail"] == error_msg
        
    finally:
        app.dependency_overrides = {}

@given(st.text(min_size=1))
def test_voices_list_error_handling(reason: str):
    """**Feature: education-audio-page, Property 5: Error Response Display**
    
    Validates that API errors return proper error responses for voice listing.
    """
    # Mock service to raise ElevenLabsTTSError
    mock_service = MagicMock(spec=AudioService)
    mock_service.get_available_voices.side_effect = ElevenLabsTTSError(reason)
    
    app.dependency_overrides[get_audio_service] = lambda: mock_service
    
    try:
        response = client.get("/api/audio/voices/list")
        
        assert response.status_code == 502
        assert response.json()["detail"] == reason
    finally:
        app.dependency_overrides = {}
