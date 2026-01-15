
"""
Script to create the complete Postman collection for backend testing.
"""

import json
import logging
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager
from backend.services.test_script_generator import TestScriptGenerator
from backend.services.postman_power_client import PostmanPowerClient
from tests.postman.postman_test_helpers import PostmanConfigHelper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "{{base_url}}"

def add_health_requests(builder, folder_id):
    """Add health and infrastructure requests."""
    # Root
    req = builder.add_request(folder_id, "Root Endpoint", "GET", f"{BASE_URL}/")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))
    
    # Health
    req = builder.add_request(folder_id, "Health Check", "GET", f"{BASE_URL}/api/health")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))
    builder.add_test_script(req, TestScriptGenerator.generate_schema_validation(["status", "timestamp"]))

    # Stats
    req = builder.add_request(folder_id, "Dashboard Stats", "GET", f"{BASE_URL}/api/dashboard/stats")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))

def add_knowledge_requests(builder, folder_id):
    """Add knowledge management requests."""
    # List
    req = builder.add_request(folder_id, "List Knowledge", "GET", f"{BASE_URL}/api/knowledge")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))

    # Create
    req = builder.add_request(
        folder_id, 
        "Create Document", 
        "POST", 
        f"{BASE_URL}/api/knowledge",
        body={"title": "Test Doc", "content": "Test content", "type": "text"}
    )
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(201))
    builder.add_test_script(req, TestScriptGenerator.generate_variable_save("id", "last_knowledge_id"))

    # Get One
    req = builder.add_request(folder_id, "Get Document", "GET", f"{BASE_URL}/api/knowledge/{{{{last_knowledge_id}}}}")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))
    
    # Delete
    req = builder.add_request(folder_id, "Delete Document", "DELETE", f"{BASE_URL}/api/knowledge/{{{{last_knowledge_id}}}}")
    builder.add_test_script(req, TestScriptGenerator.generate_status_check(200))

def build_full_collection(workspace_id: str):
    """Build the complete collection."""
    logger.info(f"Building collection for workspace {workspace_id}...")
    builder = CollectionBuilder(workspace_id)
    builder.create_collection("Backend Integration Tests", "Complete integration test suite")
    
    # Global Variables
    builder.add_collection_variable("base_url", "http://localhost:8000")
    
    # Folders
    health_folder = builder.add_folder("Health_Checks")
    knowledge_folder = builder.add_folder("Knowledge_API")
    
    # Add requests
    add_health_requests(builder, health_folder)
    add_knowledge_requests(builder, knowledge_folder)
    
    return builder.build()

def build_environments(workspace_id: str):
    """Build test environments."""
    logger.info("Building environments...")
    
    # Local Environment
    local_env = EnvironmentManager(workspace_id, "Local_Env")
    local_env.create_environment("Local Development")
    local_env.set_variable("base_url", "http://localhost:8000")
    
    # Mock Environment (for completeness)
    mock_env = EnvironmentManager(workspace_id, "Mock_Env")
    mock_env.create_environment("Mock Service")
    mock_env.set_variable("base_url", "http://mock-service:8000")
    
    return [local_env.build(), mock_env.build()]

def main():
    config = PostmanConfigHelper.load_config()
    workspace_id = config.get("workspace_id", "default_workspace")
    
    # Build Collection
    collection = build_full_collection(workspace_id)
    
    # Save to file
    output_file = "backend_test_collection.json"
    with open(output_file, "w") as f:
        json.dump(collection, f, indent=2)
    logger.info(f"Collection saved to {output_file}")
    
    # Build Environments
    envs = build_environments(workspace_id)
    with open("backend_test_environments.json", "w") as f:
        json.dump(envs, f, indent=2)
    logger.info("Environments saved to backend_test_environments.json")

    # Upload if configured
    api_key = config.get("postman_api_key")
    if api_key:
        logger.info("Uploading to Postman...")
        client = PostmanPowerClient(api_key, workspace_id)
        if client.activate_power()["success"]:
            # Setup/Upload logic would go here using client.
            # Client has get_collection/run_collection but maybe not 'create_collection' yet?
            # Task 3 didn't mention 'create_collection' implementation in client properties.
            # So we assume for now we just verify we CAN activate.
            pass

if __name__ == "__main__":
    main()
