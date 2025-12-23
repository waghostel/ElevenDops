import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from backend.main import app 
from backend.services.audio_service import get_audio_service

@pytest.fixture
def client():
    # Clear overrides before/after
    app.dependency_overrides = {}
    yield TestClient(app)
    app.dependency_overrides = {}

def test_document_validation_404(client):
    """Property 6: Document Validation.
    Ensure 404 is returned when document is not found.
    """
    mock_service = AsyncMock()
    mock_service.generate_script.side_effect = ValueError("Knowledge document not found")
    
    app.dependency_overrides[get_audio_service] = lambda: mock_service
    
    response = client.post(
        "/api/audio/generate-script",
        json={"knowledge_id": "non_existent_id"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "").lower()

def test_generate_script_success(client):
    """Test successful script generation API call."""
    mock_service = AsyncMock()
    mock_service.generate_script.return_value = {
        "script": "Generated script",
        "model_used": "gemini-2.5-flash"
    }
    
    app.dependency_overrides[get_audio_service] = lambda: mock_service
    
    response = client.post(
        "/api/audio/generate-script",
        json={
            "knowledge_id": "doc_123",
            "model_name": "gemini-2.5-flash",
            "custom_prompt": "Prompt"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["script"] == "Generated script"
    assert data["model_used"] == "gemini-2.5-flash"
    assert data["knowledge_id"] == "doc_123"
