
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from tenacity import RetryError
from google.api_core.exceptions import GoogleAPICallError

# Import services
from backend.services.patient_service import PatientService
from backend.models.schemas import PatientSessionResponse
from backend.services.elevenlabs_service import ElevenLabsServiceError
from backend.services.firestore_data_service import FirestoreDataService

@pytest.mark.asyncio
async def test_tts_failure_graceful_degradation():
    """
    **Feature: error-handling, Task 6.1: TTS Failure Graceful Degradation**
    
    Validates that:
    1. PatientService catches ElevenLabs errors.
    2. Returns a fallback text response.
    3. Handles missing audio_data (None).
    """
    # Mock Data Service
    mock_data = AsyncMock()
    session = PatientSessionResponse(
        session_id="sess_1", patient_id="p1", agent_id="a1", signed_url="url", created_at=datetime.now()
    )
    mock_data.get_patient_session.return_value = session
    
    # Mock ElevenLabs Service to raise error
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.send_text_message = AsyncMock(side_effect=ElevenLabsServiceError("Simulated TTS Error"))
    
    service = PatientService(
        data_service=mock_data,
        elevenlabs_service=mock_elevenlabs,
        conversation_service=MagicMock()
    )
    
    response = await service.send_message("sess_1", "Hello")
    
    # Assertions
    assert response.audio_data is None
    assert "apologize" in response.response_text or "difficulties" in response.response_text
    
    # Verify session message was still logged (fallback text)
    mock_data.add_session_message.assert_called()
    calls = mock_data.add_session_message.call_args_list
    # Second call should be agent message
    agent_msg = calls[1].args[1]
    assert agent_msg.role == "agent"
    assert agent_msg.content == response.response_text
    assert agent_msg.audio_data is None


@pytest.mark.asyncio
async def test_firestore_retry_logic():
    """
    **Feature: error-handling, Task 6.2: Firestore Retry Logic**
    
    Validates that:
    1. Firestore methods retry on GoogleAPICallError.
    """
    # We need to mock the underlying firestore client to raise error
    with patch("backend.services.firestore_data_service.get_firestore_service") as mock_get_fs:
        mock_db = MagicMock()
        mock_fs_service = MagicMock()
        mock_fs_service.db = mock_db
        mock_get_fs.return_value = mock_fs_service
        
        # Reset singleton if possible, or create a fresh instance if __new__ allows
        # Since implementation uses singleton pattern, we might need to reset _instance
        FirestoreDataService._instance = None
        
        service = FirestoreDataService()
        
        mock_doc_ref = MagicMock()
        mock_doc_ref.set.side_effect = GoogleAPICallError("Transient Error")
        
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        from backend.models.schemas import AgentResponse, AnswerStyle
        agent = AgentResponse(
            agent_id="a1", name="n", knowledge_ids=[], voice_id="v", 
            answer_style=AnswerStyle.PROFESSIONAL, elevenlabs_agent_id="e", 
            doctor_id="d", created_at=datetime.now()
        )
        
        # Expect RetryError because tenacity wraps the exception after failing retries
        with pytest.raises(RetryError):
            await service.save_agent(agent)
            
        # Verify it was called multiple times (stop_after_attempt(3))
        assert mock_doc_ref.set.call_count >= 3
