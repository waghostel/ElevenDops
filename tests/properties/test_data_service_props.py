
import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from unittest.mock import MagicMock, AsyncMock, patch

from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import AudioMetadata
import uuid
from datetime import datetime

# Property 4: Audio metadata persistence round trip
# Validates: Requirements 3.3

@given(
    audio=st.builds(AudioMetadata,
        audio_id=st.uuids().map(str),
        knowledge_id=st.uuids().map(str),
        voice_id=st.text(min_size=1),
        script=st.text(min_size=1),
        audio_url=st.text(min_size=1),
        duration_seconds=st.floats(min_value=0.1, allow_nan=False, allow_infinity=False) | st.none(),
        created_at=st.datetimes()
    )
)

@pytest.mark.asyncio
async def test_audio_metadata_persistence_round_trip(audio):
    # Mock Firestore dependency
    with patch("backend.services.firestore_data_service.get_firestore_service") as mock_get_service:
        mock_db = MagicMock()
        mock_get_service.return_value.db = mock_db
        
        # Reset singleton if needed
        FirestoreDataService._instance = None
        service = FirestoreDataService()
        
        # Mock set return
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        
        # Execute Save
        saved = await service.save_audio_metadata(audio)
        
        # Verify Save
        assert saved == audio
        mock_db.collection.assert_called_with("audio_files")
        mock_doc_ref.set.assert_called_once()
        
        # Verify passed data matches
        call_args = mock_doc_ref.set.call_args[0][0]
        assert call_args["audio_id"] == audio.audio_id
        assert call_args["knowledge_id"] == audio.knowledge_id
        
        # Mock Get
        mock_snapshot = MagicMock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = audio.model_dump()
        mock_doc_ref.get.return_value = mock_snapshot
        
        # Execute Get
        retrieved = await service.get_audio_file(audio.audio_id)
        
        # Verify Get
        assert retrieved == audio
