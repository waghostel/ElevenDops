"""
Task 9: Collection Builder Component Tests

This test file validates collection building functionality:
- CollectionBuilder class implementation
- Collection creation and folder management
- Request addition and script attachment
- Collection JSON generation
- Unit tests for all builder methods
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List

from postman_test_helpers import TestDataManager

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.collection_builder import CollectionBuilder


class TestCollectionBuilderInitialization:
    """Test CollectionBuilder initialization."""
    
    def test_initialization_defaults(self):
        """Test creating CollectionBuilder with defaults."""
        builder = CollectionBuilder(workspace_id="workspace123456789012345")
        
        assert builder.workspace_id == "workspace123456789012345"
        assert builder.name == "Test Collection"
        assert len(builder.folders) == 0
        assert len(builder.requests) == 0
        assert builder.collection_id is not None
    
    def test_initialization_custom_name(self):
        """Test creating CollectionBuilder with custom name."""
        builder = CollectionBuilder(
            workspace_id="workspace123456789012345",
            name="Custom Collection"
        )
        
        assert builder.name == "Custom Collection"
    
    def test_collection_id_generation(self):
        """Test that collection ID is generated."""
        builder1 = CollectionBuilder("workspace1")
        builder2 = CollectionBuilder("workspace2")
        
        assert builder1.collection_id != builder2.collection_id
        assert builder1.collection_id.startswith("col_")


class TestCollectionCreation:
    """Test collection creation."""
    
    def test_create_collection(self):
        """Test creating a collection."""
        builder = CollectionBuilder("workspace123456789012345")
        
        metadata = builder.create_collection("Test Collection", "Test description")
        
        assert metadata["name"] == "Test Collection"
        assert metadata["description"] == "Test description"
        assert metadata["workspace_id"] == "workspace123456789012345"
        assert metadata["folder_count"] == 0
        assert metadata["request_count"] == 0
    
    def test_create_collection_with_auth(self):
        """Test creating collection with authentication."""
        builder = CollectionBuilder("workspace123456789012345")
        
        auth = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "test_token"}]
        }
        
        metadata = builder.create_collection(
            "Test Collection",
            auth=auth
        )
        
        assert builder.auth == auth


class TestFolderManagement:
    """Test folder management."""
    
    def test_add_folder(self):
        """Test adding a folder."""
        builder = CollectionBuilder("workspace123456789012345")
        
        folder_id = builder.add_folder("Test Folder", description="Test folder")
        
        assert folder_id in builder.folders
        assert builder.folders[folder_id]["name"] == "Test Folder"
        assert builder.folders[folder_id]["description"] == "Test folder"
    
    def test_add_multiple_folders(self):
        """Test adding multiple folders."""
        builder = CollectionBuilder("workspace123456789012345")
        
        folder_id1 = builder.add_folder("Folder 1")
        folder_id2 = builder.add_folder("Folder 2")
        folder_id3 = builder.add_folder("Folder 3")
        
        assert len(builder.folders) == 3
        assert folder_id1 != folder_id2 != folder_id3
    
    def test_add_nested_folder(self):
        """Test adding nested folder."""
        builder = CollectionBuilder("workspace123456789012345")
        
        parent_id = builder.add_folder("Parent Folder")
        child_id = builder.add_folder("Child Folder", parent_folder=parent_id)
        
        assert builder.folders[child_id]["parent"] == parent_id
    
    def test_get_folder_count(self):
        """Test getting folder count."""
        builder = CollectionBuilder("workspace123456789012345")
        
        builder.add_folder("Folder 1")
        builder.add_folder("Folder 2")
        
        assert builder.get_folder_count() == 2
    
    def test_get_folder_ids(self):
        """Test getting all folder IDs."""
        builder = CollectionBuilder("workspace123456789012345")
        
        id1 = builder.add_folder("Folder 1")
        id2 = builder.add_folder("Folder 2")
        
        folder_ids = builder.get_folder_ids()
        
        assert len(folder_ids) == 2
        assert id1 in folder_ids
        assert id2 in folder_ids


class TestRequestManagement:
    """Test request management."""
    
    def test_add_request(self):
        """Test adding a request."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test"
        )
        
        assert request_id in builder.requests
        assert builder.requests[request_id]["name"] == "Test Request"
        assert builder.requests[request_id]["method"] == "GET"
    
    def test_add_request_with_body(self):
        """Test adding request with body."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        body = {"key": "value", "nested": {"field": "data"}}
        
        request_id = builder.add_request(
            folder_id,
            "POST Request",
            "POST",
            "http://localhost:8000/api/test",
            body=body
        )
        
        assert builder.requests[request_id]["body"] == body
    
    def test_add_request_with_headers(self):
        """Test adding request with headers."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token"
        }
        
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test",
            headers=headers
        )
        
        assert builder.requests[request_id]["headers"] == headers
    
    def test_add_request_with_params(self):
        """Test adding request with query parameters."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        params = {"filter": "active", "limit": "10"}
        
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test",
            params=params
        )
        
        assert builder.requests[request_id]["params"] == params
    
    def test_add_request_to_nonexistent_folder(self):
        """Test adding request to nonexistent folder."""
        builder = CollectionBuilder("workspace123456789012345")
        
        with pytest.raises(ValueError):
            builder.add_request(
                "nonexistent_folder",
                "Test Request",
                "GET",
                "http://localhost:8000/api/test"
            )
    
    def test_add_multiple_requests(self):
        """Test adding multiple requests."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        req_id1 = builder.add_request(folder_id, "Request 1", "GET", "http://localhost:8000/1")
        req_id2 = builder.add_request(folder_id, "Request 2", "POST", "http://localhost:8000/2")
        req_id3 = builder.add_request(folder_id, "Request 3", "PUT", "http://localhost:8000/3")
        
        assert len(builder.requests) == 3
        assert req_id1 != req_id2 != req_id3
    
    def test_get_request_count(self):
        """Test getting request count."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        builder.add_request(folder_id, "Request 1", "GET", "http://localhost:8000/1")
        builder.add_request(folder_id, "Request 2", "POST", "http://localhost:8000/2")
        
        assert builder.get_request_count() == 2
    
    def test_get_request_ids(self):
        """Test getting all request IDs."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        id1 = builder.add_request(folder_id, "Request 1", "GET", "http://localhost:8000/1")
        id2 = builder.add_request(folder_id, "Request 2", "POST", "http://localhost:8000/2")
        
        request_ids = builder.get_request_ids()
        
        assert len(request_ids) == 2
        assert id1 in request_ids
        assert id2 in request_ids
    
    def test_get_requests_in_folder(self):
        """Test getting requests in specific folder."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id1 = builder.add_folder("Folder 1")
        folder_id2 = builder.add_folder("Folder 2")
        
        req_id1 = builder.add_request(folder_id1, "Request 1", "GET", "http://localhost:8000/1")
        req_id2 = builder.add_request(folder_id1, "Request 2", "POST", "http://localhost:8000/2")
        req_id3 = builder.add_request(folder_id2, "Request 3", "PUT", "http://localhost:8000/3")
        
        folder1_requests = builder.get_requests_in_folder(folder_id1)
        folder2_requests = builder.get_requests_in_folder(folder_id2)
        
        assert len(folder1_requests) == 2
        assert len(folder2_requests) == 1
        assert req_id1 in folder1_requests
        assert req_id3 in folder2_requests


class TestTestScriptManagement:
    """Test script management."""
    
    def test_add_test_script(self):
        """Test adding test script to request."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test"
        )
        
        test_script = "pm.test('Status is 200', function() { pm.response.to.have.status(200); });"
        
        builder.add_test_script(request_id, test_script)
        
        assert len(builder.requests[request_id]["tests"]) == 1
        assert builder.requests[request_id]["tests"][0]["script"] == test_script
    
    def test_add_multiple_test_scripts(self):
        """Test adding multiple test scripts to request."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test"
        )
        
        script1 = "pm.test('Status is 200', function() { pm.response.to.have.status(200); });"
        script2 = "pm.test('Has id', function() { pm.expect(pm.response.json().id).to.exist; });"
        
        builder.add_test_script(request_id, script1)
        builder.add_test_script(request_id, script2)
        
        assert len(builder.requests[request_id]["tests"]) == 2
    
    def test_add_test_script_to_nonexistent_request(self):
        """Test adding test script to nonexistent request."""
        builder = CollectionBuilder("workspace123456789012345")
        
        with pytest.raises(ValueError):
            builder.add_test_script("nonexistent_request", "test script")


class TestPreRequestScriptManagement:
    """Test pre-request script management."""
    
    def test_add_pre_request_script(self):
        """Test adding pre-request script to request."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        request_id = builder.add_request(
            folder_id,
            "Test Request",
            "GET",
            "http://localhost:8000/api/test"
        )
        
        pre_script = "pm.collectionVariables.set('timestamp', new Date().toISOString());"
        
        builder.add_pre_request_script(request_id, pre_script)
        
        assert builder.requests[request_id]["pre_request_script"] is not None
        assert builder.requests[request_id]["pre_request_script"]["script"] == pre_script
    
    def test_add_pre_request_script_to_nonexistent_request(self):
        """Test adding pre-request script to nonexistent request."""
        builder = CollectionBuilder("workspace123456789012345")
        
        with pytest.raises(ValueError):
            builder.add_pre_request_script("nonexistent_request", "script")


class TestCollectionVariableManagement:
    """Test collection variable management."""
    
    def test_add_collection_variable(self):
        """Test adding collection variable."""
        builder = CollectionBuilder("workspace123456789012345")
        
        builder.add_collection_variable("base_url", "http://localhost:8000")
        
        assert "base_url" in builder.variables
        assert builder.variables["base_url"]["value"] == "http://localhost:8000"
    
    def test_add_multiple_collection_variables(self):
        """Test adding multiple collection variables."""
        builder = CollectionBuilder("workspace123456789012345")
        
        builder.add_collection_variable("base_url", "http://localhost:8000")
        builder.add_collection_variable("api_key", "test_key_12345")
        builder.add_collection_variable("timeout", "30")
        
        assert len(builder.variables) == 3
    
    def test_get_variable_count(self):
        """Test getting variable count."""
        builder = CollectionBuilder("workspace123456789012345")
        
        builder.add_collection_variable("var1", "value1")
        builder.add_collection_variable("var2", "value2")
        
        assert builder.get_variable_count() == 2


class TestAuthenticationManagement:
    """Test authentication management."""
    
    def test_set_auth_bearer(self):
        """Test setting bearer token authentication."""
        builder = CollectionBuilder("workspace123456789012345")
        
        credentials = {"token": "test_token_12345"}
        builder.set_auth("bearer", credentials)
        
        assert builder.auth["type"] == "bearer"
        assert builder.auth["credentials"]["token"] == "test_token_12345"
    
    def test_set_auth_basic(self):
        """Test setting basic authentication."""
        builder = CollectionBuilder("workspace123456789012345")
        
        credentials = {"username": "user", "password": "pass"}
        builder.set_auth("basic", credentials)
        
        assert builder.auth["type"] == "basic"
        assert builder.auth["credentials"]["username"] == "user"


class TestCollectionBuilding:
    """Test collection JSON building."""
    
    def test_build_empty_collection(self):
        """Test building empty collection."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Empty Collection")
        
        collection = builder.build()
        
        assert collection["info"]["name"] == "Empty Collection"
        assert len(collection["item"]) == 0
        assert collection["variable"] == []
    
    def test_build_collection_with_folders(self):
        """Test building collection with folders."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        builder.add_folder("Folder 1")
        builder.add_folder("Folder 2")
        
        collection = builder.build()
        
        assert len(collection["item"]) == 2
    
    def test_build_collection_with_requests(self):
        """Test building collection with requests."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        folder_id = builder.add_folder("Test Folder")
        builder.add_request(folder_id, "Request 1", "GET", "http://localhost:8000/1")
        builder.add_request(folder_id, "Request 2", "POST", "http://localhost:8000/2")
        
        collection = builder.build()
        
        assert len(collection["item"]) == 1
        assert len(collection["item"][0]["item"]) == 2
    
    def test_build_collection_with_variables(self):
        """Test building collection with variables."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        builder.add_collection_variable("base_url", "http://localhost:8000")
        builder.add_collection_variable("api_key", "test_key")
        
        collection = builder.build()
        
        assert len(collection["variable"]) == 2
    
    def test_build_collection_structure(self):
        """Test that built collection has correct structure."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection", "Test description")
        
        collection = builder.build()
        
        # Check required fields
        assert "info" in collection
        assert "item" in collection
        assert "variable" in collection
        assert "auth" in collection
        assert "event" in collection
        
        # Check info structure
        assert "name" in collection["info"]
        assert "description" in collection["info"]
        assert "_postman_id" in collection["info"]
        assert "schema" in collection["info"]
    
    def test_build_collection_with_auth(self):
        """Test building collection with authentication."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        auth = {"type": "bearer", "bearer": [{"key": "token", "value": "test"}]}
        builder.set_auth("bearer", {"token": "test"})
        
        collection = builder.build()
        
        assert collection["auth"] is not None


class TestCollectionSerialization:
    """Test collection serialization."""
    
    def test_to_json(self):
        """Test converting collection to JSON string."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        json_str = builder.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["info"]["name"] == "Test Collection"
    
    def test_to_json_valid_json(self):
        """Test that to_json produces valid JSON."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        folder_id = builder.add_folder("Test Folder")
        builder.add_request(folder_id, "Test Request", "GET", "http://localhost:8000/test")
        
        json_str = builder.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed is not None


class TestCollectionValidation:
    """Test collection validation."""
    
    def test_validate_valid_collection(self):
        """Test validating valid collection."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        folder_id = builder.add_folder("Test Folder")
        builder.add_request(folder_id, "Test Request", "GET", "http://localhost:8000/test")
        
        assert builder.validate_collection() is True
    
    def test_validate_collection_empty_name(self):
        """Test validating collection with empty name."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.name = ""
        
        assert builder.validate_collection() is False
    
    def test_validate_collection_orphaned_requests(self):
        """Test validating collection with orphaned requests."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        # Add request directly without folder
        builder.requests["orphaned_req"] = {"name": "Orphaned"}
        
        assert builder.validate_collection() is False


class TestCollectionBuilderIntegration:
    """Integration tests for collection builder."""
    
    def test_build_complete_collection(self):
        """Test building a complete collection."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Complete Collection", "A complete test collection")
        
        # Add variables
        builder.add_collection_variable("base_url", "http://localhost:8000")
        builder.add_collection_variable("api_key", "test_key")
        
        # Add folders
        health_folder = builder.add_folder("Health Checks")
        api_folder = builder.add_folder("API Tests")
        
        # Add requests to health folder
        health_req = builder.add_request(
            health_folder,
            "Health Check",
            "GET",
            "http://localhost:8000/api/health"
        )
        builder.add_test_script(health_req, "pm.test('Status is 200', function() { pm.response.to.have.status(200); });")
        
        # Add requests to API folder
        api_req = builder.add_request(
            api_folder,
            "Create Resource",
            "POST",
            "http://localhost:8000/api/resource",
            body={"name": "Test"}
        )
        builder.add_test_script(api_req, "pm.test('Status is 201', function() { pm.response.to.have.status(201); });")
        builder.add_test_script(api_req, "pm.test('Has ID', function() { pm.expect(pm.response.json().id).to.exist; });")
        
        # Build and validate
        collection = builder.build()
        
        assert collection["info"]["name"] == "Complete Collection"
        assert len(collection["variable"]) == 2
        assert len(collection["item"]) == 2
        assert builder.validate_collection() is True
    
    def test_build_workflow_collection(self):
        """Test building a workflow collection."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Workflow Collection")
        
        # Setup folder
        setup_folder = builder.add_folder("Setup")
        setup_req = builder.add_request(
            setup_folder,
            "Create Test Data",
            "POST",
            "http://localhost:8000/api/setup"
        )
        builder.add_test_script(setup_req, "pm.test('Setup successful', function() { pm.response.to.have.status(200); });")
        builder.add_test_script(setup_req, "pm.collectionVariables.set('resource_id', pm.response.json().id);")
        
        # Test folder
        test_folder = builder.add_folder("Tests")
        test_req = builder.add_request(
            test_folder,
            "Test Resource",
            "GET",
            "http://localhost:8000/api/resource/{{resource_id}}"
        )
        builder.add_test_script(test_req, "pm.test('Resource exists', function() { pm.response.to.have.status(200); });")
        
        # Cleanup folder
        cleanup_folder = builder.add_folder("Cleanup")
        cleanup_req = builder.add_request(
            cleanup_folder,
            "Delete Test Data",
            "DELETE",
            "http://localhost:8000/api/resource/{{resource_id}}"
        )
        builder.add_test_script(cleanup_req, "pm.test('Cleanup successful', function() { pm.response.to.have.status(204); });")
        
        collection = builder.build()
        
        assert len(collection["item"]) == 3
        assert builder.validate_collection() is True


class TestCollectionBuilderEdgeCases:
    """Test edge cases in collection builder."""
    
    def test_add_request_with_all_parameters(self):
        """Test adding request with all parameters."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        request_id = builder.add_request(
            folder_id,
            "Complete Request",
            "POST",
            "http://localhost:8000/api/test",
            body={"key": "value"},
            headers={"Content-Type": "application/json"},
            params={"filter": "active"},
            description="A complete request"
        )
        
        assert request_id in builder.requests
        request = builder.requests[request_id]
        assert request["body"] == {"key": "value"}
        assert request["headers"]["Content-Type"] == "application/json"
        assert request["params"]["filter"] == "active"
    
    def test_add_request_with_special_characters_in_url(self):
        """Test adding request with special characters in URL."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        url = "http://localhost:8000/api/test?param=value&other=123"
        request_id = builder.add_request(folder_id, "Test", "GET", url)
        
        assert builder.requests[request_id]["url"] == url
    
    def test_add_request_with_unicode_in_name(self):
        """Test adding request with unicode in name."""
        builder = CollectionBuilder("workspace123456789012345")
        folder_id = builder.add_folder("Test Folder")
        
        request_id = builder.add_request(
            folder_id,
            "测试请求 🎉",
            "GET",
            "http://localhost:8000/api/test"
        )
        
        assert builder.requests[request_id]["name"] == "测试请求 🎉"


@pytest.mark.postman
class TestCollectionBuilderProperties:
    """Property-based tests for collection builder."""
    
    def test_property_collection_consistency(self):
        """Test that collection is consistent."""
        builder = CollectionBuilder("workspace123456789012345")
        builder.create_collection("Test Collection")
        
        folder_id = builder.add_folder("Test Folder")
        builder.add_request(folder_id, "Request 1", "GET", "http://localhost:8000/1")
        
        # Build multiple times
        collection1 = builder.build()
        collection2 = builder.build()
        
        # Should be identical
        assert collection1["info"]["name"] == collection2["info"]["name"]
        assert len(collection1["item"]) == len(collection2["item"])
