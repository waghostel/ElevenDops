"""
Task 2: Configuration Management Tests

This test file validates configuration management functionality:
- PostmanConfig model with validation
- Configuration loading and validation
- Property tests for configuration completeness
- Unit tests for edge cases
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
from hypothesis import given, strategies as st

from postman_test_helpers import (
    TestDataManager,
    PostmanConfigHelper,
    valid_uid_strategy,
    valid_name_strategy,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.postman_config import PostmanConfig
from backend.services.postman_config_service import PostmanConfigService


class TestPostmanConfigModel:
    """Test PostmanConfig Pydantic model."""
    
    def test_valid_config_creation(self):
        """Test creating a valid PostmanConfig."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
        )
        
        assert config.workspace_id == "workspace123456789012345"
        assert config.collection_id == "collection12345678901234"
        assert config.environment_id == "environment1234567890123"
        assert config.api_key == "test_api_key_12345"
        assert config.base_url == "http://localhost:8000"
    
    def test_config_with_custom_base_url(self):
        """Test creating config with custom base URL."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
            base_url="https://api.example.com",
        )
        
        assert config.base_url == "https://api.example.com"
    
    def test_config_missing_required_field(self):
        """Test that missing required fields raise error."""
        with pytest.raises(ValueError):
            PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                # Missing environment_id
                api_key="test_api_key_12345",
            )
    
    def test_config_invalid_uid_format(self):
        """Test that invalid UID format raises error."""
        with pytest.raises(ValueError):
            PostmanConfig(
                workspace_id="invalid@uid",  # Invalid characters
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
            )
    
    def test_config_invalid_api_key(self):
        """Test that invalid API key raises error."""
        with pytest.raises(ValueError):
            PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="short",  # Too short
            )
    
    def test_config_invalid_base_url(self):
        """Test that invalid base URL raises error."""
        with pytest.raises(ValueError):
            PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
                base_url="invalid-url",  # Missing protocol
            )
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
        )
        
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["workspace_id"] == "workspace123456789012345"
        assert config_dict["api_key"] == "test_api_key_12345"
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "workspace_id": "workspace123456789012345",
            "collection_id": "collection12345678901234",
            "environment_id": "environment1234567890123",
            "api_key": "test_api_key_12345",
        }
        
        config = PostmanConfig.from_dict(config_dict)
        assert config.workspace_id == "workspace123456789012345"
        assert config.api_key == "test_api_key_12345"


class TestPostmanConfigService:
    """Test PostmanConfigService."""
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")
            
            # Create and save config
            config = PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
            )
            
            PostmanConfigService.save_config(config, config_file)
            assert os.path.exists(config_file)
            
            # Load and verify
            loaded_config = PostmanConfigService.load_config(config_file)
            assert loaded_config.workspace_id == config.workspace_id
            assert loaded_config.api_key == config.api_key
    
    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError):
            PostmanConfigService.load_config("/nonexistent/path/config.json")
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "invalid.json")
            
            # Write invalid JSON
            with open(config_file, 'w') as f:
                f.write("{ invalid json }")
            
            with pytest.raises(ValueError):
                PostmanConfigService.load_config(config_file)
    
    def test_load_config_missing_required_fields(self):
        """Test loading config with missing required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "incomplete.json")
            
            # Write incomplete config
            with open(config_file, 'w') as f:
                json.dump({
                    "workspace_id": "workspace123456789012345",
                    # Missing other required fields
                }, f)
            
            with pytest.raises(ValueError):
                PostmanConfigService.load_config(config_file)
    
    def test_update_config(self):
        """Test updating configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")
            
            # Create initial config
            config = PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
            )
            PostmanConfigService.save_config(config, config_file)
            
            # Update config
            updated_config = PostmanConfigService.update_config(
                {"base_url": "https://api.example.com"},
                config_file
            )
            
            assert updated_config.base_url == "https://api.example.com"
            assert updated_config.workspace_id == "workspace123456789012345"
    
    def test_validate_config(self):
        """Test configuration validation."""
        valid_config = {
            "workspace_id": "workspace123456789012345",
            "collection_id": "collection12345678901234",
            "environment_id": "environment1234567890123",
            "api_key": "test_api_key_12345",
        }
        
        assert PostmanConfigService.validate_config(valid_config) is True
    
    def test_validate_config_invalid(self):
        """Test validation of invalid configuration."""
        invalid_config = {
            "workspace_id": "workspace123456789012345",
            # Missing required fields
        }
        
        with pytest.raises(ValueError):
            PostmanConfigService.validate_config(invalid_config)
    
    def test_get_config_field(self):
        """Test getting specific config field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")
            
            config = PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
            )
            PostmanConfigService.save_config(config, config_file)
            
            workspace_id = PostmanConfigService.get_config_field("workspace_id", config_file)
            assert workspace_id == "workspace123456789012345"
    
    def test_set_config_field(self):
        """Test setting specific config field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")
            
            config = PostmanConfig(
                workspace_id="workspace123456789012345",
                collection_id="collection12345678901234",
                environment_id="environment1234567890123",
                api_key="test_api_key_12345",
            )
            PostmanConfigService.save_config(config, config_file)
            
            updated_config = PostmanConfigService.set_config_field(
                "base_url",
                "https://new.example.com",
                config_file
            )
            
            assert updated_config.base_url == "https://new.example.com"


class TestConfigurationLoadingCompleteness:
    """Property tests for configuration loading completeness."""
    
    @given(
        workspace_id=valid_uid_strategy(),
        collection_id=valid_uid_strategy(),
        environment_id=valid_uid_strategy(),
        api_key=st.text(min_size=8, max_size=100),
    )
    def test_property_config_loading_completeness(
        self,
        workspace_id,
        collection_id,
        environment_id,
        api_key,
    ):
        """
        Property 2: Configuration Loading Completeness
        
        Validates: Requirements 1.2
        
        For any valid configuration data, the configuration should:
        1. Load successfully
        2. Preserve all fields
        3. Validate all required fields
        4. Be convertible to/from dictionary
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.json")
            
            # Create config with generated data
            config_data = {
                "workspace_id": workspace_id,
                "collection_id": collection_id,
                "environment_id": environment_id,
                "api_key": api_key,
            }
            
            # Save config
            with open(config_file, 'w') as f:
                json.dump(config_data, f)
            
            # Load and verify
            loaded_config = PostmanConfigService.load_config(config_file)
            
            # Property 1: All fields preserved
            assert loaded_config.workspace_id == workspace_id
            assert loaded_config.collection_id == collection_id
            assert loaded_config.environment_id == environment_id
            assert loaded_config.api_key == api_key
            
            # Property 2: Convertible to dictionary
            config_dict = loaded_config.to_dict()
            assert config_dict["workspace_id"] == workspace_id
            
            # Property 3: Convertible from dictionary
            recreated_config = PostmanConfig.from_dict(config_dict)
            assert recreated_config.workspace_id == workspace_id
            assert recreated_config.api_key == api_key


class TestConfigurationEdgeCases:
    """Test configuration edge cases."""
    
    def test_config_with_metadata(self):
        """Test config with additional metadata."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
            metadata={"custom_field": "custom_value"},
        )
        
        assert config.metadata["custom_field"] == "custom_value"
    
    def test_config_with_test_results(self):
        """Test config with test results."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
            test_results={"total": 10, "passed": 10, "failed": 0},
        )
        
        assert config.test_results["total"] == 10
        assert config.test_results["passed"] == 10
    
    def test_config_with_postman_api_key(self):
        """Test config with Postman API key."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
            postman_api_key="postman_key_12345",
        )
        
        assert config.postman_api_key == "postman_key_12345"


@pytest.mark.postman
@pytest.mark.property
class TestConfigurationProperties:
    """Property-based tests for configuration."""
    
    @given(st.just(None))
    def test_property_config_defaults(self, _):
        """Test that config has sensible defaults."""
        config = PostmanConfig(
            workspace_id="workspace123456789012345",
            collection_id="collection12345678901234",
            environment_id="environment1234567890123",
            api_key="test_api_key_12345",
        )
        
        # Default values should be set
        assert config.base_url == "http://localhost:8000"
        assert config.test_results == {}
        assert config.metadata == {}
        assert config.postman_api_key is None
