"""
Environment Manager Component for Postman Testing

Manages Postman environment variables and environment creation.
Supports dynamic variable chaining and environment JSON generation.

Requirements: 1.3, 14.1, 14.2, 14.3, 14.5, 15.1
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Manages Postman environment variables and environment creation.
    
    Supports:
    - Creating new environments
    - Setting and getting variables
    - Dynamic variable chaining
    - Building valid Postman environment JSON
    """
    
    def __init__(self, workspace_id: str, name: str = "Test Environment"):
        """
        Initialize EnvironmentManager.
        
        Args:
            workspace_id: Postman workspace ID
            name: Environment name
        """
        self.workspace_id = workspace_id
        self.name = name
        self.variables: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.utcnow().isoformat()
        self.environment_id = f"env_{uuid.uuid4().hex[:16]}"
    
    def create_environment(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new environment.
        
        Args:
            name: Environment name
            description: Environment description
            
        Returns:
            Environment metadata
        """
        self.name = name
        self.description = description
        
        metadata = {
            "id": self.environment_id,
            "name": name,
            "description": description,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at,
            "variable_count": len(self.variables),
        }
        
        logger.info(f"Created environment: {name} ({self.environment_id})")
        return metadata
    
    def set_variable(
        self,
        key: str,
        value: str,
        enabled: bool = True,
        description: str = "",
    ) -> None:
        """
        Set an environment variable.
        
        Args:
            key: Variable key
            value: Variable value
            enabled: Whether variable is enabled
            description: Variable description
        """
        if not key:
            raise ValueError("Variable key cannot be empty")
        
        self.variables[key] = {
            "key": key,
            "value": value,
            "enabled": enabled,
            "description": description,
            "type": "string",
        }
        
        logger.debug(f"Set variable: {key} = {value[:20]}...")
    
    def get_variable(self, key: str) -> Optional[str]:
        """
        Get an environment variable value.
        
        Args:
            key: Variable key
            
        Returns:
            Variable value or None if not found
        """
        if key not in self.variables:
            return None
        
        return self.variables[key]["value"]
    
    def get_all_variables(self) -> Dict[str, str]:
        """
        Get all environment variables as key-value pairs.
        
        Returns:
            Dictionary of all variables
        """
        return {
            key: var["value"]
            for key, var in self.variables.items()
        }
    
    def delete_variable(self, key: str) -> bool:
        """
        Delete an environment variable.
        
        Args:
            key: Variable key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self.variables:
            del self.variables[key]
            logger.debug(f"Deleted variable: {key}")
            return True
        return False
    
    def enable_variable(self, key: str) -> bool:
        """
        Enable an environment variable.
        
        Args:
            key: Variable key
            
        Returns:
            True if enabled, False if not found
        """
        if key in self.variables:
            self.variables[key]["enabled"] = True
            return True
        return False
    
    def disable_variable(self, key: str) -> bool:
        """
        Disable an environment variable.
        
        Args:
            key: Variable key
            
        Returns:
            True if disabled, False if not found
        """
        if key in self.variables:
            self.variables[key]["enabled"] = False
            return True
        return False
    
    def validate_required_variables(self, required_keys: List[str]) -> bool:
        """
        Validate that all required variables are present and enabled.
        
        Args:
            required_keys: List of required variable keys
            
        Returns:
            True if all required variables are present and enabled
        """
        for key in required_keys:
            if key not in self.variables:
                logger.warning(f"Missing required variable: {key}")
                return False
            
            if not self.variables[key]["enabled"]:
                logger.warning(f"Required variable disabled: {key}")
                return False
        
        return True
    
    def get_missing_variables(self, required_keys: List[str]) -> List[str]:
        """
        Get list of missing required variables.
        
        Args:
            required_keys: List of required variable keys
            
        Returns:
            List of missing variable keys
        """
        missing = []
        for key in required_keys:
            if key not in self.variables or not self.variables[key]["enabled"]:
                missing.append(key)
        return missing
    
    def build(self) -> Dict[str, Any]:
        """
        Build valid Postman environment JSON.
        
        Returns:
            Postman environment JSON structure
        """
        # Validate required variables
        required_vars = ["base_url"]
        missing = self.get_missing_variables(required_vars)
        if missing:
            logger.warning(f"Missing required variables: {missing}")
        
        # Build environment structure
        environment = {
            "id": self.environment_id,
            "name": self.name,
            "values": [
                {
                    "key": var["key"],
                    "value": var["value"],
                    "enabled": var["enabled"],
                    "type": var.get("type", "string"),
                }
                for var in self.variables.values()
            ],
            "_postman_variable_scope": "environment",
            "_postman_exported_at": datetime.utcnow().isoformat(),
            "_postman_exported_using": "Postman/11.0.0",
        }
        
        logger.info(f"Built environment: {self.name} with {len(self.variables)} variables")
        return environment
    
    def to_json(self) -> str:
        """
        Convert environment to JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.build(), indent=2)
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load environment from dictionary.
        
        Args:
            data: Environment data dictionary
        """
        if "values" in data:
            for var in data["values"]:
                self.set_variable(
                    key=var.get("key", ""),
                    value=var.get("value", ""),
                    enabled=var.get("enabled", True),
                    description=var.get("description", ""),
                )
        
        if "name" in data:
            self.name = data["name"]
        
        if "id" in data:
            self.environment_id = data["id"]
        
        logger.info(f"Loaded environment from dict: {self.name}")
    
    def clone(self, new_name: str) -> "EnvironmentManager":
        """
        Clone this environment with a new name.
        
        Args:
            new_name: Name for cloned environment
            
        Returns:
            New EnvironmentManager instance
        """
        cloned = EnvironmentManager(self.workspace_id, new_name)
        
        # Copy all variables
        for key, var in self.variables.items():
            cloned.set_variable(
                key=var["key"],
                value=var["value"],
                enabled=var["enabled"],
                description=var.get("description", ""),
            )
        
        logger.info(f"Cloned environment: {self.name} -> {new_name}")
        return cloned
    
    def merge(self, other: "EnvironmentManager") -> None:
        """
        Merge another environment into this one.
        
        Args:
            other: EnvironmentManager to merge
        """
        for key, var in other.variables.items():
            self.set_variable(
                key=var["key"],
                value=var["value"],
                enabled=var["enabled"],
                description=var.get("description", ""),
            )
        
        logger.info(f"Merged environment: {other.name} into {self.name}")
    
    def get_variable_count(self) -> int:
        """
        Get count of variables in environment.
        
        Returns:
            Number of variables
        """
        return len(self.variables)
    
    def get_enabled_variable_count(self) -> int:
        """
        Get count of enabled variables.
        
        Returns:
            Number of enabled variables
        """
        return sum(1 for var in self.variables.values() if var["enabled"])
    
    def get_variable_keys(self) -> List[str]:
        """
        Get all variable keys.
        
        Returns:
            List of variable keys
        """
        return list(self.variables.keys())
    
    def clear(self) -> None:
        """Clear all variables from environment."""
        self.variables.clear()
        logger.info(f"Cleared all variables from environment: {self.name}")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"EnvironmentManager(name={self.name}, "
            f"variables={len(self.variables)}, "
            f"id={self.environment_id})"
        )


__all__ = ["EnvironmentManager"]
