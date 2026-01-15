"""
Pytest configuration for Postman backend testing.

This module provides shared fixtures and configuration for all Postman tests.
"""

import os
import sys
import logging
from pathlib import Path
from threading import current_thread

import pytest
from hypothesis import settings, HealthCheck

# Add tests/postman to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from postman_test_helpers import (
    TestDataManager,
    PostmanConfigHelper,
    HealthCheckHelper,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Hypothesis settings for property-based tests
settings.register_profile("default", max_examples=100, deadline=None)
settings.register_profile("ci", max_examples=200, deadline=None)
settings.register_profile("dev", max_examples=50, deadline=None)

# Use CI profile in CI environment, otherwise use default
profile = "ci" if os.environ.get("CI") else "default"
settings.load_profile(profile)


@pytest.fixture(scope="session")
def session_config():
    """Load configuration once per test session."""
    logger.info("Loading Postman configuration for session")
    config = PostmanConfigHelper.load_config()
    logger.info(f"Configuration loaded: {list(config.keys())}")
    return config


@pytest.fixture(scope="session")
def backend_available():
    """Check if backend is available for the entire session."""
    logger.info("Checking backend availability")
    available = HealthCheckHelper.is_backend_healthy(timeout=10)
    if not available:
        logger.warning("Backend is not available - some tests may be skipped")
    return available


@pytest.fixture
def test_data_prefix():
    """Generate unique prefix for test data to avoid conflicts in parallel execution."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    thread_id = current_thread().ident
    prefix = f"Test_{worker_id}_{thread_id}_"
    logger.debug(f"Generated test data prefix: {prefix}")
    return prefix


@pytest.fixture
def test_data_manager(test_data_prefix):
    """Create and manage test data with automatic cleanup."""
    manager = TestDataManager(prefix=test_data_prefix)
    logger.info(f"Created test data manager with prefix: {test_data_prefix}")
    
    yield manager
    
    # Cleanup after test
    manager.cleanup()
    logger.info(f"Cleaned up test data for prefix: {test_data_prefix}")


@pytest.fixture
def postman_config(session_config):
    """Provide Postman configuration to tests."""
    return session_config


@pytest.fixture
def backend_health(backend_available):
    """Provide backend health status to tests."""
    return backend_available


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "postman: mark test as a Postman backend test"
    )
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    logger.info("Pytest configured with custom markers")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add postman marker to all tests in this directory
        item.add_marker(pytest.mark.postman)
        
        # Add property marker if test name contains "property"
        if "property" in item.nodeid.lower():
            item.add_marker(pytest.mark.property)
        
        # Add integration marker if test name contains "integration"
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Automatically log test information."""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Completed test: {request.node.name}")


def pytest_runtest_logreport(report):
    """Log test results."""
    if report.when == "call":
        if report.outcome == "passed":
            logger.info(f"✅ Test passed: {report.nodeid}")
        elif report.outcome == "failed":
            logger.error(f"❌ Test failed: {report.nodeid}")
        elif report.outcome == "skipped":
            logger.warning(f"⏭️  Test skipped: {report.nodeid}")
