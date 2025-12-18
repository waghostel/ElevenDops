"""Property tests for ElevenLabs Service."""

import pytest
from unittest.mock import MagicMock, patch
from backend.services.elevenlabs_service import ElevenLabsService, ElevenLabsSyncError, ElevenLabsDeleteError

# Using mocks for ElevenLabs service properties since we can't call real API in tests without cost/auth.

@pytest.mark.asyncio
async def test_sync_failure_handling():
    """
    **Feature: upload-knowledge-page, Property 6: Sync Failure Handling**
    Verifies that service raises appropriate error on client failure.
    """
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        # Setup mock to raise exception
        instance = MockClient.return_value
        # Mock add_to_knowledge_base raising exception
        instance.conversational_ai.add_to_knowledge_base.side_effect = Exception("API Error")
        
        service = ElevenLabsService()
        
        with pytest.raises(ElevenLabsSyncError):
            service.create_document("text", "name")

@pytest.mark.asyncio
async def test_sync_success():
    """
    **Feature: upload-knowledge-page, Property 5: Sync Workflow Integrity**
    Verifies that service returns ID on success.
    """
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        # Setup mock to return object with id
        instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.id = "el_doc_123"
        instance.conversational_ai.add_to_knowledge_base.return_value = mock_response
        
        service = ElevenLabsService()
        result_id = service.create_document("text", "name")
        
        assert result_id == "el_doc_123"

@pytest.mark.asyncio
async def test_delete_success():
    """
    **Feature: upload-knowledge-page, Property: Delete Workflow**
    Verifies that service calls delete_knowledge_base_document.
    """
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        instance = MockClient.return_value
        service = ElevenLabsService()
        
        result = service.delete_document("doc_id")
        
        assert result is True
        instance.conversational_ai.delete_knowledge_base_document.assert_called_once_with(document_id="doc_id")

@pytest.mark.asyncio
async def test_delete_failure():
    """
    **Feature: upload-knowledge-page, Property: Delete Failure**
    Verifies handling of deletion errors.
    """
    with patch("backend.services.elevenlabs_service.ElevenLabs") as MockClient:
        instance = MockClient.return_value
        instance.conversational_ai.delete_knowledge_base_document.side_effect = Exception("Delete Error")
        service = ElevenLabsService()
        
        with pytest.raises(ElevenLabsDeleteError):
            service.delete_document("doc_id")
