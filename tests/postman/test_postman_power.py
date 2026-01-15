"""
Task 3: Postman Power Integration Tests

This test file validates Postman Power integration:
- PostmanPowerClient wrapper implementation
- Power activation
- Collection and environment retrieval
- Collection execution
- Unit tests for all methods
"""

import pytest
from typing import Dict, Any
from pathlib import Path

from postman_test_helpers import (
    TestDataManager,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.postman_power_client import PostmanPowerClient


class TestPostmanPowerClientInitialization:
    """Test PostmanPowerClient initialization."""
    
    def test_client_initialization(self):
        """Test creating PostmanPowerClient."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        assert client.api_key == "test_api_key_12345"
        assert client.workspace_id == "workspace123456789012345"
        assert client.is_activated is False
    
    def test_client_with_different_credentials(self):
        """Test client with different credentials."""
        client1 = PostmanPowerClient(
            api_key="key1",
            workspace_id="workspace1",
        )
        
        client2 = PostmanPowerClient(
            api_key="key2",
            workspace_id="workspace2",
        )
        
        assert client1.api_key != client2.api_key
        assert client1.workspace_id != client2.workspace_id


class TestPostmanPowerActivation:
    """Test Postman power activation."""
    
    def test_activate_power_success(self):
        """Test successful power activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        result = client.activate_power()
        
        assert result["success"] is True
        assert "message" in result
        assert "metadata" in result
        assert client.is_activated is True
    
    def test_activate_power_sets_metadata(self):
        """Test that activation sets metadata."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        client.activate_power()
        
        assert client.power_metadata["status"] == "activated"
        assert client.power_metadata["workspace_id"] == "workspace123456789012345"
        assert client.power_metadata["api_key_set"] is True
    
    def test_get_power_status_before_activation(self):
        """Test getting power status before activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        status = client.get_power_status()
        
        assert status["is_activated"] is False
        assert status["workspace_id"] == "workspace123456789012345"
    
    def test_get_power_status_after_activation(self):
        """Test getting power status after activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        client.activate_power()
        status = client.get_power_status()
        
        assert status["is_activated"] is True
        assert status["metadata"]["status"] == "activated"


class TestPostmanPowerCollectionRetrieval:
    """Test collection retrieval."""
    
    def test_get_collection_success(self):
        """Test successful collection retrieval."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        collection = client.get_collection("collection12345678901234")
        
        assert collection["id"] == "collection12345678901234"
        assert "name" in collection
        assert "item" in collection
        assert "variable" in collection
    
    def test_get_collection_without_activation(self):
        """Test that collection retrieval requires activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        with pytest.raises(RuntimeError):
            client.get_collection("collection12345678901234")
    
    def test_get_collection_with_empty_id(self):
        """Test collection retrieval with empty ID."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        with pytest.raises(ValueError):
            client.get_collection("")
    
    def test_get_collection_structure(self):
        """Test that retrieved collection has expected structure."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        collection = client.get_collection("collection12345678901234")
        
        # Verify structure
        assert "id" in collection
        assert "name" in collection
        assert "description" in collection
        assert "item" in collection
        assert "variable" in collection
        assert "auth" in collection
        assert "event" in collection


class TestPostmanPowerEnvironmentRetrieval:
    """Test environment retrieval."""
    
    def test_get_environment_success(self):
        """Test successful environment retrieval."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        environment = client.get_environment("environment1234567890123")
        
        assert environment["id"] == "environment1234567890123"
        assert "name" in environment
        assert "values" in environment
    
    def test_get_environment_without_activation(self):
        """Test that environment retrieval requires activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        with pytest.raises(RuntimeError):
            client.get_environment("environment1234567890123")
    
    def test_get_environment_with_empty_id(self):
        """Test environment retrieval with empty ID."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        with pytest.raises(ValueError):
            client.get_environment("")
    
    def test_get_environment_structure(self):
        """Test that retrieved environment has expected structure."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        environment = client.get_environment("environment1234567890123")
        
        # Verify structure
        assert "id" in environment
        assert "name" in environment
        assert "values" in environment
        assert isinstance(environment["values"], list)
        
        # Verify variable structure
        if environment["values"]:
            var = environment["values"][0]
            assert "key" in var
            assert "value" in var
            assert "enabled" in var
    
    def test_get_environment_variables(self):
        """Test that environment contains expected variables."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        environment = client.get_environment("environment1234567890123")
        
        # Check for expected variables
        var_keys = [v["key"] for v in environment["values"]]
        assert "base_url" in var_keys
        assert "api_key" in var_keys


class TestPostmanPowerCollectionExecution:
    """Test collection execution."""
    
    def test_run_collection_success(self):
        """Test successful collection execution."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        result = client.run_collection("collection12345678901234")
        
        assert result["collection_id"] == "collection12345678901234"
        assert result["status"] == "completed"
        assert "stats" in result
    
    def test_run_collection_without_activation(self):
        """Test that collection execution requires activation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        with pytest.raises(RuntimeError):
            client.run_collection("collection12345678901234")
    
    def test_run_collection_with_empty_id(self):
        """Test collection execution with empty ID."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        with pytest.raises(ValueError):
            client.run_collection("")
    
    def test_run_collection_with_environment(self):
        """Test collection execution with environment."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        result = client.run_collection(
            "collection12345678901234",
            environment_id="environment1234567890123",
        )
        
        assert result["collection_id"] == "collection12345678901234"
        assert result["environment_id"] == "environment1234567890123"
    
    def test_run_collection_with_options(self):
        """Test collection execution with options."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        options = {"timeout": 30, "verbose": True}
        result = client.run_collection(
            "collection12345678901234",
            options=options,
        )
        
        assert result["status"] == "completed"
    
    def test_run_collection_result_structure(self):
        """Test that execution result has expected structure."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        client.activate_power()
        
        result = client.run_collection("collection12345678901234")
        
        # Verify structure
        assert "collection_id" in result
        assert "status" in result
        assert "stats" in result
        assert "results" in result
        assert "timestamp" in result
        
        # Verify stats structure
        stats = result["stats"]
        assert "total" in stats
        assert "passed" in stats
        assert "failed" in stats
        assert "skipped" in stats


class TestPostmanPowerDeactivation:
    """Test power deactivation."""
    
    def test_deactivate_power(self):
        """Test power deactivation."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        client.activate_power()
        assert client.is_activated is True
        
        result = client.deactivate_power()
        
        assert result["success"] is True
        assert client.is_activated is False
        assert client.power_metadata == {}
    
    def test_deactivate_power_clears_metadata(self):
        """Test that deactivation clears metadata."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        client.activate_power()
        assert len(client.power_metadata) > 0
        
        client.deactivate_power()
        assert client.power_metadata == {}


class TestPostmanPowerClientWorkflow:
    """Test complete Postman Power client workflow."""
    
    def test_complete_workflow(self):
        """Test complete workflow: activate -> get collection -> run -> deactivate."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        # Activate
        activation_result = client.activate_power()
        assert activation_result["success"] is True
        
        # Get collection
        collection = client.get_collection("collection12345678901234")
        assert collection["id"] == "collection12345678901234"
        
        # Get environment
        environment = client.get_environment("environment1234567890123")
        assert environment["id"] == "environment1234567890123"
        
        # Run collection
        execution_result = client.run_collection(
            "collection12345678901234",
            environment_id="environment1234567890123",
        )
        assert execution_result["status"] == "completed"
        
        # Deactivate
        deactivation_result = client.deactivate_power()
        assert deactivation_result["success"] is True
    
    def test_multiple_collections(self):
        """Test running multiple collections."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        client.activate_power()
        
        # Run multiple collections
        results = []
        for i in range(3):
            collection_id = f"collection{i:024d}"
            result = client.run_collection(collection_id)
            results.append(result)
        
        assert len(results) == 3
        for result in results:
            assert result["status"] == "completed"


@pytest.mark.postman
class TestPostmanPowerClientErrorHandling:
    """Test error handling in PostmanPowerClient."""
    
    def test_error_handling_activation(self):
        """Test error handling during activation."""
        client = PostmanPowerClient(
            api_key="",  # Empty API key
            workspace_id="workspace123456789012345",
        )
        
        # Should still activate (validation happens elsewhere)
        result = client.activate_power()
        assert result["success"] is True
    
    def test_error_handling_collection_retrieval(self):
        """Test error handling during collection retrieval."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        # Should raise error if not activated
        with pytest.raises(RuntimeError):
            client.get_collection("collection12345678901234")
    
    def test_error_handling_environment_retrieval(self):
        """Test error handling during environment retrieval."""
        client = PostmanPowerClient(
            api_key="test_api_key_12345",
            workspace_id="workspace123456789012345",
        )
        
        # Should raise error if not activated
        with pytest.raises(RuntimeError):
            client.get_environment("environment1234567890123")
