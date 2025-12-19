
import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock, MagicMock

from backend.services.patient_service import PatientService
from backend.models.schemas import PatientSessionCreate, PatientSessionResponse

# **Feature: patient-params, Property 5: Message Round Trip**
# **Validates: Requirements 4.4**
@pytest.mark.asyncio
async def test_property_5_message_round_trip():
    """
    Property 5: Message Round Trip
    For any valid patient question submitted during an active conversation, the system 
    should send the message to the backend and receive a response containing both text and audio data.
    """
    # Setup Mocks
    mock_data_service = AsyncMock()
    mock_elevenlabs_service = MagicMock()
    
    # Mock create session persistence
    mock_data_service.create_patient_session.side_effect = lambda s: s
    # Mock get session to return a valid session
    from datetime import datetime
    session_response = PatientSessionResponse(
        session_id="test_session_id",
        patient_id="patient123",
        agent_id="agent123",
        signed_url="wss://test",
        created_at=datetime.now()
    )
    
    mock_data_service.get_patient_session.return_value = session_response
    
    # Mock ElevenLabs send_text_message
    expected_text = "Response text"
    expected_audio = b"fakeaudio"
    mock_elevenlabs_service.send_text_message.return_value = (expected_text, expected_audio)
    
    service = PatientService(data_service=mock_data_service, elevenlabs_service=mock_elevenlabs_service)

    # Test
    message = "Hello, Doctor."
    response = await service.send_message("test_session_id", message)
    
    # Assertions
    assert response.response_text == expected_text
    assert response.audio_data is not None
    # Check if base64 encoded
    import base64
    decoded = base64.b64decode(response.audio_data)
    assert decoded == expected_audio
    
    # Verify interaction
    mock_elevenlabs_service.send_text_message.assert_called_with("agent123", message)

if __name__ == "__main__":
    # verification script
    import asyncio
    asyncio.run(test_property_5_message_round_trip())
    print("Test Property 5 passed manually")
