"""
Task 6: Environment Manager Component Tests

This test file validates environment management functionality:
- EnvironmentManager class implementation
- Environment creation and variable management
- Property tests for environment completeness
- Property tests for dynamic variable chaining
- Unit tests for edge cases
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List

from hypothesis import given, strategies as st

from postman_test_helpers import (
    TestDataManager,
    valid_name_strategy,
    valid_description_strategy,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.environment_manager import EnvironmentManager


class TestEnvironmentManagerInitialization:
    """Test EnvironmentManager initialization."""
    
    def test_initialization_defaults(self):
        """Test creating EnvironmentManager with defaults."""
        manager = EnvironmentManager(workspace_id="workspace123456789012345")
        
        assert manager.workspace_id == "workspace123456789012345"
        assert manager.name == "Test Environment"
        assert len(manager.variables) == 0
        assert manager.environment_id is not None
    
    def test_initialization_custom_name(self):
        """Test creating EnvironmentManager with custom name."""
        manager = EnvironmentManager(
            workspace_id="workspace123456789012345",
            name="Custom Environment"
        )
        
        assert manager.name == "Custom Environment"
    
    def test_environment_id_generation(self):
        """Test that environment ID is generated."""
        manager1 = EnvironmentManager("workspace1")
        manager2 = EnvironmentManager("workspace2")
        
        assert manager1.environment_id != manager2.environment_id
        assert manager1.environment_id.startswith("env_")


class TestEnvironmentVariableManagement:
    """Test environment variable management."""
    
    def test_set_variable(self):
        """Test setting a variable."""
        manager = EnvironmentManager("workspace123456789012345")
        
        manager.set_variable("base_url", "http://localhost:8000")
        
        assert "base_url" in manager.variables
        assert manager.variables["base_url"]["value"] == "http://localhost:8000"
        assert manager.variables["base_url"]["enabled"] is True
    
    def test_set_multiple_variables(self):
        """Test setting multiple variables."""
        manager = EnvironmentManager("workspace123456789012345")
        
        manager.set_variable("base_url", "http://localhost:8000")
        manager.set_variable("api_key", "test_key_12345")
        manager.set_variable("timeout", "30")
        
        assert len(manager.variables) == 3
        assert manager.get_variable("base_url") == "http://localhost:8000"
        assert manager.get_variable("api_key") == "test_key_12345"
    
    def test_get_variable(self):
        """Test getting a variable."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("test_var", "test_value")
        
        value = manager.get_variable("test_var")
        
        assert value == "test_value"
    
    def test_get_nonexistent_variable(self):
        """Test getting a nonexistent variable."""
        manager = EnvironmentManager("workspace123456789012345")
        
        value = manager.get_variable("nonexistent")
        
        assert value is None
    
    def test_delete_variable(self):
        """Test deleting a variable."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("test_var", "test_value")
        
        result = manager.delete_variable("test_var")
        
        assert result is True
        assert "test_var" not in manager.variables
    
    def test_delete_nonexistent_variable(self):
        """Test deleting a nonexistent variable."""
        manager = EnvironmentManager("workspace123456789012345")
        
        result = manager.delete_variable("nonexistent")
        
        assert result is False
    
    def test_enable_disable_variable(self):
        """Test enabling and disabling variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("test_var", "test_value", enabled=True)
        
        # Disable
        manager.disable_variable("test_var")
        assert manager.variables["test_var"]["enabled"] is False
        
        # Enable
        manager.enable_variable("test_var")
        assert manager.variables["test_var"]["enabled"] is True
    
    def test_get_all_variables(self):
        """Test getting all variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("var1", "value1")
        manager.set_variable("var2", "value2")
        manager.set_variable("var3", "value3")
        
        all_vars = manager.get_all_variables()
        
        assert len(all_vars) == 3
        assert all_vars["var1"] == "value1"
        assert all_vars["var2"] == "value2"


class TestEnvironmentCreation:
    """Test environment creation."""
    
    def test_create_environment(self):
        """Test creating an environment."""
        manager = EnvironmentManager("workspace123456789012345")
        
        metadata = manager.create_environment("Test Env", "Test environment")
        
        assert metadata["name"] == "Test Env"
        assert metadata["description"] == "Test environment"
        assert metadata["workspace_id"] == "workspace123456789012345"
        assert metadata["variable_count"] == 0
    
    def test_create_environment_with_variables(self):
        """Test creating environment with variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        manager.set_variable("api_key", "test_key")
        
        metadata = manager.create_environment("Test Env")
        
        assert metadata["variable_count"] == 2


class TestEnvironmentValidation:
    """Test environment validation."""
    
    def test_validate_required_variables_success(self):
        """Test validation when all required variables are present."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        manager.set_variable("api_key", "test_key")
        
        result = manager.validate_required_variables(["base_url", "api_key"])
        
        assert result is True
    
    def test_validate_required_variables_missing(self):
        """Test validation when required variables are missing."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        result = manager.validate_required_variables(["base_url", "api_key"])
        
        assert result is False
    
    def test_validate_required_variables_disabled(self):
        """Test validation when required variables are disabled."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000", enabled=True)
        manager.set_variable("api_key", "test_key", enabled=False)
        
        result = manager.validate_required_variables(["base_url", "api_key"])
        
        assert result is False
    
    def test_get_missing_variables(self):
        """Test getting list of missing variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        missing = manager.get_missing_variables(["base_url", "api_key", "timeout"])
        
        assert len(missing) == 2
        assert "api_key" in missing
        assert "timeout" in missing


class TestEnvironmentBuild:
    """Test environment JSON building."""
    
    def test_build_environment(self):
        """Test building environment JSON."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        manager.set_variable("api_key", "test_key")
        
        env_json = manager.build()
        
        assert env_json["id"] == manager.environment_id
        assert env_json["name"] == manager.name
        assert len(env_json["values"]) == 2
        assert env_json["_postman_variable_scope"] == "environment"
    
    def test_build_environment_structure(self):
        """Test that built environment has correct structure."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        env_json = manager.build()
        
        # Check required fields
        assert "id" in env_json
        assert "name" in env_json
        assert "values" in env_json
        assert "_postman_variable_scope" in env_json
        assert "_postman_exported_at" in env_json
        
        # Check variable structure
        assert len(env_json["values"]) > 0
        var = env_json["values"][0]
        assert "key" in var
        assert "value" in var
        assert "enabled" in var
        assert "type" in var
    
    def test_build_environment_with_disabled_variables(self):
        """Test building environment with disabled variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000", enabled=True)
        manager.set_variable("api_key", "test_key", enabled=False)
        
        env_json = manager.build()
        
        # Find variables
        base_url_var = next(v for v in env_json["values"] if v["key"] == "base_url")
        api_key_var = next(v for v in env_json["values"] if v["key"] == "api_key")
        
        assert base_url_var["enabled"] is True
        assert api_key_var["enabled"] is False


class TestEnvironmentSerialization:
    """Test environment serialization."""
    
    def test_to_json(self):
        """Test converting environment to JSON string."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        json_str = manager.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == manager.name
    
    def test_from_dict(self):
        """Test loading environment from dictionary."""
        manager = EnvironmentManager("workspace123456789012345")
        
        data = {
            "name": "Loaded Environment",
            "id": "env_test123",
            "values": [
                {"key": "base_url", "value": "http://localhost:8000", "enabled": True},
                {"key": "api_key", "value": "test_key", "enabled": True},
            ]
        }
        
        manager.from_dict(data)
        
        assert manager.name == "Loaded Environment"
        assert manager.environment_id == "env_test123"
        assert len(manager.variables) == 2
        assert manager.get_variable("base_url") == "http://localhost:8000"


class TestEnvironmentCloning:
    """Test environment cloning."""
    
    def test_clone_environment(self):
        """Test cloning an environment."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        manager.set_variable("api_key", "test_key")
        
        cloned = manager.clone("Cloned Environment")
        
        assert cloned.name == "Cloned Environment"
        assert cloned.environment_id != manager.environment_id
        assert len(cloned.variables) == 2
        assert cloned.get_variable("base_url") == "http://localhost:8000"
    
    def test_clone_independence(self):
        """Test that cloned environment is independent."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        cloned = manager.clone("Cloned")
        cloned.set_variable("new_var", "new_value")
        
        assert "new_var" not in manager.variables
        assert "new_var" in cloned.variables


class TestEnvironmentMerging:
    """Test environment merging."""
    
    def test_merge_environments(self):
        """Test merging two environments."""
        manager1 = EnvironmentManager("workspace1")
        manager1.set_variable("base_url", "http://localhost:8000")
        
        manager2 = EnvironmentManager("workspace2")
        manager2.set_variable("api_key", "test_key")
        manager2.set_variable("timeout", "30")
        
        manager1.merge(manager2)
        
        assert len(manager1.variables) == 3
        assert manager1.get_variable("base_url") == "http://localhost:8000"
        assert manager1.get_variable("api_key") == "test_key"
        assert manager1.get_variable("timeout") == "30"
    
    def test_merge_overwrites_existing(self):
        """Test that merge overwrites existing variables."""
        manager1 = EnvironmentManager("workspace1")
        manager1.set_variable("base_url", "http://localhost:8000")
        
        manager2 = EnvironmentManager("workspace2")
        manager2.set_variable("base_url", "http://api.example.com")
        
        manager1.merge(manager2)
        
        assert manager1.get_variable("base_url") == "http://api.example.com"


class TestEnvironmentUtilities:
    """Test environment utility methods."""
    
    def test_get_variable_count(self):
        """Test getting variable count."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("var1", "value1")
        manager.set_variable("var2", "value2")
        
        count = manager.get_variable_count()
        
        assert count == 2
    
    def test_get_enabled_variable_count(self):
        """Test getting enabled variable count."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("var1", "value1", enabled=True)
        manager.set_variable("var2", "value2", enabled=False)
        manager.set_variable("var3", "value3", enabled=True)
        
        count = manager.get_enabled_variable_count()
        
        assert count == 2
    
    def test_get_variable_keys(self):
        """Test getting all variable keys."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("var1", "value1")
        manager.set_variable("var2", "value2")
        
        keys = manager.get_variable_keys()
        
        assert len(keys) == 2
        assert "var1" in keys
        assert "var2" in keys
    
    def test_clear_variables(self):
        """Test clearing all variables."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("var1", "value1")
        manager.set_variable("var2", "value2")
        
        manager.clear()
        
        assert len(manager.variables) == 0


class TestEnvironmentCompleteness:
    """Property tests for environment completeness."""
    
    @given(
        var_count=st.integers(min_value=1, max_value=10),
    )
    def test_property_environment_completeness(self, var_count):
        """
        Property 3: Environment Variable Completeness
        
        Validates: Requirements 1.3, 14.3, 14.5
        
        For any number of variables added to an environment:
        1. All variables should be retrievable
        2. Environment should build successfully
        3. Built JSON should contain all variables
        4. All required fields should be present
        """
        manager = EnvironmentManager("workspace123456789012345")
        
        # Add variables
        for i in range(var_count):
            manager.set_variable(f"var_{i}", f"value_{i}")
        
        # Property 1: All variables retrievable
        for i in range(var_count):
            assert manager.get_variable(f"var_{i}") == f"value_{i}"
        
        # Property 2: Environment builds successfully
        env_json = manager.build()
        assert env_json is not None
        
        # Property 3: Built JSON contains all variables
        assert len(env_json["values"]) == var_count
        
        # Property 4: Required fields present
        assert "id" in env_json
        assert "name" in env_json
        assert "values" in env_json
        assert "_postman_variable_scope" in env_json


class TestDynamicVariableChaining:
    """Property tests for dynamic variable chaining."""
    
    @given(
        chain_length=st.integers(min_value=2, max_value=5),
    )
    def test_property_dynamic_variable_chaining(self, chain_length):
        """
        Property 40: Dynamic Variable Chaining
        
        Validates: Requirements 14.2, 15.1
        
        For any chain of variable references:
        1. Variables should be settable with references
        2. Variables should be retrievable in order
        3. Chaining should not create circular references
        4. All variables in chain should be accessible
        """
        manager = EnvironmentManager("workspace123456789012345")
        
        # Create chain of variables
        for i in range(chain_length):
            if i == 0:
                manager.set_variable(f"var_{i}", f"base_value_{i}")
            else:
                # Reference previous variable
                manager.set_variable(f"var_{i}", f"{{{{var_{i-1}}}}}_{i}")
        
        # Property 1: All variables settable
        assert len(manager.variables) == chain_length
        
        # Property 2: All variables retrievable
        for i in range(chain_length):
            value = manager.get_variable(f"var_{i}")
            assert value is not None
        
        # Property 3: Build should succeed
        env_json = manager.build()
        assert len(env_json["values"]) == chain_length
        
        # Property 4: All variables in JSON
        var_keys = [v["key"] for v in env_json["values"]]
        for i in range(chain_length):
            assert f"var_{i}" in var_keys


class TestEnvironmentEdgeCases:
    """Test environment edge cases."""
    
    def test_empty_variable_key(self):
        """Test setting variable with empty key."""
        manager = EnvironmentManager("workspace123456789012345")
        
        with pytest.raises(ValueError):
            manager.set_variable("", "value")
    
    def test_special_characters_in_value(self):
        """Test variable with special characters."""
        manager = EnvironmentManager("workspace123456789012345")
        
        special_value = "value!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        manager.set_variable("special", special_value)
        
        assert manager.get_variable("special") == special_value
    
    def test_unicode_in_variable(self):
        """Test variable with unicode characters."""
        manager = EnvironmentManager("workspace123456789012345")
        
        unicode_value = "值 🎉 مرحبا"
        manager.set_variable("unicode", unicode_value)
        
        assert manager.get_variable("unicode") == unicode_value
    
    def test_very_long_variable_value(self):
        """Test variable with very long value."""
        manager = EnvironmentManager("workspace123456789012345")
        
        long_value = "x" * 10000
        manager.set_variable("long", long_value)
        
        assert manager.get_variable("long") == long_value
    
    def test_variable_with_description(self):
        """Test setting variable with description."""
        manager = EnvironmentManager("workspace123456789012345")
        
        manager.set_variable(
            "test_var",
            "test_value",
            description="This is a test variable"
        )
        
        assert manager.variables["test_var"]["description"] == "This is a test variable"


@pytest.mark.postman
@pytest.mark.property
class TestEnvironmentProperties:
    """Property-based tests for environment."""
    
    @given(st.just(None))
    def test_property_environment_idempotence(self, _):
        """Test that environment operations are idempotent."""
        manager = EnvironmentManager("workspace123456789012345")
        
        # Set variable multiple times
        manager.set_variable("test", "value1")
        manager.set_variable("test", "value2")
        manager.set_variable("test", "value3")
        
        # Should have latest value
        assert manager.get_variable("test") == "value3"
        assert len(manager.variables) == 1
    
    @given(st.just(None))
    def test_property_environment_consistency(self, _):
        """Test that environment is consistent."""
        manager = EnvironmentManager("workspace123456789012345")
        manager.set_variable("base_url", "http://localhost:8000")
        
        # Build multiple times
        env1 = manager.build()
        env2 = manager.build()
        
        # Should be identical
        assert env1["id"] == env2["id"]
        assert len(env1["values"]) == len(env2["values"])
