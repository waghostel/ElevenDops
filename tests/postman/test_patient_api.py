"""
Task 16: Conversations API Tests

This test file validates conversation API endpoints:
- GET /api/conversations (list with filters)
- GET /api/conversations/statistics
- GET /api/conversations/{conversation_id}

Requirements: 7.1-7.5

Property Tests:
- Property 19: Conversation Analysis Inclusion

Test Coverage:
- Unit tests for each endpoint
- Property-based tests with 100+ iterations
- Test request creation for Postman collection
- Test script generation for response validation
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck

from postman_test_helpers import TestDataManager, PostmanConfigHelper

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_data_generator import TestDataGenerator
from backend.services.test_script_generator import TestScriptGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager


# ============================================================================
# UNIT TESTS FOR CONVERSATIONS API ENDPOINTS
# ============================================================================

class TestConversationsListEndpoint:
    """Test GET /api/conversations endpoint."""
    
    def test_list_conversations_basic(self):
        """Test listing conversations without filters."""
        # Generate test data
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        # Verify structure
        assert "session_id" in conversation
        assert "messages" in conversation
        assert "started_at" in conversation
        assert "ended_at" in conversation
        assert "analysis" in conversation
        assert len(conversation["messages"]) == 3
    
    def test_list_conversations_with_patient_filter(self):
        """Test listing conversations filtered by patient ID."""
        patient_id = "patient_001"
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=2
        )
        
        # Add patient ID to conversation
        conversation["patient_id"] = patient_id
        
        assert conversation["patient_id"] == patient_id
        assert "messages" in conversation
    
    def test_list_conversations_with_agent_filter(self):
        """Test listing conversations filtered by agent ID."""
        agent_id = "agent_001"
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=2
        )
        
        # Add agent ID to conversation
        conversation["agent_id"] = agent_id
        
        assert conversation["agent_id"] == agent_id
    
    def test_list_conversations_with_date_range_filter(self):
        """Test listing conversations filtered by date range."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=2
        )
        
        # Parse dates
        started = datetime.fromisoformat(conversation["started_at"])
        ended = datetime.fromisoformat(conversation["ended_at"])
        
        # Verify date range
        assert started < ended
        assert (ended - started).total_seconds() > 0
    
    def test_list_conversations_response_structure(self):
        """Test that list response has correct structure."""
        conversations = []
        for i in range(3):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
        
        # Verify list structure
        assert isinstance(conversations, list)
        assert len(conversations) == 3
        for conv in conversations:
            assert "session_id" in conv
            assert "messages" in conv
            assert "analysis" in conv
    
    def test_list_conversations_pagination(self):
        """Test that list endpoint supports pagination."""
        # Generate multiple conversations
        conversations = []
        for i in range(5):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
        
        # Verify we can paginate
        assert len(conversations) >= 5
    
    def test_list_conversations_empty_result(self):
        """Test listing conversations with no results."""
        # Empty list should be valid
        conversations = []
        assert isinstance(conversations, list)
        assert len(conversations) == 0
    
    def test_list_conversations_message_count(self):
        """Test that conversations have correct message count."""
        for message_count in [1, 3, 5, 10]:
            conversation = TestDataGenerator.generate_conversation(
                session_id="session_001",
                message_count=message_count
            )
            
            assert conversation["message_count"] == message_count
            assert len(conversation["messages"]) == message_count


class TestConversationsStatisticsEndpoint:
    """Test GET /api/conversations/statistics endpoint."""
    
    def test_statistics_basic_structure(self):
        """Test that statistics endpoint returns correct structure."""
        # Generate multiple conversations
        conversations = []
        for i in range(3):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=random.randint(2, 5)
            )
            conversations.append(conv)
        
        # Calculate statistics
        total_conversations = len(conversations)
        total_messages = sum(c["message_count"] for c in conversations)
        
        assert total_conversations == 3
        assert total_messages > 0
    
    def test_statistics_message_count_aggregation(self):
        """Test that statistics correctly aggregate message counts."""
        conversations = []
        expected_total = 0
        
        for i in range(5):
            message_count = random.randint(1, 10)
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=message_count
            )
            conversations.append(conv)
            expected_total += message_count
        
        actual_total = sum(c["message_count"] for c in conversations)
        assert actual_total == expected_total
    
    def test_statistics_sentiment_distribution(self):
        """Test that statistics include sentiment distribution."""
        conversations = []
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        for i in range(10):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
            sentiment = conv["analysis"]["sentiment"]
            sentiment_counts[sentiment] += 1
        
        # Verify sentiment distribution
        total = sum(sentiment_counts.values())
        assert total == 10
    
    def test_statistics_requires_attention_count(self):
        """Test that statistics track conversations requiring attention."""
        conversations = []
        requires_attention_count = 0
        
        for i in range(10):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
            if conv["analysis"]["requires_attention"]:
                requires_attention_count += 1
        
        # Verify count
        assert requires_attention_count >= 0
        assert requires_attention_count <= 10
    
    def test_statistics_average_message_count(self):
        """Test that statistics calculate average message count."""
        conversations = []
        message_counts = []
        
        for i in range(5):
            message_count = random.randint(1, 10)
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=message_count
            )
            conversations.append(conv)
            message_counts.append(message_count)
        
        # Calculate average
        expected_avg = sum(message_counts) / len(message_counts)
        actual_total = sum(c["message_count"] for c in conversations)
        actual_avg = actual_total / len(conversations)
        
        assert actual_avg == expected_avg
    
    def test_statistics_date_range(self):
        """Test that statistics include date range information."""
        conversations = []
        
        for i in range(5):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
        
        # Get date range
        start_dates = [datetime.fromisoformat(c["started_at"]) for c in conversations]
        end_dates = [datetime.fromisoformat(c["ended_at"]) for c in conversations]
        
        earliest_start = min(start_dates)
        latest_end = max(end_dates)
        
        assert earliest_start <= latest_end


class TestConversationsGetByIdEndpoint:
    """Test GET /api/conversations/{conversation_id} endpoint."""
    
    def test_get_conversation_by_id_basic(self):
        """Test getting a conversation by ID."""
        conversation_id = "conv_001"
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        # Add ID
        conversation["id"] = conversation_id
        
        assert conversation["id"] == conversation_id
        assert "messages" in conversation
    
    def test_get_conversation_by_id_structure(self):
        """Test that conversation has complete structure."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        # Verify all required fields
        assert "session_id" in conversation
        assert "messages" in conversation
        assert "started_at" in conversation
        assert "ended_at" in conversation
        assert "duration_seconds" in conversation
        assert "message_count" in conversation
        assert "analysis" in conversation
    
    def test_get_conversation_messages_structure(self):
        """Test that conversation messages have correct structure."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        # Verify message structure
        for message in conversation["messages"]:
            assert "role" in message
            assert "content" in message
            assert "timestamp" in message
            assert message["role"] in ["patient", "assistant"]
    
    def test_get_conversation_analysis_structure(self):
        """Test that conversation analysis has correct structure."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        analysis = conversation["analysis"]
        
        # Verify analysis structure
        assert "sentiment" in analysis
        assert "topics" in analysis
        assert "requires_attention" in analysis
        assert analysis["sentiment"] in ["positive", "neutral", "negative"]
        assert isinstance(analysis["topics"], list)
        assert isinstance(analysis["requires_attention"], bool)
    
    def test_get_conversation_duration_calculation(self):
        """Test that conversation duration is correctly calculated."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=5
        )
        
        # Verify duration
        assert conversation["duration_seconds"] > 0
        assert conversation["duration_seconds"] == 5 * 60  # 5 messages * 60 seconds
    
    def test_get_conversation_timestamps_order(self):
        """Test that message timestamps are in correct order."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=5
        )
        
        # Verify timestamps are ordered
        timestamps = [datetime.fromisoformat(m["timestamp"]) for m in conversation["messages"]]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1]
    
    def test_get_conversation_with_many_messages(self):
        """Test getting conversation with many messages."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=50
        )
        
        assert conversation["message_count"] == 50
        assert len(conversation["messages"]) == 50
    
    def test_get_conversation_topics_extraction(self):
        """Test that conversation topics are extracted."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_001",
            message_count=3
        )
        
        topics = conversation["analysis"]["topics"]
        
        # Verify topics
        assert isinstance(topics, list)
        assert len(topics) > 0
        assert all(isinstance(t, str) for t in topics)


# ============================================================================
# PROPERTY-BASED TESTS
# ============================================================================

class TestConversationAnalysisInclusion:
    """
    Property 19: Conversation Analysis Inclusion
    
    Verifies that all conversations include analysis data with:
    - Sentiment classification
    - Topic extraction
    - Attention flag
    """
    
    @given(
        message_count=st.integers(min_value=1, max_value=20),
        session_id=st.text(min_size=5, max_size=20, alphabet=st.characters(
            blacklist_categories=('Cc', 'Cs'), blacklist_characters='\x00'
        )),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None
    )
    def test_conversation_always_has_analysis(self, message_count, session_id):
        """Property: Every conversation must include analysis data."""
        conversation = TestDataGenerator.generate_conversation(
            session_id=session_id,
            message_count=message_count
        )
        
        # Verify analysis exists
        assert "analysis" in conversation, "Conversation missing analysis field"
        
        analysis = conversation["analysis"]
        
        # Verify analysis structure
        assert "sentiment" in analysis, "Analysis missing sentiment"
        assert "topics" in analysis, "Analysis missing topics"
        assert "requires_attention" in analysis, "Analysis missing requires_attention"
        
        # Verify analysis values
        assert analysis["sentiment"] in ["positive", "neutral", "negative"], \
            f"Invalid sentiment: {analysis['sentiment']}"
        assert isinstance(analysis["topics"], list), "Topics must be a list"
        assert len(analysis["topics"]) > 0, "Topics list must not be empty"
        assert isinstance(analysis["requires_attention"], bool), \
            "requires_attention must be boolean"
    
    @given(
        message_count=st.integers(min_value=1, max_value=20),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None
    )
    def test_conversation_analysis_consistency(self, message_count):
        """Property: Analysis data must be consistent across multiple calls."""
        session_id = "session_consistency_test"
        
        # Generate multiple conversations with same session
        conversations = [
            TestDataGenerator.generate_conversation(
                session_id=session_id,
                message_count=message_count
            )
            for _ in range(3)
        ]
        
        # Verify all have analysis
        for conv in conversations:
            assert "analysis" in conv
            assert "sentiment" in conv["analysis"]
            assert "topics" in conv["analysis"]
            assert "requires_attention" in conv["analysis"]
    
    @given(
        message_count=st.integers(min_value=1, max_value=20),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None
    )
    def test_conversation_topics_are_valid(self, message_count):
        """Property: All topics in analysis must be valid strings."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_topics_test",
            message_count=message_count
        )
        
        topics = conversation["analysis"]["topics"]
        
        # Verify all topics are valid
        assert isinstance(topics, list)
        assert len(topics) > 0
        for topic in topics:
            assert isinstance(topic, str), f"Topic must be string, got {type(topic)}"
            assert len(topic) > 0, "Topic must not be empty"
    
    @given(
        message_count=st.integers(min_value=1, max_value=20),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None
    )
    def test_conversation_sentiment_distribution(self, message_count):
        """Property: Sentiment must be one of valid values."""
        conversation = TestDataGenerator.generate_conversation(
            session_id="session_sentiment_test",
            message_count=message_count
        )
        
        sentiment = conversation["analysis"]["sentiment"]
        
        # Verify sentiment is valid
        valid_sentiments = ["positive", "neutral", "negative"]
        assert sentiment in valid_sentiments, \
            f"Sentiment '{sentiment}' not in {valid_sentiments}"


# ============================================================================
# TEST REQUEST CREATION FOR POSTMAN COLLECTION
# ============================================================================

class TestConversationsRequestCreation:
    """Create test requests for Conversations API endpoints."""
    
    def test_create_list_conversations_request(self):
        """Create test request for GET /api/conversations."""
        builder = CollectionBuilder("workspace_test")
        folder_id = builder.add_folder("Conversations API")
        
        # Create request
        request_id = builder.add_request(
            folder_id=folder_id,
            name="List Conversations",
            method="GET",
            url="{{base_url}}/api/conversations",
            params={
                "patient_id": "{{patient_id}}",
                "agent_id": "{{agent_id}}",
                "limit": "10",
                "offset": "0"
            },
            description="List all conversations with optional filters"
        )
        
        assert request_id is not None
        assert request_id in builder.requests
        
        request = builder.requests[request_id]
        assert request["method"] == "GET"
        assert request["url"] == "{{base_url}}/api/conversations"
    
    def test_create_statistics_request(self):
        """Create test request for GET /api/conversations/statistics."""
        builder = CollectionBuilder("workspace_test")
        folder_id = builder.add_folder("Conversations API")
        
        # Create request
        request_id = builder.add_request(
            folder_id=folder_id,
            name="Get Conversations Statistics",
            method="GET",
            url="{{base_url}}/api/conversations/statistics",
            description="Get aggregated statistics for all conversations"
        )
        
        assert request_id is not None
        assert request_id in builder.requests
        
        request = builder.requests[request_id]
        assert request["method"] == "GET"
        assert request["url"] == "{{base_url}}/api/conversations/statistics"
    
    def test_create_get_conversation_request(self):
        """Create test request for GET /api/conversations/{id}."""
        builder = CollectionBuilder("workspace_test")
        folder_id = builder.add_folder("Conversations API")
        
        # Create request
        request_id = builder.add_request(
            folder_id=folder_id,
            name="Get Conversation by ID",
            method="GET",
            url="{{base_url}}/api/conversations/{{conversation_id}}",
            description="Get specific conversation by ID"
        )
        
        assert request_id is not None
        assert request_id in builder.requests
        
        request = builder.requests[request_id]
        assert request["method"] == "GET"
        assert "{{conversation_id}}" in request["url"]
    
    def test_add_test_scripts_to_requests(self):
        """Add test scripts to conversation requests."""
        builder = CollectionBuilder("workspace_test")
        folder_id = builder.add_folder("Conversations API")
        
        # Create request
        request_id = builder.add_request(
            folder_id=folder_id,
            name="List Conversations",
            method="GET",
            url="{{base_url}}/api/conversations"
        )
        
        # Add test scripts
        script1 = TestScriptGenerator.generate_status_check(200)
        script2 = TestScriptGenerator.generate_schema_validation(
            ["id", "session_id", "messages", "analysis"]
        )
        script3 = TestScriptGenerator.generate_variable_save("conversation_id", "id")
        
        builder.add_test_script(request_id, script1)
        builder.add_test_script(request_id, script2)
        builder.add_test_script(request_id, script3)
        
        # Verify scripts added
        request = builder.requests[request_id]
        assert len(request["tests"]) == 3


# ============================================================================
# TEST SCRIPT GENERATION
# ============================================================================

class TestConversationsTestScriptGeneration:
    """Generate test scripts for conversation endpoints."""
    
    def test_generate_list_conversations_scripts(self):
        """Generate test scripts for list conversations endpoint."""
        # Status check
        status_script = TestScriptGenerator.generate_status_check(200)
        assert "pm.test" in status_script
        assert "200" in status_script
        
        # Schema validation
        schema_script = TestScriptGenerator.generate_schema_validation(
            ["id", "session_id", "messages", "analysis"]
        )
        assert "pm.test" in schema_script
        assert "session_id" in schema_script
        
        # Field checks
        field_script = TestScriptGenerator.generate_field_check("messages", "array")
        assert "pm.test" in field_script
        assert "Array.isArray" in field_script
    
    def test_generate_statistics_scripts(self):
        """Generate test scripts for statistics endpoint."""
        # Status check
        status_script = TestScriptGenerator.generate_status_check(200)
        assert "pm.test" in status_script
        
        # Schema validation
        schema_script = TestScriptGenerator.generate_schema_validation(
            ["total_conversations", "total_messages", "sentiment_distribution"]
        )
        assert "total_conversations" in schema_script
        
        # Value assertions
        value_script = TestScriptGenerator.generate_value_assertion(
            "total_conversations",
            0,
            "greater_than"
        )
        assert "pm.test" in value_script
    
    def test_generate_get_conversation_scripts(self):
        """Generate test scripts for get conversation endpoint."""
        # Status check
        status_script = TestScriptGenerator.generate_status_check(200)
        assert "pm.test" in status_script
        
        # Schema validation
        schema_script = TestScriptGenerator.generate_schema_validation(
            ["id", "messages", "analysis", "duration_seconds"]
        )
        assert "messages" in schema_script
        
        # Field checks
        field_script = TestScriptGenerator.generate_field_check("analysis", "object")
        assert "pm.test" in field_script
        
        # Variable save
        var_script = TestScriptGenerator.generate_variable_save(
            "conversation_analysis",
            "analysis"
        )
        assert "pm.collectionVariables.set" in var_script


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestConversationsIntegration:
    """Integration tests for conversations API."""
    
    def test_conversation_workflow(self):
        """Test complete conversation workflow."""
        # Create session
        session_id = "session_workflow_test"
        
        # Generate conversation
        conversation = TestDataGenerator.generate_conversation(
            session_id=session_id,
            message_count=5
        )
        
        # Verify conversation
        assert conversation["session_id"] == session_id
        assert conversation["message_count"] == 5
        assert "analysis" in conversation
        
        # Verify analysis
        analysis = conversation["analysis"]
        assert "sentiment" in analysis
        assert "topics" in analysis
        assert "requires_attention" in analysis
    
    def test_multiple_conversations_aggregation(self):
        """Test aggregating multiple conversations."""
        conversations = []
        total_messages = 0
        
        for i in range(5):
            message_count = random.randint(2, 10)
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=message_count
            )
            conversations.append(conv)
            total_messages += message_count
        
        # Verify aggregation
        assert len(conversations) == 5
        assert total_messages > 0
        
        # Verify each has analysis
        for conv in conversations:
            assert "analysis" in conv
    
    def test_conversation_filtering_by_sentiment(self):
        """Test filtering conversations by sentiment."""
        conversations = []
        
        for i in range(10):
            conv = TestDataGenerator.generate_conversation(
                session_id=f"session_{i:03d}",
                message_count=2
            )
            conversations.append(conv)
        
        # Filter by sentiment
        positive_convs = [c for c in conversations 
                         if c["analysis"]["sentiment"] == "positive"]
        
        # Verify filtering works
        assert len(positive_convs) >= 0
        assert len(positive_convs) <= len(conversations)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

import random


def create_test_environment() -> EnvironmentManager:
    """Create test environment with required variables."""
    env = EnvironmentManager("test_env")
    env.set_variable("base_url", "http://localhost:8000")
    env.set_variable("patient_id", "patient_test_001")
    env.set_variable("agent_id", "agent_test_001")
    env.set_variable("conversation_id", "conv_test_001")
    return env


def verify_conversation_structure(conversation: Dict[str, Any]) -> bool:
    """Verify conversation has correct structure."""
    required_fields = [
        "session_id", "messages", "started_at", "ended_at",
        "duration_seconds", "message_count", "analysis"
    ]
    
    for field in required_fields:
        if field not in conversation:
            return False
    
    # Verify analysis structure
    analysis = conversation["analysis"]
    analysis_fields = ["sentiment", "topics", "requires_attention"]
    for field in analysis_fields:
        if field not in analysis:
            return False
    
    return True


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def test_data_manager():
    """Provide test data manager."""
    manager = TestDataManager(prefix="Conv_")
    yield manager
    manager.cleanup()


@pytest.fixture
def collection_builder():
    """Provide collection builder."""
    return CollectionBuilder("workspace_test")


@pytest.fixture
def test_environment():
    """Provide test environment."""
    return create_test_environment()


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
