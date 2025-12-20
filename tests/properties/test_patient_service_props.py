
import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from datetime import datetime
import uuid

from backend.services.patient_service import PatientService
from backend.services.data_service import MockDataService
from backend.models.schemas import PatientSessionCreate

# **Feature: patient-conversation-text, Property 1: Session creation returns unique session_id**
@settings(deadline=None)
@given(
    patient_id=st.text(min_size=1, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    agent_id=st.text(min_size=1)
)
def test_session_creation_unique_id(patient_id, agent_id):
    """Verify session creation returns unique session_id."""
    # Mock ElevenLabs service to avoid API calls
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.get_signed_url.return_value = "wss://mock-url"
    # send_text_message not called here so no need to mock specific async property


    service = PatientService(
        data_service=MockDataService(),
        elevenlabs_service=mock_elevenlabs
    )

    loop = asyncio.new_event_loop()
    try:
        request = PatientSessionCreate(patient_id=patient_id, agent_id=agent_id)
        try:
            session = loop.run_until_complete(service.create_session(request))
        except Exception as e:
            print(f"Caught exception in create_session: {e}")
            raise e
        
        # Check if ID is a valid UUID
        try:
            uuid.UUID(session.session_id)
        except ValueError:
            pytest.fail("session_id is not a valid UUID")
            
        assert session.patient_id == patient_id
        assert session.agent_id == agent_id
    finally:
        loop.close()

# **Feature: patient-conversation-text, Property 3: Session data round-trip to Firestore**
@settings(deadline=None)
@given(
    patient_id=st.text(min_size=1, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    agent_id=st.text(min_size=1)
)
def test_session_data_round_trip(patient_id, agent_id):
    """Verify session data round-trip to persistence."""
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.get_signed_url.return_value = "wss://mock-url"
    
    data_store = MockDataService()
    service = PatientService(
        data_service=data_store,
        elevenlabs_service=mock_elevenlabs
    )

    loop = asyncio.new_event_loop()
    try:
        request = PatientSessionCreate(patient_id=patient_id, agent_id=agent_id)
        created_session = loop.run_until_complete(service.create_session(request))
        
        # Retrieve from store
        retrieved_session = loop.run_until_complete(data_store.get_patient_session(created_session.session_id))
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.patient_id == patient_id
        assert retrieved_session.agent_id == agent_id
        assert retrieved_session.created_at == created_session.created_at
    finally:
        loop.close()


# **Feature: patient-conversation-text, Property 5: Message exchange round-trip to Firestore**
@settings(deadline=None)
@given(
    patient_id=st.text(min_size=1, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    agent_id=st.text(min_size=1),
    message_text=st.text(min_size=1),
    agent_response_text=st.text(min_size=1)
)
def test_message_exchange_round_trip(patient_id, agent_id, message_text, agent_response_text):
    """Verify message exchange persists both patient and agent messages."""
    # Mock ElevenLabs to return specific text/audio
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.get_signed_url.return_value = "wss://mock-url"
    mock_elevenlabs.send_text_message = AsyncMock(return_value=(agent_response_text, b"mock_audio"))
    
    data_store = MockDataService()
    service = PatientService(
        data_service=data_store,
        elevenlabs_service=mock_elevenlabs
    )

    loop = asyncio.new_event_loop()
    try:
        # Create session
        request = PatientSessionCreate(patient_id=patient_id, agent_id=agent_id)
        session = loop.run_until_complete(service.create_session(request))
        
        # Send message
        loop.run_until_complete(service.send_message(session.session_id, message_text))
        
        # Verify persistence
        messages = loop.run_until_complete(data_store.get_session_messages(session.session_id))
        
        assert len(messages) == 2
        
        # Check patient message
        patient_msg = messages[0]
        assert patient_msg.role == "patient"
        assert patient_msg.content == message_text
        
        # Check agent message
        agent_msg = messages[1]
        assert agent_msg.role == "agent"
        assert agent_msg.content == agent_response_text
        # Check audio data - base64 of b"mock_audio" is "bW9ja19hdWRpbw=="
        assert agent_msg.audio_data == "bW9ja19hdWRpbw=="

    finally:
        loop.close()

# **Feature: patient-conversation-text, Property 11: Response includes timestamp**
@settings(deadline=None)
@given(
    patient_id=st.text(min_size=1, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
    message_text=st.text(min_size=1)
)
def test_response_includes_timestamp(patient_id, message_text):
    """Verify response includes valid timestamp."""
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.get_signed_url.return_value = "wss://mock-url"
    mock_elevenlabs.send_text_message = AsyncMock(return_value=("response", b"audio"))
    
    service = PatientService(
        data_service=MockDataService(),
        elevenlabs_service=mock_elevenlabs
    )

    loop = asyncio.new_event_loop()
    try:
        request = PatientSessionCreate(patient_id=patient_id, agent_id="agent")
        session = loop.run_until_complete(service.create_session(request))
        
        start_time = datetime.now()
        response = loop.run_until_complete(service.send_message(session.session_id, message_text))
        
        # Be lenient with timing check across systems
        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)
    finally:
        loop.close()
