"""
Postman Configuration Service

This module provides configuration loading, validation, and management
for Postman integration.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from backend.models.postman_config import PostmanConfig


logger = logging.getLogger(__name__)


class PostmanConfigService:
    """Service for managing Postman configuration."""
    
    CONFIG_FILE = ".postman.json"
    
    @staticmethod
    def load_config(config_file: Optional[str] = None) -> PostmanConfig:
        """
        Load Postman configuration from file.
        
        Args:
            config_file: Path to configuration file (default: .postman.json)
        
        Returns:
            PostmanConfig: Validated configuration object
        
        Raises:
            FileNotFoundError: If configuration file not found
            ValueError: If configuration is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        config_path = config_file or PostmanConfigService.CONFIG_FILE
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        
        try:
            config = PostmanConfig(**config_data)
            logger.info("Configuration validated successfully")
            return config
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ValueError(f"Configuration validation failed: {e}")
    
    @staticmethod
    def save_config(config: PostmanConfig, config_file: Optional[str] = None) -> None:
        """
        Save Postman configuration to file.
        
        Args:
            config: PostmanConfig object to save
            config_file: Path to configuration file (default: .postman.json)
        """
        config_path = config_file or PostmanConfigService.CONFIG_FILE
        
        try:
            config_data = config.dict()
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    @staticmethod
    def update_config(updates: Dict[str, Any], config_file: Optional[str] = None) -> PostmanConfig:
        """
        Update specific fields in configuration.
        
        Args:
            updates: Dictionary of fields to update
            config_file: Path to configuration file (default: .postman.json)
        
        Returns:
            PostmanConfig: Updated configuration object
        """
        config_path = config_file or PostmanConfigService.CONFIG_FILE
        
        try:
            config = PostmanConfigService.load_config(config_path)
        except FileNotFoundError:
            # If file doesn't exist, create new config with updates
            config_data = updates
        else:
            config_data = config.dict()
            config_data.update(updates)
        
        try:
            updated_config = PostmanConfig(**config_data)
            PostmanConfigService.save_config(updated_config, config_path)
            logger.info(f"Updated configuration with: {list(updates.keys())}")
            return updated_config
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise
    
    @staticmethod
    def validate_config(config_data: Dict[str, Any]) -> bool:
        """
        Validate configuration data without saving.
        
        Args:
            config_data: Configuration dictionary to validate
        
        Returns:
            bool: True if valid, raises exception otherwise
        """
        try:
            PostmanConfig(**config_data)
            logger.info("Configuration validation passed")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    @staticmethod
    def get_config_field(field_name: str, config_file: Optional[str] = None) -> Any:
        """
        Get a specific field from configuration.
        
        Args:
            field_name: Name of field to retrieve
            config_file: Path to configuration file (default: .postman.json)
        
        Returns:
            Field value
        
        Raises:
            KeyError: If field not found
        """
        config = PostmanConfigService.load_config(config_file)
        if not hasattr(config, field_name):
            raise KeyError(f"Configuration field not found: {field_name}")
        return getattr(config, field_name)
    
    @staticmethod
    def set_config_field(field_name: str, value: Any, config_file: Optional[str] = None) -> PostmanConfig:
        """
        Set a specific field in configuration.
        
        Args:
            field_name: Name of field to set
            value: Value to set
            config_file: Path to configuration file (default: .postman.json)
        
        Returns:
            PostmanConfig: Updated configuration object
        """
        return PostmanConfigService.update_config({field_name: value}, config_file)


__all__ = ['PostmanConfigService']
