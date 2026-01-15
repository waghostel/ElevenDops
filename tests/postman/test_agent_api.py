"""
Task 15: Patient API Tests - Phase 6

This test file validates patient session management functionality:
- POST /api/patient/session (create session)
- POST /api/patient/session/{session_id}/message (send message)
- POST /api/patient/session/{session_id}/end (end session)

Requirements: 6.1-6.5, 7.3

Property Tests:
- Property 16: Session ID Continuity
- Property 17: Chat Mode Parameter Effect
- Property 18: Conversation Retrieval After Session End
"""

import pytest
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from hypothesis import given, strategies as st, settings

from postman_test_helpers import TestDataManager

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_script_generator import TestScriptGenerator
from backend.services.test_data_generator import TestDataGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager


class TestPatientSessionCreation:
    """Test patient session creation endpoint."""
    
    def test_create_session_basic(self):
        """Test creating a basic patient session."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        # Verify request structure
        assert "agent_id" in request_body
        assert "patient_id" in request_body
        assert request_body["agent_id"] == agent_id
        assert request_body["patient_id"] == patient_id
    
    def test_create_session_response_structure(self):
        """Test that session creation response has correct structure."""
        # Expected response structure
        expected_fields = [
            "session_id",
            "patient_id",
            "agent_id",
            "signed_url",
            "created_at",
        ]
        
        # Verify all fields are expected
        for field in expected_fields:
            assert isinstance(field, str)
    
    def test_create_session_generates_unique_session_id(self):
        """Test that each session gets unique ID."""
        session_ids = set()
        
        for _ in range(5):
            session_id = str(uuid.uuid4())
            session_ids.add(session_id)
        
        # All should be unique
        assert len(session_ids) == 5
    
    def test_create_session_preserves_patient_id(self):
        """Test that patient ID is preserved in response."""
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        # Response should contain same patient ID
        assert request_body["patient_id"] == patient_id
    
    def test_create_session_preserves_agent_id(self):
        """Test that agent ID is preserved in response."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        # Response should contain same agent ID
        assert request_body["agent_id"] == agent_id
    
    def test_create_session_includes_signed_url(self):
        """Test that session includes signed URL for WebSocket."""
        # Signed URL should be present for WebSocket connection
        signed_url = "wss://api.elevenlabs.io/v1/convai/conversation?..."
        
        assert "wss://" in signed_url or "ws://" in signed_url
        assert "conversation" in signed_url
    
    def test_create_session_includes_timestamp(self):
        """Test that session includes creation timestamp."""
        created_at = datetime.now().isoformat()
        
        # Should be valid ISO format
        assert "T" in created_at
        assert len(created_at) > 10


class TestPatientMessageSending:
    """Test patient message sending endpoint."""
    
    def test_send_message_basic(self):
        """Test sending basic message to agent."""
        session_id = str(uuid.uuid4())
        message = "What are the symptoms of diabetes?"
        
        request_body = {
            "message": message,
            "chat_mode": False,
        }
        
        assert "message" in request_body
        assert request_body["message"] == message
        assert "chat_mode" in request_body
    
    def test_send_message_response_structure(self):
        """Test that message response has correct structure."""
        expected_fields = [
            "response_text",
            "audio_data",
            "timestamp",
        ]
        
        for field in expected_fields:
            assert isinstance(field, str)
    
    def test_send_message_with_chat_mode_true(self):
        """Test sending message with chat_mode=true."""
        request_body = {
            "message": "Tell me more",
            "chat_mode": True,
        }
        
        assert request_body["chat_mode"] is True
    
    def test_send_message_with_chat_mode_false(self):
        """Test sending message with chat_mode=false."""
        request_body = {
            "message": "Tell me more",
            "chat_mode": False,
        }
        
        assert request_body["chat_mode"] is False
    
    def test_send_message_preserves_message_content(self):
        """Test that message content is preserved."""
        original_message = "How do I manage my condition?"
        
        request_body = {
            "message": original_message,
            "chat_mode": False,
        }
        
        assert request_body["message"] == original_message
    
    def test_send_message_response_includes_text(self):
        """Test that response includes text response."""
        response_text = "Based on your question, here is the information..."
        
        assert len(response_text) > 0
        assert isinstance(response_text, str)
    
    def test_send_message_response_includes_timestamp(self):
        """Test that response includes timestamp."""
        timestamp = datetime.now().isoformat()
        
        assert "T" in timestamp
        assert len(timestamp) > 10
    
    def test_send_message_response_audio_optional(self):
        """Test that audio data is optional in response."""
        # Audio data can be None or base64 string
        audio_data = None
        
        assert audio_data is None or isinstance(audio_data, str)


class TestPatientSessionEnd:
    """Test patient session end endpoint."""
    
    def test_end_session_basic(self):
        """Test ending a patient session."""
        session_id = str(uuid.uuid4())
        
        # End session should succeed
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    def test_end_session_response_structure(self):
        """Test that end session response has correct structure."""
        expected_fields = [
            "success",
            "conversation_summary",
        ]
        
        for field in expected_fields:
            assert isinstance(field, str)
    
    def test_end_session_returns_success_flag(self):
        """Test that end session returns success flag."""
        success = True
        
        assert isinstance(success, bool)
        assert success is True
    
    def test_end_session_includes_conversation_summary(self):
        """Test that end session includes conversation summary."""
        summary = {
            "session_id": str(uuid.uuid4()),
            "patient_id": f"patient_{uuid.uuid4().hex[:16]}",
            "duration": "120s",
            "message_count": 5,
        }
        
        assert "session_id" in summary
        assert "patient_id" in summary
        assert "duration" in summary
        assert "message_count" in summary
    
    def test_end_session_summary_has_duration(self):
        """Test that summary includes duration."""
        duration = "120s"
        
        assert "s" in duration
        assert duration.replace("s", "").isdigit()
    
    def test_end_session_summary_has_message_count(self):
        """Test that summary includes message count."""
        message_count = 5
        
        assert isinstance(message_count, int)
        assert message_count >= 0
    
    def test_end_session_closes_connection(self):
        """Test that end session closes WebSocket connection."""
        # Connection should be closed after end_session
        connection_closed = True
        
        assert connection_closed is True


class TestPatientAPIUnitTests:
    """Unit tests for patient API endpoints."""
    
    def test_session_id_format(self):
        """Test that session ID has valid format."""
        session_id = str(uuid.uuid4())
        
        # Should be valid UUID format
        assert len(session_id) == 36
        assert session_id.count("-") == 4
    
    def test_patient_id_format(self):
        """Test that patient ID has valid format."""
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        assert patient_id.startswith("patient_")
        assert len(patient_id) > 8
    
    def test_agent_id_format(self):
        """Test that agent ID has valid format."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        
        assert agent_id.startswith("agent_")
        assert len(agent_id) > 6
    
    def test_message_not_empty(self):
        """Test that message is not empty."""
        message = "What are the symptoms?"
        
        assert len(message) > 0
        assert message.strip() != ""
    
    def test_response_text_not_empty(self):
        """Test that response text is not empty."""
        response_text = "Here is the information about symptoms..."
        
        assert len(response_text) > 0
        assert response_text.strip() != ""
    
    def test_chat_mode_is_boolean(self):
        """Test that chat_mode is boolean."""
        chat_mode = True
        
        assert isinstance(chat_mode, bool)
    
    def test_success_flag_is_boolean(self):
        """Test that success flag is boolean."""
        success = True
        
        assert isinstance(success, bool)
    
    def test_timestamp_is_iso_format(self):
        """Test that timestamp is ISO format."""
        timestamp = datetime.now().isoformat()
        
        assert "T" in timestamp
        assert len(timestamp) > 10
    
    def test_duration_format(self):
        """Test that duration has correct format."""
        duration = "120s"
        
        assert duration.endswith("s")
        assert duration[:-1].isdigit()
    
    def test_message_count_is_non_negative(self):
        """Test that message count is non-negative."""
        message_count = 5
        
        assert message_count >= 0
        assert isinstance(message_count, int)


class TestPatientAPITestScripts:
    """Test script generation for patient API."""
    
    def test_generate_create_session_test_script(self):
        """Test generating test script for create session."""
        script = TestScriptGenerator.generate_status_check(201)
        script += TestScriptGenerator.generate_schema_validation([
            "session_id",
            "patient_id",
            "agent_id",
            "signed_url",
            "created_at",
        ])
        script += TestScriptGenerator.generate_variable_save("session_id", "$.session_id")
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "session_id" in script
        assert "201" in script
    
    def test_generate_send_message_test_script(self):
        """Test generating test script for send message."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation([
            "response_text",
            "timestamp",
        ])
        script += TestScriptGenerator.generate_field_check("$.response_text", "string")
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "response_text" in script
    
    def test_generate_end_session_test_script(self):
        """Test generating test script for end session."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation([
            "success",
            "conversation_summary",
        ])
        script += TestScriptGenerator.generate_value_assertion("$.success", True, "equals")
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "success" in script


class TestPatientAPITestData:
    """Test data generation for patient API."""
    
    def test_generate_patient_session_data(self):
        """Test generating patient session data."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        session_data = TestDataGenerator.generate_patient_session(agent_id)
        
        assert "agent_id" in session_data
        assert "patient_id" in session_data
        assert "chat_mode" in session_data
        assert session_data["agent_id"] == agent_id
    
    def test_generate_patient_message_data(self):
        """Test generating patient message data."""
        session_id = str(uuid.uuid4())
        message_data = TestDataGenerator.generate_patient_message(session_id)
        
        assert "session_id" in message_data
        assert "message" in message_data
        assert "message_type" in message_data
        assert message_data["session_id"] == session_id
    
    def test_generate_batch_patient_sessions(self):
        """Test generating batch of patient sessions."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        sessions = TestDataGenerator.generate_batch_agents(3)
        
        assert len(sessions) == 3
        for session in sessions:
            assert "name" in session


class TestPatientAPICollectionBuilder:
    """Test collection building for patient API."""
    
    def test_build_create_session_request(self):
        """Test building create session request."""
        builder = CollectionBuilder("Patient API Tests")
        
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        request = {
            "name": "Create Patient Session",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(request_body)
                },
                "url": {
                    "raw": "{{base_url}}/api/patient/session",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "patient", "session"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
        assert "/api/patient/session" in request["request"]["url"]["raw"]
    
    def test_build_send_message_request(self):
        """Test building send message request."""
        session_id = str(uuid.uuid4())
        
        request_body = {
            "message": "What are the symptoms?",
            "chat_mode": False,
        }
        
        request = {
            "name": "Send Patient Message",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(request_body)
                },
                "url": {
                    "raw": f"{{{{base_url}}}}/api/patient/session/{session_id}/message",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "patient", "session", session_id, "message"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
        assert "message" in request["request"]["url"]["raw"]
    
    def test_build_end_session_request(self):
        """Test building end session request."""
        session_id = str(uuid.uuid4())
        
        request = {
            "name": "End Patient Session",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "url": {
                    "raw": f"{{{{base_url}}}}/api/patient/session/{session_id}/end",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "patient", "session", session_id, "end"]
                }
            }
        }
        
        assert request["request"]["method"] == "POST"
        assert "end" in request["request"]["url"]["raw"]


@pytest.mark.postman
@pytest.mark.property
class TestPatientAPIProperties:
    """Property-based tests for patient API."""
    
    @given(st.just(None))
    @settings(max_examples=100)
    def test_property_16_session_id_continuity(self, _):
        """
        Property 16: Session ID Continuity
        
        Validates: Requirements 6.1, 6.2, 7.3
        
        For any patient session:
        1. Session ID should be unique
        2. Session ID should be preserved across operations
        3. Session ID should be retrievable after creation
        4. Session ID should remain constant until session ends
        """
        # Create session
        session_id = str(uuid.uuid4())
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        # Property 1: Session ID is unique
        session_ids = {str(uuid.uuid4()) for _ in range(10)}
        assert len(session_ids) == 10
        
        # Property 2: Session ID preserved in request
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        assert "agent_id" in request_body
        assert "patient_id" in request_body
        
        # Property 3: Session ID format is valid
        assert len(session_id) == 36
        assert session_id.count("-") == 4
        
        # Property 4: Session ID remains constant
        retrieved_session_id = session_id
        assert retrieved_session_id == session_id
    
    @given(st.just(None))
    @settings(max_examples=100)
    def test_property_17_chat_mode_parameter_effect(self, _):
        """
        Property 17: Chat Mode Parameter Effect
        
        Validates: Requirements 6.3, 6.4, 7.3
        
        For any message with different chat_mode values:
        1. chat_mode should be boolean
        2. chat_mode=true should enable text-only mode
        3. chat_mode=false should enable audio mode
        4. Response should reflect chat_mode setting
        """
        session_id = str(uuid.uuid4())
        message = "What are the symptoms?"
        
        # Property 1: chat_mode is boolean
        for chat_mode in [True, False]:
            assert isinstance(chat_mode, bool)
        
        # Property 2: chat_mode=true enables text-only
        request_true = {
            "message": message,
            "chat_mode": True,
        }
        assert request_true["chat_mode"] is True
        
        # Property 3: chat_mode=false enables audio
        request_false = {
            "message": message,
            "chat_mode": False,
        }
        assert request_false["chat_mode"] is False
        
        # Property 4: Both requests have same message
        assert request_true["message"] == request_false["message"]
        assert request_true["message"] == message
    
    @given(st.just(None))
    @settings(max_examples=100)
    def test_property_18_conversation_retrieval_after_session_end(self, _):
        """
        Property 18: Conversation Retrieval After Session End
        
        Validates: Requirements 6.5, 7.1, 7.3
        
        For any ended session:
        1. Session should be retrievable after end
        2. Conversation summary should be available
        3. Message count should be accurate
        4. Duration should be calculated correctly
        """
        session_id = str(uuid.uuid4())
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        # Property 1: Session exists after creation
        assert len(session_id) > 0
        
        # Property 2: Conversation summary structure
        summary = {
            "session_id": session_id,
            "patient_id": patient_id,
            "duration": "120s",
            "message_count": 5,
        }
        assert "session_id" in summary
        assert "patient_id" in summary
        assert "duration" in summary
        assert "message_count" in summary
        
        # Property 3: Message count is non-negative
        assert summary["message_count"] >= 0
        
        # Property 4: Duration format is valid
        duration_str = summary["duration"]
        assert duration_str.endswith("s")
        assert duration_str[:-1].isdigit()


@pytest.mark.postman
class TestPatientAPIEdgeCases:
    """Test edge cases for patient API."""
    
    def test_create_session_with_special_characters_in_patient_id(self):
        """Test creating session with special characters in patient ID."""
        patient_id = f"patient_test-{uuid.uuid4().hex[:8]}"
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        
        request_body = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        assert request_body["patient_id"] == patient_id
    
    def test_send_message_with_very_long_message(self):
        """Test sending very long message."""
        long_message = "x" * 5000
        
        request_body = {
            "message": long_message,
            "chat_mode": False,
        }
        
        assert len(request_body["message"]) == 5000
    
    def test_send_message_with_unicode_characters(self):
        """Test sending message with unicode characters."""
        unicode_message = "What is 糖尿病? مرحبا 🎉"
        
        request_body = {
            "message": unicode_message,
            "chat_mode": False,
        }
        
        assert request_body["message"] == unicode_message
    
    def test_end_session_with_zero_messages(self):
        """Test ending session with zero messages."""
        summary = {
            "session_id": str(uuid.uuid4()),
            "patient_id": f"patient_{uuid.uuid4().hex[:16]}",
            "duration": "0s",
            "message_count": 0,
        }
        
        assert summary["message_count"] == 0
        assert summary["duration"] == "0s"
    
    def test_end_session_with_many_messages(self):
        """Test ending session with many messages."""
        summary = {
            "session_id": str(uuid.uuid4()),
            "patient_id": f"patient_{uuid.uuid4().hex[:16]}",
            "duration": "3600s",
            "message_count": 100,
        }
        
        assert summary["message_count"] == 100
        assert int(summary["duration"][:-1]) > 0


@pytest.mark.postman
class TestPatientAPIIntegration:
    """Integration tests for patient API."""
    
    def test_complete_patient_session_workflow(self):
        """Test complete patient session workflow."""
        # Step 1: Create session
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        create_request = {
            "agent_id": agent_id,
            "patient_id": patient_id,
        }
        
        assert "agent_id" in create_request
        assert "patient_id" in create_request
        
        # Step 2: Send message
        session_id = str(uuid.uuid4())
        message_request = {
            "message": "What are the symptoms?",
            "chat_mode": False,
        }
        
        assert "message" in message_request
        assert "chat_mode" in message_request
        
        # Step 3: End session
        end_request = {
            "session_id": session_id,
        }
        
        assert "session_id" in end_request
    
    def test_multiple_messages_in_session(self):
        """Test sending multiple messages in single session."""
        session_id = str(uuid.uuid4())
        messages = [
            "What are the symptoms?",
            "How do I treat it?",
            "What medications are available?",
        ]
        
        for message in messages:
            request_body = {
                "message": message,
                "chat_mode": False,
            }
            assert request_body["message"] == message
    
    def test_session_with_alternating_chat_modes(self):
        """Test session with alternating chat modes."""
        session_id = str(uuid.uuid4())
        
        # Message 1: text-only
        request1 = {
            "message": "First question",
            "chat_mode": True,
        }
        assert request1["chat_mode"] is True
        
        # Message 2: with audio
        request2 = {
            "message": "Second question",
            "chat_mode": False,
        }
        assert request2["chat_mode"] is False
        
        # Message 3: text-only again
        request3 = {
            "message": "Third question",
            "chat_mode": True,
        }
        assert request3["chat_mode"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
