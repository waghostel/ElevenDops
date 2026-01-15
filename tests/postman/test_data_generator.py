"""
Task 8: Test Data Generator Component Tests

This test file validates test data generation functionality:
- TestDataGenerator class implementation
- Knowledge document generation
- Audio request generation
- Agent configuration generation
- Patient session generation
- Template generation
- Unit tests for all generator methods
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List

from postman_test_helpers import TestDataManager

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_data_generator import TestDataGenerator


class TestKnowledgeDocumentGeneration:
    """Test knowledge document generation."""
    
    def test_generate_knowledge_document_basic(self):
        """Test generating basic knowledge document."""
        doc = TestDataGenerator.generate_knowledge_document()
        
        assert "disease_name" in doc
        assert "tags" in doc
        assert "raw_content" in doc
        assert "doctor_id" in doc
        assert "name" in doc
        assert "description" in doc
    
    def test_generate_knowledge_document_structure(self):
        """Test knowledge document has correct structure."""
        doc = TestDataGenerator.generate_knowledge_document()
        
        assert isinstance(doc["disease_name"], str)
        assert isinstance(doc["tags"], list)
        assert isinstance(doc["raw_content"], str)
        assert len(doc["tags"]) >= 2
        assert len(doc["raw_content"]) > 0
    
    def test_generate_knowledge_document_with_structured_sections(self):
        """Test generating knowledge document with structured sections."""
        doc = TestDataGenerator.generate_knowledge_document(
            include_structured_sections=True
        )
        
        assert "structured_sections" in doc
        assert isinstance(doc["structured_sections"], list)
        assert len(doc["structured_sections"]) > 0
    
    def test_generate_knowledge_document_without_structured_sections(self):
        """Test generating knowledge document without structured sections."""
        doc = TestDataGenerator.generate_knowledge_document(
            include_structured_sections=False
        )
        
        assert "structured_sections" not in doc
    
    def test_generate_knowledge_document_custom_doctor_id(self):
        """Test generating knowledge document with custom doctor ID."""
        doctor_id = "custom_doctor_123"
        doc = TestDataGenerator.generate_knowledge_document(doctor_id=doctor_id)
        
        assert doc["doctor_id"] == doctor_id
    
    def test_generate_knowledge_document_uniqueness(self):
        """Test that generated documents are unique."""
        doc1 = TestDataGenerator.generate_knowledge_document()
        doc2 = TestDataGenerator.generate_knowledge_document()
        
        # Names should be different
        assert doc1["name"] != doc2["name"]
    
    def test_generate_knowledge_document_content_quality(self):
        """Test that generated content has good quality."""
        doc = TestDataGenerator.generate_knowledge_document()
        
        # Should have markdown sections
        assert "#" in doc["raw_content"]
        # Should have multiple paragraphs
        assert "\n" in doc["raw_content"]
        # Should be substantial
        assert len(doc["raw_content"]) > 200


class TestAudioRequestGeneration:
    """Test audio request generation."""
    
    def test_generate_audio_request_basic(self):
        """Test generating basic audio request."""
        knowledge_id = "knowledge_123"
        request = TestDataGenerator.generate_audio_request(knowledge_id)
        
        assert "script" in request
        assert "voice_id" in request
        assert "knowledge_id" in request
        assert "doctor_id" in request
        assert "name" in request
        assert "description" in request
    
    def test_generate_audio_request_structure(self):
        """Test audio request has correct structure."""
        request = TestDataGenerator.generate_audio_request("knowledge_123")
        
        assert isinstance(request["script"], str)
        assert isinstance(request["voice_id"], str)
        assert request["knowledge_id"] == "knowledge_123"
        assert isinstance(request["name"], str)
        assert len(request["script"]) > 0
    
    def test_generate_audio_request_voice_id_valid(self):
        """Test that generated voice ID is valid."""
        request = TestDataGenerator.generate_audio_request("knowledge_123")
        
        # Voice ID should be from predefined list
        assert request["voice_id"] in TestDataGenerator.VOICE_IDS
    
    def test_generate_audio_request_custom_doctor_id(self):
        """Test generating audio request with custom doctor ID."""
        doctor_id = "custom_doctor_456"
        request = TestDataGenerator.generate_audio_request(
            "knowledge_123",
            doctor_id=doctor_id
        )
        
        assert request["doctor_id"] == doctor_id
    
    def test_generate_audio_request_has_metadata(self):
        """Test that audio request has metadata fields."""
        request = TestDataGenerator.generate_audio_request("knowledge_123")
        
        assert "language" in request
        assert "model_id" in request
        assert request["language"] == "en-US"


class TestAgentConfigGeneration:
    """Test agent configuration generation."""
    
    def test_generate_agent_config_basic(self):
        """Test generating basic agent config."""
        config = TestDataGenerator.generate_agent_config()
        
        assert "name" in config
        assert "description" in config
        assert "knowledge_ids" in config
        assert "doctor_id" in config
        assert "system_prompt_style" in config
        assert "voice_id" in config
    
    def test_generate_agent_config_structure(self):
        """Test agent config has correct structure."""
        config = TestDataGenerator.generate_agent_config()
        
        assert isinstance(config["name"], str)
        assert isinstance(config["knowledge_ids"], list)
        assert len(config["knowledge_ids"]) > 0
        assert isinstance(config["system_prompt_style"], str)
        assert isinstance(config["temperature"], float)
    
    def test_generate_agent_config_with_knowledge_ids(self):
        """Test generating agent config with specific knowledge IDs."""
        knowledge_ids = ["knowledge_1", "knowledge_2", "knowledge_3"]
        config = TestDataGenerator.generate_agent_config(knowledge_ids=knowledge_ids)
        
        assert config["knowledge_ids"] == knowledge_ids
    
    def test_generate_agent_config_system_prompt_valid(self):
        """Test that system prompt style is valid."""
        config = TestDataGenerator.generate_agent_config()
        
        assert config["system_prompt_style"] in TestDataGenerator.SYSTEM_PROMPTS
    
    def test_generate_agent_config_temperature_range(self):
        """Test that temperature is in valid range."""
        config = TestDataGenerator.generate_agent_config()
        
        assert 0.5 <= config["temperature"] <= 1.0
    
    def test_generate_agent_config_max_tokens_valid(self):
        """Test that max tokens is valid."""
        config = TestDataGenerator.generate_agent_config()
        
        assert config["max_tokens"] in [256, 512, 1024]
    
    def test_generate_agent_config_enabled(self):
        """Test that agent is enabled by default."""
        config = TestDataGenerator.generate_agent_config()
        
        assert config["enabled"] is True


class TestPatientSessionGeneration:
    """Test patient session generation."""
    
    def test_generate_patient_session_basic(self):
        """Test generating basic patient session."""
        agent_id = "agent_123"
        session = TestDataGenerator.generate_patient_session(agent_id)
        
        assert "agent_id" in session
        assert "patient_id" in session
        assert "chat_mode" in session
        assert "language" in session
        assert "metadata" in session
    
    def test_generate_patient_session_structure(self):
        """Test patient session has correct structure."""
        session = TestDataGenerator.generate_patient_session("agent_123")
        
        assert session["agent_id"] == "agent_123"
        assert isinstance(session["patient_id"], str)
        assert session["chat_mode"] in ["streaming", "non-streaming"]
        assert session["language"] == "en-US"
    
    def test_generate_patient_session_custom_patient_id(self):
        """Test generating session with custom patient ID."""
        patient_id = "patient_custom_123"
        session = TestDataGenerator.generate_patient_session(
            "agent_123",
            patient_id=patient_id
        )
        
        assert session["patient_id"] == patient_id
    
    def test_generate_patient_session_metadata(self):
        """Test that session has metadata."""
        session = TestDataGenerator.generate_patient_session("agent_123")
        
        assert "session_type" in session["metadata"]
        assert "created_by" in session["metadata"]
        assert session["metadata"]["session_type"] == "test"
    
    def test_generate_patient_session_uniqueness(self):
        """Test that generated sessions are unique."""
        session1 = TestDataGenerator.generate_patient_session("agent_123")
        session2 = TestDataGenerator.generate_patient_session("agent_123")
        
        # Patient IDs should be different
        assert session1["patient_id"] != session2["patient_id"]


class TestPatientMessageGeneration:
    """Test patient message generation."""
    
    def test_generate_patient_message_basic(self):
        """Test generating basic patient message."""
        session_id = "session_123"
        message = TestDataGenerator.generate_patient_message(session_id)
        
        assert "session_id" in message
        assert "message" in message
        assert "message_type" in message
        assert "timestamp" in message
    
    def test_generate_patient_message_structure(self):
        """Test patient message has correct structure."""
        message = TestDataGenerator.generate_patient_message("session_123")
        
        assert message["session_id"] == "session_123"
        assert isinstance(message["message"], str)
        assert message["message_type"] in ["text", "audio"]
        assert len(message["message"]) > 0
    
    def test_generate_patient_message_custom_type(self):
        """Test generating message with custom type."""
        message = TestDataGenerator.generate_patient_message(
            "session_123",
            message_type="audio"
        )
        
        assert message["message_type"] == "audio"
    
    def test_generate_patient_message_has_timestamp(self):
        """Test that message has valid timestamp."""
        message = TestDataGenerator.generate_patient_message("session_123")
        
        assert "T" in message["timestamp"]  # ISO format
        # Timestamp should be in ISO format (YYYY-MM-DDTHH:MM:SS.ffffff)
        assert len(message["timestamp"]) > 10


class TestTemplateGeneration:
    """Test template generation."""
    
    def test_generate_template_basic(self):
        """Test generating basic template."""
        template = TestDataGenerator.generate_template()
        
        assert "name" in template
        assert "description" in template
        assert "content" in template
        assert "doctor_id" in template
        assert "is_system" in template
        assert "variables" in template
        assert "style" in template
    
    def test_generate_template_structure(self):
        """Test template has correct structure."""
        template = TestDataGenerator.generate_template()
        
        assert isinstance(template["name"], str)
        assert isinstance(template["content"], str)
        assert isinstance(template["variables"], list)
        assert template["is_system"] is False
        assert template["doctor_id"] is not None
    
    def test_generate_template_system_template(self):
        """Test generating system template."""
        template = TestDataGenerator.generate_template(is_system=True)
        
        assert template["is_system"] is True
        assert template["doctor_id"] is None
    
    def test_generate_template_custom_doctor_id(self):
        """Test generating template with custom doctor ID."""
        doctor_id = "doctor_custom_789"
        template = TestDataGenerator.generate_template(doctor_id=doctor_id)
        
        assert template["doctor_id"] == doctor_id
    
    def test_generate_template_style_valid(self):
        """Test that template style is valid."""
        template = TestDataGenerator.generate_template()
        
        assert template["style"] in TestDataGenerator.SYSTEM_PROMPTS
    
    def test_generate_template_content_quality(self):
        """Test that template content is substantial."""
        template = TestDataGenerator.generate_template()
        
        assert len(template["content"]) > 100
        assert "{" in template["content"]  # Has placeholders


class TestConversationGeneration:
    """Test conversation generation."""
    
    def test_generate_conversation_basic(self):
        """Test generating basic conversation."""
        session_id = "session_123"
        conversation = TestDataGenerator.generate_conversation(session_id)
        
        assert "session_id" in conversation
        assert "messages" in conversation
        assert "started_at" in conversation
        assert "ended_at" in conversation
        assert "duration_seconds" in conversation
        assert "message_count" in conversation
        assert "analysis" in conversation
    
    def test_generate_conversation_structure(self):
        """Test conversation has correct structure."""
        conversation = TestDataGenerator.generate_conversation("session_123")
        
        assert conversation["session_id"] == "session_123"
        assert isinstance(conversation["messages"], list)
        assert len(conversation["messages"]) > 0
        assert isinstance(conversation["message_count"], int)
    
    def test_generate_conversation_custom_message_count(self):
        """Test generating conversation with custom message count."""
        conversation = TestDataGenerator.generate_conversation(
            "session_123",
            message_count=5
        )
        
        assert len(conversation["messages"]) == 5
        assert conversation["message_count"] == 5
    
    def test_generate_conversation_message_structure(self):
        """Test that messages have correct structure."""
        conversation = TestDataGenerator.generate_conversation("session_123")
        
        for message in conversation["messages"]:
            assert "role" in message
            assert "content" in message
            assert "timestamp" in message
            assert message["role"] in ["patient", "assistant"]
    
    def test_generate_conversation_analysis(self):
        """Test that conversation has analysis."""
        conversation = TestDataGenerator.generate_conversation("session_123")
        
        analysis = conversation["analysis"]
        assert "sentiment" in analysis
        assert "topics" in analysis
        assert "requires_attention" in analysis
        assert analysis["sentiment"] in ["positive", "neutral", "negative"]


class TestBatchGeneration:
    """Test batch data generation."""
    
    def test_generate_batch_knowledge_documents(self):
        """Test generating batch of knowledge documents."""
        docs = TestDataGenerator.generate_batch_knowledge_documents(5)
        
        assert len(docs) == 5
        for doc in docs:
            assert "disease_name" in doc
            assert "tags" in doc
    
    def test_generate_batch_knowledge_documents_uniqueness(self):
        """Test that batch documents are unique."""
        docs = TestDataGenerator.generate_batch_knowledge_documents(3)
        
        names = [doc["name"] for doc in docs]
        assert len(names) == len(set(names))  # All unique
    
    def test_generate_batch_agents(self):
        """Test generating batch of agents."""
        agents = TestDataGenerator.generate_batch_agents(3)
        
        assert len(agents) == 3
        for agent in agents:
            assert "name" in agent
            assert "knowledge_ids" in agent
    
    def test_generate_batch_agents_with_knowledge_ids(self):
        """Test generating batch agents with specific knowledge IDs."""
        knowledge_ids = ["knowledge_1", "knowledge_2"]
        agents = TestDataGenerator.generate_batch_agents(
            2,
            knowledge_ids=knowledge_ids
        )
        
        for agent in agents:
            assert agent["knowledge_ids"] == knowledge_ids
    
    def test_generate_batch_templates(self):
        """Test generating batch of templates."""
        templates = TestDataGenerator.generate_batch_templates(3)
        
        assert len(templates) == 3
        for template in templates:
            assert "name" in template
            assert "content" in template


class TestUniqueIdGeneration:
    """Test unique ID generation."""
    
    def test_generate_unique_id_default(self):
        """Test generating unique ID with default prefix."""
        id1 = TestDataGenerator.generate_unique_id()
        id2 = TestDataGenerator.generate_unique_id()
        
        assert id1.startswith("test_")
        assert id2.startswith("test_")
        assert id1 != id2
    
    def test_generate_unique_id_custom_prefix(self):
        """Test generating unique ID with custom prefix."""
        id1 = TestDataGenerator.generate_unique_id("custom")
        id2 = TestDataGenerator.generate_unique_id("custom")
        
        assert id1.startswith("custom_")
        assert id2.startswith("custom_")
        assert id1 != id2
    
    def test_generate_unique_id_format(self):
        """Test that unique ID has correct format."""
        unique_id = TestDataGenerator.generate_unique_id("prefix")
        
        parts = unique_id.split("_")
        assert len(parts) == 2
        assert parts[0] == "prefix"
        assert len(parts[1]) == 16  # hex string


class TestCompleteTestDataSet:
    """Test complete test data set generation."""
    
    def test_generate_test_data_set(self):
        """Test generating complete test data set."""
        data_set = TestDataGenerator.generate_test_data_set()
        
        assert "doctor_id" in data_set
        assert "knowledge_documents" in data_set
        assert "knowledge_ids" in data_set
        assert "agents" in data_set
        assert "agent_ids" in data_set
        assert "sessions" in data_set
        assert "session_ids" in data_set
        assert "audio_requests" in data_set
        assert "templates" in data_set
        assert "generated_at" in data_set
    
    def test_generate_test_data_set_structure(self):
        """Test that test data set has correct structure."""
        data_set = TestDataGenerator.generate_test_data_set()
        
        assert isinstance(data_set["knowledge_documents"], list)
        assert isinstance(data_set["agents"], list)
        assert isinstance(data_set["sessions"], list)
        assert isinstance(data_set["audio_requests"], list)
        assert isinstance(data_set["templates"], list)
    
    def test_generate_test_data_set_consistency(self):
        """Test that test data set is internally consistent."""
        data_set = TestDataGenerator.generate_test_data_set()
        
        # Knowledge IDs should match documents
        assert len(data_set["knowledge_ids"]) == len(data_set["knowledge_documents"])
        
        # Agent IDs should match agents
        assert len(data_set["agent_ids"]) == len(data_set["agents"])
        
        # Session IDs should match sessions
        assert len(data_set["session_ids"]) == len(data_set["sessions"])


class TestDataGeneratorEdgeCases:
    """Test edge cases in data generation."""
    
    def test_generate_knowledge_document_disease_name_valid(self):
        """Test that disease name is from valid list."""
        doc = TestDataGenerator.generate_knowledge_document()
        
        assert doc["disease_name"] in TestDataGenerator.DISEASE_NAMES
    
    def test_generate_knowledge_document_tags_valid(self):
        """Test that tags are from valid list."""
        doc = TestDataGenerator.generate_knowledge_document()
        
        for tag in doc["tags"]:
            assert tag in TestDataGenerator.TAGS
    
    def test_generate_agent_config_voice_id_valid(self):
        """Test that voice ID is from valid list."""
        config = TestDataGenerator.generate_agent_config()
        
        assert config["voice_id"] in TestDataGenerator.VOICE_IDS
    
    def test_generate_batch_with_zero_count(self):
        """Test generating batch with zero count."""
        docs = TestDataGenerator.generate_batch_knowledge_documents(0)
        
        assert len(docs) == 0
    
    def test_generate_batch_with_large_count(self):
        """Test generating batch with large count."""
        docs = TestDataGenerator.generate_batch_knowledge_documents(50)
        
        assert len(docs) == 50


@pytest.mark.postman
class TestDataGeneratorProperties:
    """Property-based tests for data generator."""
    
    def test_property_data_validity(self):
        """Test that all generated data is valid."""
        # Generate various data types
        doc = TestDataGenerator.generate_knowledge_document()
        audio = TestDataGenerator.generate_audio_request("knowledge_123")
        agent = TestDataGenerator.generate_agent_config()
        session = TestDataGenerator.generate_patient_session("agent_123")
        template = TestDataGenerator.generate_template()
        
        # All should be dictionaries
        assert isinstance(doc, dict)
        assert isinstance(audio, dict)
        assert isinstance(agent, dict)
        assert isinstance(session, dict)
        assert isinstance(template, dict)
        
        # All should have required fields
        assert len(doc) > 0
        assert len(audio) > 0
        assert len(agent) > 0
        assert len(session) > 0
        assert len(template) > 0
    
    def test_property_data_uniqueness(self):
        """Test that generated data is unique."""
        docs = [TestDataGenerator.generate_knowledge_document() for _ in range(10)]
        
        names = [doc["name"] for doc in docs]
        # All names should be unique
        assert len(names) == len(set(names))
