"""
Shared test utilities for Postman backend testing.

This module provides common utilities, fixtures, and helpers for all Postman
backend testing tasks.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path
from threading import current_thread
import pytest
from hypothesis import strategies as st


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestDataManager:
    """Manages test data creation and cleanup."""
    
    def __init__(self, prefix: str = "Test_"):
        self.prefix = prefix
        self.created_resources: Dict[str, List[str]] = {
            "documents": [],
            "audio": [],
            "agents": [],
            "sessions": [],
            "templates": [],
        }
    
    def get_test_id(self, resource_type: str) -> str:
        """Generate unique test ID for a resource."""
        import uuid
        test_id = f"{self.prefix}{resource_type}_{uuid.uuid4().hex[:8]}"
        if resource_type in self.created_resources:
            self.created_resources[resource_type].append(test_id)
        return test_id
    
    def cleanup(self) -> None:
        """Clean up all created test resources."""
        logger.info(f"Cleaning up {sum(len(v) for v in self.created_resources.values())} test resources")
        for resource_type, ids in self.created_resources.items():
            logger.debug(f"Cleaned up {len(ids)} {resource_type}: {ids}")
    
    def get_created_resources(self) -> Dict[str, List[str]]:
        """Get all created resources."""
        return self.created_resources


class PostmanConfigHelper:
    """Helper for Postman configuration management."""
    
    CONFIG_FILE = ".postman.json"
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load Postman configuration from file."""
        if not os.path.exists(PostmanConfigHelper.CONFIG_FILE):
            logger.warning(f"{PostmanConfigHelper.CONFIG_FILE} not found")
            return {}
        
        try:
            with open(PostmanConfigHelper.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {PostmanConfigHelper.CONFIG_FILE}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {PostmanConfigHelper.CONFIG_FILE}: {e}")
            raise
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> None:
        """Save Postman configuration to file."""
        with open(PostmanConfigHelper.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Saved config to {PostmanConfigHelper.CONFIG_FILE}")
    
    @staticmethod
    def update_config(updates: Dict[str, Any]) -> None:
        """Update specific fields in Postman configuration."""
        config = PostmanConfigHelper.load_config()
        config.update(updates)
        PostmanConfigHelper.save_config(config)
        logger.info(f"Updated config with: {list(updates.keys())}")


class HealthCheckHelper:
    """Helper for backend health verification."""
    
    @staticmethod
    def is_backend_healthy(timeout: int = 5) -> bool:
        """Check if backend is healthy."""
        import httpx
        
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get("http://localhost:8000/api/health")
                is_healthy = response.status_code == 200
                logger.info(f"Backend health check: {'HEALTHY' if is_healthy else 'UNHEALTHY'}")
                return is_healthy
        except Exception as e:
            logger.warning(f"Backend health check failed: {e}")
            return False


# Pytest Fixtures

@pytest.fixture
def test_data_prefix():
    """Generate unique prefix for test data."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    thread_id = current_thread().ident
    return f"Test_{worker_id}_{thread_id}_"


@pytest.fixture
def test_data_manager(test_data_prefix):
    """Create test data manager with cleanup."""
    manager = TestDataManager(prefix=test_data_prefix)
    yield manager
    manager.cleanup()


@pytest.fixture
def postman_config():
    """Load Postman configuration."""
    return PostmanConfigHelper.load_config()


@pytest.fixture
def backend_health():
    """Check backend health."""
    return HealthCheckHelper.is_backend_healthy()


# Hypothesis Strategies

@st.composite
def valid_uid_strategy(draw):
    """Generate valid UID format for Postman."""
    return draw(st.text(
        alphabet='0123456789abcdef',
        min_size=24,
        max_size=24
    ))


@st.composite
def valid_name_strategy(draw):
    """Generate valid name for resources."""
    return draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
        min_size=1,
        max_size=100
    ))


@st.composite
def valid_description_strategy(draw):
    """Generate valid description for resources."""
    return draw(st.text(
        min_size=0,
        max_size=500
    ))


# Utility Functions

def assert_valid_response(response: Dict[str, Any], expected_keys: List[str]) -> None:
    """Assert response has expected structure."""
    for key in expected_keys:
        assert key in response, f"Missing key '{key}' in response"


def assert_valid_error_response(response: Dict[str, Any]) -> None:
    """Assert error response has expected structure."""
    assert "error" in response or "message" in response, "Missing error/message in response"
    assert "status_code" in response or "code" in response, "Missing status_code/code in response"


def log_test_info(test_name: str, info: Dict[str, Any]) -> None:
    """Log test information for debugging."""
    logger.info(f"Test: {test_name}")
    for key, value in info.items():
        logger.debug(f"  {key}: {value}")


__all__ = [
    'TestDataManager',
    'PostmanConfigHelper',
    'HealthCheckHelper',
    'test_data_prefix',
    'test_data_manager',
    'postman_config',
    'backend_health',
    'valid_uid_strategy',
    'valid_name_strategy',
    'valid_description_strategy',
    'assert_valid_response',
    'assert_valid_error_response',
    'log_test_info',
]
