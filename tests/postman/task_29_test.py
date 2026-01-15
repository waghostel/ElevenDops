
"""
Tests for Task 29: Complete Test Collection Creation
"""

import sys
import pytest
from unittest.mock import MagicMock, patch
from tests.postman.create_full_collection import build_full_collection, build_environments

def test_build_full_collection_structure():
    """Test that full collection has correct structure."""
    collection = build_full_collection("workspace_id")
    
    assert collection["info"]["name"] == "Backend Integration Tests"
    assert len(collection["variable"]) >= 1
    
    # Check folders
    folder_names = [item["name"] for item in collection["item"]]
    assert "Health_Checks" in folder_names
    assert "Knowledge_API" in folder_names
    
    # Check Health Requests
    health_folder = next(item for item in collection["item"] if item["name"] == "Health_Checks")
    req_names = [item["name"] for item in health_folder["item"]]
    assert "Root Endpoint" in req_names
    assert "Health Check" in req_names
    
    # Check Scripts
    health_req = next(item for item in health_folder["item"] if item["name"] == "Health Check")
    assert len(health_req["event"]) > 0  # Has scripts

def test_build_environments_structure():
    """Test that environments are built correctly."""
    envs = build_environments("workspace_id")
    
    assert len(envs) == 2
    local_env = next(e for e in envs if e["name"] == "Local Development")
    mock_env = next(e for e in envs if e["name"] == "Mock Service")
    
    assert local_env is not None
    assert mock_env is not None
    
    # Check variables
    local_vars = {v["key"]: v["value"] for v in local_env["values"]}
    assert local_vars["base_url"] == "http://localhost:8000"
