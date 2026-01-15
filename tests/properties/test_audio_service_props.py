import pytest
import uuid
from datetime import datetime
from hypothesis import given, settings
import hypothesis.strategies as st
from unittest.mock import MagicMock, AsyncMock

from backend.services.audio_service import AudioService
from backend.models.schemas import AudioMetadata

# Strategies
script_strategy = st.text(min_size=10, max_size=1000)
voice_id_strategy = st.uuids().map(str)
knowledge_id_strategy = st.uuids().map(str)


@pytest.fixture
def mock_elevenlabs_service():
    service = MagicMock()
    service.text_to_speech.return_value = b"fake_audio_bytes"
    return service


@pytest.fixture
def mock_storage_service():
    service = MagicMock()
    service.upload_audio.return_value = "https://storage.googleapis.com/fake-bucket/audio/fake.mp3"
    service.get_audio_files.return_value = []
    return service


@pytest.fixture
def mock_data_service():
    service = AsyncMock()
    # Mock save_audio_metadata to return the passed metadata object
    service.save_audio_metadata.side_effect = lambda x: x
    service.get_audio_files.return_value = []
    return service


@pytest.mark.asyncio
# **Feature: elevenlabs-tts-audio, Property 1: Audio generation produces complete metadata**
# **Validates: Requirements 1.4**
@given(
    script=script_strategy,
    voice_id=voice_id_strategy,
    knowledge_id=knowledge_id_strategy
)

async def test_audio_generation_produces_complete_metadata(
    script, voice_id, knowledge_id
):
    # Setup mocks
    elevenlabs = MagicMock()
    elevenlabs.text_to_speech.return_value = b"audio_content"
    
    storage = MagicMock()
    storage.upload_audio.return_value = f"https://storage.example.com/audio/{uuid.uuid4()}.mp3"
    
    data = AsyncMock()
    data.save_audio_metadata.side_effect = lambda x: x
    
    service = AudioService(
        elevenlabs_service=elevenlabs,
        storage_service=storage,
        data_service=data
    )
    
    # Execute
    metadata = await service.generate_audio(script, voice_id, knowledge_id)
    
    # Verify
    assert metadata is not None
    assert metadata.script == script
    assert metadata.voice_id == voice_id
    assert metadata.knowledge_id == knowledge_id
    assert metadata.audio_url.startswith("https://")
    assert metadata.audio_id is not None
    assert metadata.created_at is not None
    
    # Verify dependencies called
    elevenlabs.text_to_speech.assert_called_once_with(text=script, voice_id=voice_id)
    storage.upload_audio.assert_called_once()
    data.save_audio_metadata.assert_called_once()
    
    # Check that called arg equals returned metadata
    saved_metadata = data.save_audio_metadata.call_args[0][0]
    assert saved_metadata == metadata


@pytest.mark.asyncio
# **Feature: elevenlabs-tts-audio, Property 7: Upload failure prevents metadata persistence**
# **Validates: Requirements 6.2**
@given(
    script=script_strategy,
    voice_id=voice_id_strategy,
    knowledge_id=knowledge_id_strategy
)
 
async def test_upload_failure_prevents_metadata_persistence(
    script, voice_id, knowledge_id
):
    # Setup mocks
    elevenlabs = MagicMock()
    elevenlabs.text_to_speech.return_value = b"audio_content"
    
    storage = MagicMock()
    # Simulate upload failure
    storage.upload_audio.side_effect = Exception("Upload failed")
    
    data = AsyncMock()
    
    service = AudioService(
        elevenlabs_service=elevenlabs,
        storage_service=storage,
        data_service=data
    )
    
    # Execute & Verify
    with pytest.raises(Exception, match="Upload failed"):
        await service.generate_audio(script, voice_id, knowledge_id)

    # Verify data service was NOT called
    data.save_audio_metadata.assert_not_called()


@pytest.mark.asyncio
# **Feature: elevenlabs-tts-audio, Property 5: Audio query by knowledge_id returns all matching records**
# **Validates: Requirements 3.4**
@given(
    knowledge_id=knowledge_id_strategy
)

async def test_audio_query_by_knowledge_id_returns_all_matching_records(
    knowledge_id
):
    # Setup mocks
    data = AsyncMock()
    expected_result = [
        AudioMetadata(
            audio_id=str(uuid.uuid4()),
            knowledge_id=knowledge_id,
            voice_id="v1",
            script="s1",
            audio_url="https://example.com/audio.mp3",
            duration_seconds=10.0,
            created_at=datetime.utcnow()
        )
    ]
    data.get_audio_files.return_value = expected_result
    
    service = AudioService(
        data_service=data,
        elevenlabs_service=MagicMock(),
        storage_service=MagicMock()
    )
    
    # Execute
    result = await service.get_audio_files(knowledge_id)
    
    # Verify
    assert result == expected_result
    data.get_audio_files.assert_called_once_with(knowledge_id=knowledge_id, doctor_id=None)


# **Feature: elevenlabs-tts-audio, Property 2: Voice list contains required fields**
# **Validates: Requirements 2.2**
@given(
    voices_data=st.lists(
        st.fixed_dictionaries({
            "voice_id": st.uuids().map(str),
            "name": st.text(min_size=1),
            "description": st.text(),
            "preview_url": st.text()
        }), min_size=0, max_size=5
    )
)

def test_voice_list_contains_required_fields(voices_data):
    # Setup
    elevenlabs = MagicMock()
    elevenlabs.get_voices.return_value = voices_data
    
    service = AudioService(
        elevenlabs_service=elevenlabs,
        storage_service=MagicMock(),
        data_service=AsyncMock()
    )
    
    # Execute
    result = service.get_available_voices()
    
    # Verify
    assert len(result) == len(voices_data)
    for i, voice in enumerate(result):
        assert voice.voice_id == voices_data[i]["voice_id"]
        assert voice.name == voices_data[i]["name"]
        assert voice.description == voices_data[i]["description"]
        assert voice.preview_url == voices_data[i]["preview_url"]


# **Feature: elevenlabs-tts-audio, Property 6: Script generation response structure**
# **Validates: Requirements 4.1, 4.2**
@given(
    knowledge_id=knowledge_id_strategy
)

@pytest.mark.asyncio
async def test_script_generation_response_structure(knowledge_id):
    # Setup
    data = AsyncMock()
    # Mock knowledge document
    # importing KnowledgeDocumentResponse helper might be complex due to validation, 
    # so we mock the object directly or use a simple mock with attributes
    mock_doc = MagicMock()
    mock_doc.disease_name = "Flu"
    mock_doc.raw_content = "Flu is common."
    mock_doc.structured_sections = {"Introduction": "Intro to Flu"}
    
    data.get_knowledge_document.return_value = mock_doc
    
    mock_script_service = AsyncMock()
    mock_script_service.generate_script.return_value = {
        "script": "Patient Education Script for Flu:\n\nIntro to Flu",
        "model_used": "test-model"
    }

    service = AudioService(
        data_service=data, 
        elevenlabs_service=MagicMock(), 
        storage_service=MagicMock(),
        script_service=mock_script_service
    )
    
    # Execute
    script = await service.generate_script(knowledge_id)
    
    # Verify
    assert isinstance(script, dict)
    assert "script" in script
    assert isinstance(script["script"], str)
    assert len(script["script"]) > 0
    assert "Flu" in script["script"]
    assert "Intro to Flu" in script["script"]
    
    data.get_knowledge_document.assert_called_once_with(knowledge_id)
    mock_script_service.generate_script.assert_called_once()

