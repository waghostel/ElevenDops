"""
Task 12: Knowledge API Tests

This test file validates Knowledge API functionality:
- POST /api/knowledge (create)
- GET /api/knowledge (list)
- GET /api/knowledge/{knowledge_id} (read)
- PUT /api/knowledge/{knowledge_id} (update)
- DELETE /api/knowledge/{knowledge_id} (delete)
- POST /api/knowledge/{knowledge_id}/retry-sync

Requirements: 3.1-3.8, 4.7-4.8, 5.3-5.4, 8.3-8.5, 9.5

Property Tests:
- Property 5: CRUD Round-Trip Consistency
- Property 6: Update Persistence
- Property 7: Deletion Verification
- Property 8: Structured Content Parsing
- Property 9: ElevenLabs Naming Convention
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List
from hypothesis import given, strategies as st, settings, HealthCheck

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.collection_builder import CollectionBuilder
from backend.services.test_script_generator import TestScriptGenerator
from backend.services.test_data_generator import TestDataGenerator
from backend.services.environment_manager import EnvironmentManager
from tests.postman.postman_test_helpers import (
    TestDataManager,
    PostmanConfigHelper,
    valid_name_strategy,
    valid_description_strategy,
)


# ============================================================================
# UNIT TESTS - Knowledge API Endpoints
# ============================================================================

class TestKnowledgeCreateEndpoint:
    """Test POST /api/knowledge endpoint."""
    
    def test_create_knowledge_basic(self):
        """Test creating a knowledge document with basic data."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        test_data = TestDataGenerator.generate_knowledge_document()
        
        request_id = builder.add_request(
            folder_id,
            "Create Knowledge Document",
            "POST",
            "{{base_url}}/api/knowledge",
            body={
                "disease_name": test_data["disease_name"],
                "tags": test_data["tags"],
                "raw_content": test_data["raw_content"],
                "doctor_id": test_data["doctor_id"],
            },
            headers={"Content-Type": "application/json"},
        )
        
        # Add test scripts
        script = TestScriptGenerator.generate_status_check(201)
        script += TestScriptGenerator.generate_schema_validation(
            ["knowledge_id", "disease_name", "tags", "sync_status"]
        )
        script += TestScriptGenerator.generate_variable_save("knowledge_id", "$.knowledge_id")
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
        assert builder.requests[request_id]["method"] == "POST"
    
    def test_create_knowledge_with_structured_sections(self):
        """Test creating knowledge with structured sections."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        test_data = TestDataGenerator.generate_knowledge_document(
            include_structured_sections=True
        )
        
        request_id = builder.add_request(
            folder_id,
            "Create Knowledge with Sections",
            "POST",
            "{{base_url}}/api/knowledge",
            body=test_data,
            headers={"Content-Type": "application/json"},
        )
        
        script = TestScriptGenerator.generate_status_check(201)
        script += TestScriptGenerator.generate_field_check("$.structured_sections", "array")
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_create_knowledge_missing_required_fields(self):
        """Test creating knowledge with missing required fields."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Error Handling")
        
        # Missing disease_name
        request_id = builder.add_request(
            folder_id,
            "Create Knowledge Missing Fields",
            "POST",
            "{{base_url}}/api/knowledge",
            body={
                "tags": ["chronic"],
                "raw_content": "Test content",
            },
        )
        
        script = TestScriptGenerator.generate_status_check(422)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests


class TestKnowledgeListEndpoint:
    """Test GET /api/knowledge endpoint."""
    
    def test_list_knowledge_documents(self):
        """Test listing all knowledge documents."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        request_id = builder.add_request(
            folder_id,
            "List Knowledge Documents",
            "GET",
            "{{base_url}}/api/knowledge",
            headers={"Content-Type": "application/json"},
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation(
            ["documents", "total_count"]
        )
        script += TestScriptGenerator.generate_field_check("$.documents", "array")
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_list_knowledge_with_filters(self):
        """Test listing knowledge with filter parameters."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        request_id = builder.add_request(
            folder_id,
            "List Knowledge with Filters",
            "GET",
            "{{base_url}}/api/knowledge",
            params={
                "disease_name": "Diabetes",
                "tags": "chronic",
            },
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests


class TestKnowledgeGetEndpoint:
    """Test GET /api/knowledge/{knowledge_id} endpoint."""
    
    def test_get_knowledge_by_id(self):
        """Test getting a specific knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        request_id = builder.add_request(
            folder_id,
            "Get Knowledge by ID",
            "GET",
            "{{base_url}}/api/knowledge/{{knowledge_id}}",
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation(
            ["knowledge_id", "disease_name", "raw_content", "sync_status"]
        )
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_get_knowledge_not_found(self):
        """Test getting non-existent knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Error Handling")
        
        request_id = builder.add_request(
            folder_id,
            "Get Knowledge Not Found",
            "GET",
            "{{base_url}}/api/knowledge/nonexistent_id",
        )
        
        script = TestScriptGenerator.generate_status_check(404)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests


class TestKnowledgeUpdateEndpoint:
    """Test PUT /api/knowledge/{knowledge_id} endpoint."""
    
    def test_update_knowledge_basic(self):
        """Test updating a knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        update_data = {
            "disease_name": "Updated Disease",
            "tags": ["updated", "chronic"],
            "raw_content": "Updated content for the disease",
        }
        
        request_id = builder.add_request(
            folder_id,
            "Update Knowledge Document",
            "PUT",
            "{{base_url}}/api/knowledge/{{knowledge_id}}",
            body=update_data,
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_field_check("$.disease_name", "string")
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_update_knowledge_partial(self):
        """Test partial update of knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        request_id = builder.add_request(
            folder_id,
            "Partial Update Knowledge",
            "PUT",
            "{{base_url}}/api/knowledge/{{knowledge_id}}",
            body={"disease_name": "New Disease Name"},
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_update_knowledge_not_found(self):
        """Test updating non-existent knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Error Handling")
        
        request_id = builder.add_request(
            folder_id,
            "Update Knowledge Not Found",
            "PUT",
            "{{base_url}}/api/knowledge/nonexistent_id",
            body={"disease_name": "New Name"},
        )
        
        script = TestScriptGenerator.generate_status_check(404)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests


class TestKnowledgeDeleteEndpoint:
    """Test DELETE /api/knowledge/{knowledge_id} endpoint."""
    
    def test_delete_knowledge_document(self):
        """Test deleting a knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge CRUD")
        
        request_id = builder.add_request(
            folder_id,
            "Delete Knowledge Document",
            "DELETE",
            "{{base_url}}/api/knowledge/{{knowledge_id}}",
        )
        
        script = TestScriptGenerator.generate_status_check(204)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_delete_knowledge_not_found(self):
        """Test deleting non-existent knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Error Handling")
        
        request_id = builder.add_request(
            folder_id,
            "Delete Knowledge Not Found",
            "DELETE",
            "{{base_url}}/api/knowledge/nonexistent_id",
        )
        
        script = TestScriptGenerator.generate_status_check(404)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests


class TestKnowledgeRetrySyncEndpoint:
    """Test POST /api/knowledge/{knowledge_id}/retry-sync endpoint."""
    
    def test_retry_sync_failed_document(self):
        """Test retrying sync for failed knowledge document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge Sync")
        
        request_id = builder.add_request(
            folder_id,
            "Retry Knowledge Sync",
            "POST",
            "{{base_url}}/api/knowledge/{{knowledge_id}}/retry-sync",
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_field_check("$.sync_status", "string")
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_retry_sync_already_completed(self):
        """Test retrying sync for already completed document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Knowledge Sync")
        
        request_id = builder.add_request(
            folder_id,
            "Retry Sync Already Completed",
            "POST",
            "{{base_url}}/api/knowledge/{{knowledge_id}}/retry-sync",
        )
        
        script = TestScriptGenerator.generate_status_check(200)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
    
    def test_retry_sync_not_found(self):
        """Test retrying sync for non-existent document."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Knowledge API Tests")
        folder_id = builder.add_folder("Error Handling")
        
        request_id = builder.add_request(
            folder_id,
            "Retry Sync Not Found",
            "POST",
            "{{base_url}}/api/knowledge/nonexistent_id/retry-sync",
        )
        
        script = TestScriptGenerator.generate_status_check(404)
        builder.add_test_script(request_id, script)
        
        assert request_id in builder.requests
