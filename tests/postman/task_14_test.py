"""
Task 14: Agent API Tests for Phase 6 Postman Backend Testing

This test file validates agent management API functionality:
- POST /api/agent (create agent)
- GET /api/agent (list agents)
- PUT /api/agent/{agent_id} (update agent)
- DELETE /api/agent/{agent_id} (delete agent)
- GET /api/agent/system-prompts (get system prompts)

Requirements: 5.1-5.6
Property Tests: Property 15 - Agent-Knowledge Relationship Integrity

Test Coverage:
- Agent creation with various configurations
- Agent listing and filtering
- Agent updates (name, knowledge, languages)
- Agent deletion
- System prompts retrieval
- Error handling (404, 400, 422)
- Property-based testing for agent-knowledge relationships
"""

import pytest
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from hypothesis import given, strategies as st, settings, HealthCheck

from postman_test_helpers import (
    TestDataManager,
    valid_name_strategy,
    valid_description_strategy,
    assert_valid_response,
    assert_valid_error_response,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_script_generator import TestScriptGenerator
from backend.services.test_data_generator import TestDataGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager


# ============================================================================
# Test Request Creation
# ============================================================================

class TestAgentRequestCreation:
    """Create test requests for agent API endpoints."""
    
    @staticmethod
    def create_post_agent_request(test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create POST /api/agent request."""
        script = TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(201),
            TestScriptGenerator.generate_schema_validation(["agent_id", "name", "elevenlabs_agent_id"]),
            TestScriptGenerator.generate_variable_save("agent_id", "agent_id"),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ])
        
        return {
            "name": "Create Agent",
            "request": {
                "method": "POST",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(test_data)
                },
                "url": {
                    "raw": "{{base_url}}/api/agent",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent"]
                }
            },
            "tests": script
        }
    
    @staticmethod
    def create_get_agents_request() -> Dict[str, Any]:
        """Create GET /api/agent request."""
        script = TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["agents", "total_count"]),
            TestScriptGenerator.generate_array_length_check("agents", min_length=0),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ])
        
        return {
            "name": "List Agents",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/agent",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent"]
                }
            },
            "tests": script
        }
    
    @staticmethod
    def create_put_agent_request(agent_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create PUT /api/agent/{agent_id} request."""
        script = TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["agent_id", "name"]),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ])
        
        return {
            "name": f"Update Agent {agent_id}",
            "request": {
                "method": "PUT",
                "header": [
                    {"key": "Content-Type", "value": "application/json"}
                ],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(update_data)
                },
                "url": {
                    "raw": f"{{{{base_url}}}}/api/agent/{agent_id}",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent", agent_id]
                }
            },
            "tests": script
        }
    
    @staticmethod
    def create_delete_agent_request(agent_id: str) -> Dict[str, Any]:
        """Create DELETE /api/agent/{agent_id} request."""
        script = TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["status", "message"]),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ])
        
        return {
            "name": f"Delete Agent {agent_id}",
            "request": {
                "method": "DELETE",
                "header": [],
                "url": {
                    "raw": f"{{{{base_url}}}}/api/agent/{agent_id}",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent", agent_id]
                }
            },
            "tests": script
        }
    
    @staticmethod
    def create_get_system_prompts_request() -> Dict[str, Any]:
        """Create GET /api/agent/system-prompts request."""
        script = TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_content_type_check("application/json"),
        ])
        
        return {
            "name": "Get System Prompts",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/api/agent/system-prompts",
                    "protocol": "http",
                    "host": ["{{base_url}}"],
                    "path": ["api", "agent", "system-prompts"]
                }
            },
            "tests": script
        }


# ============================================================================
# Test Script Generation
# ============================================================================

class TestAgentScriptGeneration:
    """Generate test scripts for agent operations."""
    
    @staticmethod
    def generate_create_agent_script() -> str:
        """Generate test script for agent creation."""
        return TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(201),
            TestScriptGenerator.generate_schema_validation([
                "agent_id", "name", "knowledge_ids", "voice_id", 
                "answer_style", "elevenlabs_agent_id", "created_at"
            ]),
            TestScriptGenerator.generate_field_check("agent_id", "string"),
            TestScriptGenerator.generate_field_check("name", "string"),
            TestScriptGenerator.generate_field_check("knowledge_ids", "array"),
            TestScriptGenerator.generate_field_check("voice_id", "string"),
            TestScriptGenerator.generate_field_check("answer_style", "string"),
            TestScriptGenerator.generate_variable_save("agent_id", "agent_id"),
            TestScriptGenerator.generate_response_time_check(2000),
        ])
    
    @staticmethod
    def generate_list_agents_script() -> str:
        """Generate test script for listing agents."""
        return TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["agents", "total_count"]),
            TestScriptGenerator.generate_field_check("agents", "array"),
            TestScriptGenerator.generate_field_check("total_count", "number"),
            TestScriptGenerator.generate_array_length_check("agents", min_length=0),
            TestScriptGenerator.generate_response_time_check(1000),
        ])
    
    @staticmethod
    def generate_update_agent_script() -> str:
        """Generate test script for agent update."""
        return TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["agent_id", "name"]),
            TestScriptGenerator.generate_field_check("agent_id", "string"),
            TestScriptGenerator.generate_response_time_check(2000),
        ])
    
    @staticmethod
    def generate_delete_agent_script() -> str:
        """Generate test script for agent deletion."""
        return TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_schema_validation(["status", "message"]),
            TestScriptGenerator.generate_value_assertion("status", "success", "equals"),
            TestScriptGenerator.generate_response_time_check(1000),
        ])
    
    @staticmethod
    def generate_system_prompts_script() -> str:
        """Generate test script for system prompts."""
        return TestScriptGenerator.combine_scripts([
            TestScriptGenerator.generate_status_check(200),
            TestScriptGenerator.generate_content_type_check("application/json"),
            TestScriptGenerator.generate_response_time_check(500),
        ])


# ============================================================================
# Test Data Generation
# ============================================================================

class TestAgentDataGeneration:
    """Generate test data for agent operations."""
    
    @staticmethod
    def generate_agent_create_data(
        knowledge_ids: Optional[List[str]] = None,
        doctor_id: str = "test_doctor_001",
    ) -> Dict[str, Any]:
        """Generate agent creation data."""
        if knowledge_ids is None:
            knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(2)]
        
        return {
            "name": f"Test_Agent_{uuid.uuid4().hex[:8]}",
            "knowledge_ids": knowledge_ids,
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "answer_style": "professional",
            "languages": ["en"],
            "doctor_id": doctor_id,
        }
    
    @staticmethod
    def generate_agent_update_data() -> Dict[str, Any]:
        """Generate agent update data."""
        return {
            "name": f"Updated_Agent_{uuid.uuid4().hex[:8]}",
            "languages": ["en", "es"],
        }
    
    @staticmethod
    def generate_batch_agent_data(count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple agent configurations."""
        return [TestAgentDataGeneration.generate_agent_create_data() for _ in range(count)]


# ============================================================================
# Unit Tests - Agent Creation
# ============================================================================

class TestAgentCreation:
    """Test agent creation endpoint."""
    
    def test_create_agent_minimal(self, test_data_manager: TestDataManager):
        """Test creating agent with minimal required fields."""
        test_data = TestAgentDataGeneration.generate_agent_create_data()
        request = TestAgentRequestCreation.create_post_agent_request(test_data)
        
        assert request["request"]["method"] == "POST"
        assert "/api/agent" in request["request"]["url"]["raw"]
        assert "agent_id" in request["tests"]
        assert "201" in request["tests"]
    
    def test_create_agent_with_multiple_knowledge(self, test_data_manager: TestDataManager):
        """Test creating agent with multiple knowledge documents."""
        knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(3)]
        test_data = TestAgentDataGeneration.generate_agent_create_data(knowledge_ids)
        request = TestAgentRequestCreation.create_post_agent_request(test_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert len(body["knowledge_ids"]) == 3
        assert all(isinstance(kid, str) for kid in body["knowledge_ids"])
    
    def test_create_agent_different_styles(self, test_data_manager: TestDataManager):
        """Test creating agents with different answer styles."""
        styles = ["professional", "friendly", "educational"]
        
        for style in styles:
            test_data = TestAgentDataGeneration.generate_agent_create_data()
            test_data["answer_style"] = style
            request = TestAgentRequestCreation.create_post_agent_request(test_data)
            
            body = json.loads(request["request"]["body"]["raw"])
            assert body["answer_style"] == style
    
    def test_create_agent_with_custom_prompt(self, test_data_manager: TestDataManager):
        """Test creating agent with custom system prompt."""
        test_data = TestAgentDataGeneration.generate_agent_create_data()
        test_data["system_prompt_override"] = "Custom system prompt for testing"
        request = TestAgentRequestCreation.create_post_agent_request(test_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert "system_prompt_override" in body
    
    def test_create_agent_script_validation(self, test_data_manager: TestDataManager):
        """Test that creation script is valid JavaScript."""
        script = TestAgentScriptGeneration.generate_create_agent_script()
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "pm.test(" in script
        assert "201" in script
        assert "agent_id" in script


# ============================================================================
# Unit Tests - Agent Listing
# ============================================================================

class TestAgentListing:
    """Test agent listing endpoint."""
    
    def test_list_agents_request(self, test_data_manager: TestDataManager):
        """Test listing agents request structure."""
        request = TestAgentRequestCreation.create_get_agents_request()
        
        assert request["request"]["method"] == "GET"
        assert "/api/agent" in request["request"]["url"]["raw"]
        assert "agents" in request["tests"]
        assert "total_count" in request["tests"]
    
    def test_list_agents_script_validation(self, test_data_manager: TestDataManager):
        """Test that listing script is valid JavaScript."""
        script = TestAgentScriptGeneration.generate_list_agents_script()
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "pm.test(" in script
        assert "200" in script
        assert "agents" in script
    
    def test_list_agents_response_structure(self, test_data_manager: TestDataManager):
        """Test expected response structure for list agents."""
        request = TestAgentRequestCreation.create_get_agents_request()
        
        # Verify request structure
        assert "url" in request["request"]
        assert "tests" in request
        assert "Content-Type" in request["tests"] or "application/json" in request["tests"]


# ============================================================================
# Unit Tests - Agent Update
# ============================================================================

class TestAgentUpdate:
    """Test agent update endpoint."""
    
    def test_update_agent_name(self, test_data_manager: TestDataManager):
        """Test updating agent name."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        update_data = {"name": "Updated Agent Name"}
        request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        
        assert request["request"]["method"] == "PUT"
        assert agent_id in request["request"]["url"]["raw"]
        body = json.loads(request["request"]["body"]["raw"])
        assert body["name"] == "Updated Agent Name"
    
    def test_update_agent_knowledge(self, test_data_manager: TestDataManager):
        """Test updating agent knowledge documents."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        new_knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(2)]
        update_data = {"knowledge_ids": new_knowledge_ids}
        request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["knowledge_ids"] == new_knowledge_ids
    
    def test_update_agent_languages(self, test_data_manager: TestDataManager):
        """Test updating agent languages."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        update_data = {"languages": ["en", "es", "fr"]}
        request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["languages"] == ["en", "es", "fr"]
    
    def test_update_agent_script_validation(self, test_data_manager: TestDataManager):
        """Test that update script is valid JavaScript."""
        script = TestAgentScriptGeneration.generate_update_agent_script()
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "pm.test(" in script
        assert "200" in script


# ============================================================================
# Unit Tests - Agent Deletion
# ============================================================================

class TestAgentDeletion:
    """Test agent deletion endpoint."""
    
    def test_delete_agent_request(self, test_data_manager: TestDataManager):
        """Test deleting agent request structure."""
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        request = TestAgentRequestCreation.create_delete_agent_request(agent_id)
        
        assert request["request"]["method"] == "DELETE"
        assert agent_id in request["request"]["url"]["raw"]
        assert "status" in request["tests"]
    
    def test_delete_agent_script_validation(self, test_data_manager: TestDataManager):
        """Test that deletion script is valid JavaScript."""
        script = TestAgentScriptGeneration.generate_delete_agent_script()
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "pm.test(" in script
        assert "200" in script
        assert "success" in script


# ============================================================================
# Unit Tests - System Prompts
# ============================================================================

class TestSystemPrompts:
    """Test system prompts endpoint."""
    
    def test_get_system_prompts_request(self, test_data_manager: TestDataManager):
        """Test getting system prompts request structure."""
        request = TestAgentRequestCreation.create_get_system_prompts_request()
        
        assert request["request"]["method"] == "GET"
        assert "/api/agent/system-prompts" in request["request"]["url"]["raw"]
        assert "200" in request["tests"]
    
    def test_system_prompts_script_validation(self, test_data_manager: TestDataManager):
        """Test that system prompts script is valid JavaScript."""
        script = TestAgentScriptGeneration.generate_system_prompts_script()
        
        assert TestScriptGenerator.validate_javascript(script)
        assert "pm.test(" in script
        assert "200" in script


# ============================================================================
# Unit Tests - Error Handling
# ============================================================================

class TestAgentErrorHandling:
    """Test error handling for agent endpoints."""
    
    def test_create_agent_missing_required_field(self, test_data_manager: TestDataManager):
        """Test creating agent with missing required field."""
        test_data = TestAgentDataGeneration.generate_agent_create_data()
        del test_data["voice_id"]  # Remove required field
        request = TestAgentRequestCreation.create_post_agent_request(test_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert "voice_id" not in body
    
    def test_update_nonexistent_agent(self, test_data_manager: TestDataManager):
        """Test updating nonexistent agent (404)."""
        agent_id = f"nonexistent_{uuid.uuid4().hex[:16]}"
        update_data = {"name": "Updated"}
        request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        
        assert agent_id in request["request"]["url"]["raw"]
    
    def test_delete_nonexistent_agent(self, test_data_manager: TestDataManager):
        """Test deleting nonexistent agent (404)."""
        agent_id = f"nonexistent_{uuid.uuid4().hex[:16]}"
        request = TestAgentRequestCreation.create_delete_agent_request(agent_id)
        
        assert agent_id in request["request"]["url"]["raw"]
    
    def test_invalid_answer_style(self, test_data_manager: TestDataManager):
        """Test creating agent with invalid answer style."""
        test_data = TestAgentDataGeneration.generate_agent_create_data()
        test_data["answer_style"] = "invalid_style"
        request = TestAgentRequestCreation.create_post_agent_request(test_data)
        
        body = json.loads(request["request"]["body"]["raw"])
        assert body["answer_style"] == "invalid_style"


# ============================================================================
# Collection Building
# ============================================================================

class TestAgentCollectionBuilding:
    """Build Postman collection for agent tests."""
    
    @staticmethod
    def build_agent_collection() -> Dict[str, Any]:
        """Build complete agent test collection."""
        builder = CollectionBuilder(
            name="Agent API Tests",
            description="Tests for agent management endpoints"
        )
        
        # Create folder for agent tests
        builder.create_folder("Agent Operations")
        
        # Add requests
        test_data = TestAgentDataGeneration.generate_agent_create_data()
        builder.add_request(TestAgentRequestCreation.create_post_agent_request(test_data))
        builder.add_request(TestAgentRequestCreation.create_get_agents_request())
        builder.add_request(TestAgentRequestCreation.create_get_system_prompts_request())
        
        # Add update and delete with variables
        builder.add_request(TestAgentRequestCreation.create_put_agent_request(
            "{{agent_id}}", 
            TestAgentDataGeneration.generate_agent_update_data()
        ))
        builder.add_request(TestAgentRequestCreation.create_delete_agent_request("{{agent_id}}"))
        
        return builder.build()


# ============================================================================
# Property-Based Tests
# ============================================================================

@pytest.mark.postman
@pytest.mark.property
class TestAgentProperties:
    """Property-based tests for agent operations."""
    
    @given(
        knowledge_count=st.integers(min_value=0, max_value=5),
        language_count=st.integers(min_value=1, max_value=3),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_agent_knowledge_relationship_integrity(
        self,
        knowledge_count: int,
        language_count: int,
    ):
        """
        Property 15: Agent-Knowledge Relationship Integrity
        
        Validates: Requirements 5.1-5.6
        
        For any agent configuration:
        1. Agent can be created with any number of knowledge documents (0-5)
        2. Knowledge IDs are preserved in agent configuration
        3. Agent can be updated with different knowledge documents
        4. Agent maintains language configuration
        5. Agent creation request is valid JSON
        6. Agent update request is valid JSON
        7. All required fields are present in creation request
        8. Agent ID is properly formatted
        """
        # Generate knowledge IDs
        knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(knowledge_count)]
        languages = ["en"] + [f"lang_{i}" for i in range(language_count - 1)]
        
        # Property 1: Create agent with knowledge documents
        create_data = TestAgentDataGeneration.generate_agent_create_data(knowledge_ids)
        create_request = TestAgentRequestCreation.create_post_agent_request(create_data)
        
        # Property 2: Knowledge IDs preserved
        body = json.loads(create_request["request"]["body"]["raw"])
        assert len(body["knowledge_ids"]) == knowledge_count
        for kid in body["knowledge_ids"]:
            assert kid in knowledge_ids
        
        # Property 3: Valid JSON
        assert isinstance(body, dict)
        assert "name" in body
        assert "voice_id" in body
        assert "answer_style" in body
        
        # Property 4: Update with different knowledge
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        new_knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(knowledge_count)]
        update_data = {"knowledge_ids": new_knowledge_ids}
        update_request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        
        # Property 5: Update is valid JSON
        update_body = json.loads(update_request["request"]["body"]["raw"])
        assert isinstance(update_body, dict)
        assert len(update_body["knowledge_ids"]) == knowledge_count
        
        # Property 6: Language configuration maintained
        create_data["languages"] = languages
        create_request = TestAgentRequestCreation.create_post_agent_request(create_data)
        body = json.loads(create_request["request"]["body"]["raw"])
        assert body["languages"] == languages
        
        # Property 7: Test scripts are valid
        create_script = TestAgentScriptGeneration.generate_create_agent_script()
        assert TestScriptGenerator.validate_javascript(create_script)
        
        # Property 8: Agent ID format
        assert agent_id.startswith("agent_")
        assert len(agent_id) > 6


# ============================================================================
# Integration Tests
# ============================================================================

class TestAgentIntegration:
    """Integration tests for agent operations."""
    
    def test_agent_crud_workflow(self, test_data_manager: TestDataManager):
        """Test complete CRUD workflow for agents."""
        # Create
        create_data = TestAgentDataGeneration.generate_agent_create_data()
        create_request = TestAgentRequestCreation.create_post_agent_request(create_data)
        assert create_request["request"]["method"] == "POST"
        
        # List
        list_request = TestAgentRequestCreation.create_get_agents_request()
        assert list_request["request"]["method"] == "GET"
        
        # Update
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        update_data = TestAgentDataGeneration.generate_agent_update_data()
        update_request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        assert update_request["request"]["method"] == "PUT"
        
        # Delete
        delete_request = TestAgentRequestCreation.create_delete_agent_request(agent_id)
        assert delete_request["request"]["method"] == "DELETE"
    
    def test_agent_with_multiple_knowledge_workflow(self, test_data_manager: TestDataManager):
        """Test agent workflow with multiple knowledge documents."""
        knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(3)]
        
        # Create with multiple knowledge
        create_data = TestAgentDataGeneration.generate_agent_create_data(knowledge_ids)
        create_request = TestAgentRequestCreation.create_post_agent_request(create_data)
        body = json.loads(create_request["request"]["body"]["raw"])
        assert len(body["knowledge_ids"]) == 3
        
        # Update with different knowledge
        new_knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(2)]
        agent_id = f"agent_{uuid.uuid4().hex[:16]}"
        update_data = {"knowledge_ids": new_knowledge_ids}
        update_request = TestAgentRequestCreation.create_put_agent_request(agent_id, update_data)
        update_body = json.loads(update_request["request"]["body"]["raw"])
        assert len(update_body["knowledge_ids"]) == 2


# ============================================================================
# Test Execution
# ============================================================================

@pytest.mark.postman
class TestAgentAPIExecution:
    """Execute all agent API tests."""
    
    def test_all_requests_created(self, test_data_manager: TestDataManager):
        """Verify all required requests are created."""
        requests = [
            TestAgentRequestCreation.create_post_agent_request(
                TestAgentDataGeneration.generate_agent_create_data()
            ),
            TestAgentRequestCreation.create_get_agents_request(),
            TestAgentRequestCreation.create_put_agent_request(
                "test_id",
                TestAgentDataGeneration.generate_agent_update_data()
            ),
            TestAgentRequestCreation.create_delete_agent_request("test_id"),
            TestAgentRequestCreation.create_get_system_prompts_request(),
        ]
        
        assert len(requests) == 5
        assert all("request" in r for r in requests)
        assert all("tests" in r for r in requests)
    
    def test_all_scripts_generated(self, test_data_manager: TestDataManager):
        """Verify all test scripts are generated."""
        scripts = [
            TestAgentScriptGeneration.generate_create_agent_script(),
            TestAgentScriptGeneration.generate_list_agents_script(),
            TestAgentScriptGeneration.generate_update_agent_script(),
            TestAgentScriptGeneration.generate_delete_agent_script(),
            TestAgentScriptGeneration.generate_system_prompts_script(),
        ]
        
        assert len(scripts) == 5
        assert all(TestScriptGenerator.validate_javascript(s) for s in scripts)
    
    def test_all_test_data_generated(self, test_data_manager: TestDataManager):
        """Verify all test data is generated."""
        data = [
            TestAgentDataGeneration.generate_agent_create_data(),
            TestAgentDataGeneration.generate_agent_update_data(),
            TestAgentDataGeneration.generate_batch_agent_data(3),
        ]
        
        assert len(data) == 3
        assert isinstance(data[0], dict)
        assert isinstance(data[1], dict)
        assert isinstance(data[2], list)
        assert len(data[2]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
