"""Property tests for Audio Service business logic."""

from unittest.mock import MagicMock

from hypothesis import given
from hypothesis import strategies as st

from backend.models.schemas import AudioMetadata
from backend.services.audio_service import AudioService, _AUDIO_STORE


@given(st.text(min_size=1))
def test_script_generation_correctness(knowledge_id: str):
    """**Feature: education-audio-page, Property 3: Script Generation API Call Correctness**
    
    Validates that the generate_script method correctly uses the knowledge_id
    to generate the script (or at least passes it through in the MVP).
    """
    service = AudioService()
    script = service.generate_script(knowledge_id=knowledge_id)
    
    # In our MVP implementation, the script should contain the knowledge_id
    assert knowledge_id in script


@given(
    st.text(min_size=1), # knowledge_id
    st.text(min_size=1), # script
    st.text(min_size=1), # voice_id
)
def test_audio_metadata_storage(knowledge_id: str, script: str, voice_id: str):
    """**Feature: education-audio-page, Property 9: Audio History Display**
    
    Validates that generated audio metadata is correctly stored and retrieved
    for the specific knowledge_id.
    """
    # Mock ElevenLabs service to avoid API calls
    mock_elevenlabs = MagicMock()
    mock_elevenlabs.text_to_speech.return_value = b"fake audio"
    
    service = AudioService(elevenlabs_service=mock_elevenlabs)
    
    # Clear store for isolation in property test (though hypothesis runs repeatedly)
    # Ideally use a fixture or instance-based store, but for global var MVP we clear it
    _AUDIO_STORE.clear()
    
    # Generate audio
    metadata = service.generate_audio(script=script, voice_id=voice_id, knowledge_id=knowledge_id)
    
    # Retrieve audio
    history = service.get_audio_files(knowledge_id=knowledge_id)
    
    assert len(history) == 1
    assert history[0] == metadata
    assert history[0].knowledge_id == knowledge_id
    assert history[0].voice_id == voice_id
    
    # Verify isolation
    other_history = service.get_audio_files(knowledge_id=knowledge_id + "_other")
    assert len(other_history) == 0
