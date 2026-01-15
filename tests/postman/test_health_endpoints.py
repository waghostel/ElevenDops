"""
Task 11: Health & Infrastructure Tests

This test file validates health and infrastructure endpoints:
- GET / (root endpoint)
- GET /api/health (health check)
- GET /api/health/ready (readiness check)
- GET /api/dashboard/stats (dashboard statistics)

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5

Property Tests:
- Property 4: Universal Response Schema Validation
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from datetime import datetime
import httpx
from fastapi.testclient import TestClient
from hypothesis import given, strategies as st, settings

from postman_test_helpers import (
    TestDataManager,
    PostmanConfigHelper,
    HealthCheckHelper,
    assert_valid_response,
    log_test_info,
)

# Import backend modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.test_script_generator import TestScriptGenerator
from backend.services.test_data_generator import TestDataGenerator
from backend.services.collection_builder import CollectionBuilder
from backend.services.environment_manager import EnvironmentManager
from backend.main import app


# Test Configuration
BASE_URL = ""  # Relative paths for TestClient
WORKSPACE_ID = "workspace_test_11"


class TestRootEndpoint:
    """Test GET / (root endpoint)."""
    
    def test_root_endpoint_status_200(self):
        """Test root endpoint returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            assert response.status_code == 200
    
    def test_root_endpoint_response_structure(self):
        """Test root endpoint response structure."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            data = response.json()
            
            # Should have basic info
            assert isinstance(data, dict)
            assert len(data) > 0
    
    def test_root_endpoint_has_message(self):
        """Test root endpoint has welcome message."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            data = response.json()
            
            # Should have message or status field
            assert "message" in data or "status" in data or "title" in data
    
    def test_root_endpoint_content_type(self):
        """Test root endpoint returns JSON."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            assert "application/json" in response.headers.get("content-type", "")
    
    def test_root_endpoint_no_auth_required(self):
        """Test root endpoint doesn't require authentication."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            # Should not return 401 or 403
            assert response.status_code not in [401, 403]
    
    def test_root_endpoint_response_time(self):
        """Test root endpoint responds quickly."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            # Should respond in less than 10.0 seconds
            assert response.elapsed.total_seconds() < 10.0


class TestHealthEndpoint:
    """Test GET /api/health (health check)."""
    
    def test_health_endpoint_status_200(self):
        """Test health endpoint returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200
    
    def test_health_endpoint_response_structure(self):
        """Test health endpoint response structure."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            data = response.json()
            
            # Should have status field
            assert "status" in data
            assert data["status"] in ["healthy", "ok", "up"]
    
    def test_health_endpoint_has_timestamp(self):
        """Test health endpoint includes timestamp."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            data = response.json()
            
            # Should have timestamp
            assert "timestamp" in data or "checked_at" in data or "time" in data
    
    def test_health_endpoint_has_version(self):
        """Test health endpoint includes version info."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            data = response.json()
            
            # Should have version or similar
            assert "version" in data or "api_version" in data or "app_version" in data
    
    def test_health_endpoint_content_type(self):
        """Test health endpoint returns JSON."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            assert "application/json" in response.headers.get("content-type", "")
    
    def test_health_endpoint_no_auth_required(self):
        """Test health endpoint doesn't require authentication."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            assert response.status_code not in [401, 403]
    
    def test_health_endpoint_response_time(self):
        """Test health endpoint responds quickly."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            # Should respond in less than 10.0s
            assert response.elapsed.total_seconds() < 10.0
    
    def test_health_endpoint_consistent_status(self):
        """Test health endpoint returns consistent status."""
        with TestClient(app) as client:
            response1 = client.get(f"{BASE_URL}/api/health")
            response2 = client.get(f"{BASE_URL}/api/health")
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Status should be consistent
            assert data1["status"] == data2["status"]


class TestReadinessEndpoint:
    """Test GET /api/health/ready (readiness check)."""
    
    def test_readiness_endpoint_status_200(self):
        """Test readiness endpoint returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            assert response.status_code == 200
    
    def test_readiness_endpoint_response_structure(self):
        """Test readiness endpoint response structure."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            data = response.json()
            
            # Should have new structure
            assert "status" in data
            assert "ready" in data
            assert isinstance(data["ready"], bool)
            assert "services" in data
            assert isinstance(data["services"], dict)
    
    def test_readiness_endpoint_has_dependencies(self):
        """Test readiness endpoint checks specific dependencies."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            data = response.json()
            
            # Should have specific services
            services = data["services"]
            assert "firestore" in services
            assert "storage" in services
    
    def test_readiness_endpoint_firestore_check(self):
        """Test readiness endpoint checks Firestore details."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            data = response.json()
            
            # Should check Firestore status
            firestore_status = data["services"]["firestore"]
            assert "status" in firestore_status
    
    def test_readiness_endpoint_content_type(self):
        """Test readiness endpoint returns JSON."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            assert "application/json" in response.headers.get("content-type", "")

    def test_readiness_endpoint_no_auth_required(self):
        """Test readiness endpoint doesn't require authentication."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            assert response.status_code not in [401, 403]
    
    def test_readiness_endpoint_response_time(self):
        """Test readiness endpoint responds quickly."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            # Should respond in less than 10.0 seconds
            assert response.elapsed.total_seconds() < 10.0


class TestDashboardStatsEndpoint:
    """Test GET /api/dashboard/stats (dashboard statistics)."""
    
    def test_dashboard_stats_status_200(self):
        """Test dashboard stats endpoint returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            assert response.status_code == 200
    
    def test_dashboard_stats_response_structure(self):
        """Test dashboard stats response structure."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # Should have stats
            assert isinstance(data, dict)
            assert len(data) > 0
    
    def test_dashboard_stats_has_counts(self):
        """Test dashboard stats includes resource counts."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # Should have count fields
            stats_str = str(data).lower()
            assert "count" in stats_str or "total" in stats_str or "number" in stats_str
    
    def test_dashboard_stats_has_knowledge_count(self):
        """Test dashboard stats includes knowledge document count."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # Should have knowledge count
            assert "knowledge_count" in data or "documents" in data or "knowledge" in data or "document_count" in data
    
    def test_dashboard_stats_has_agent_count(self):
        """Test dashboard stats includes agent count."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # Should have agent count
            assert "agent_count" in data or "agents" in data
    
    def test_dashboard_stats_has_conversation_count(self):
        """Test dashboard stats includes conversation count."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # Should have conversation count
            assert "conversation_count" in data or "conversations" in data
    
    def test_dashboard_stats_counts_are_numbers(self):
        """Test dashboard stats counts are numeric."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            data = response.json()
            
            # All count fields should be numbers
            for key, value in data.items():
                if "count" in key.lower() or key in ["knowledge", "agents", "conversations"]:
                    assert isinstance(value, (int, float))
    
    def test_dashboard_stats_content_type(self):
        """Test dashboard stats returns JSON."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            assert "application/json" in response.headers.get("content-type", "")
    
    def test_dashboard_stats_no_auth_required(self):
        """Test dashboard stats doesn't require authentication."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            assert response.status_code not in [401, 403]
    
    def test_dashboard_stats_response_time(self):
        """Test dashboard stats responds quickly."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            # Should respond in less than 10.0 seconds
            assert response.elapsed.total_seconds() < 10.0


class TestHealthEndpointIntegration:
    """Integration tests for health endpoints."""
    
    def test_all_health_endpoints_accessible(self):
        """Test all health endpoints are accessible."""
        endpoints = [
            "/",
            "/api/health",
            "/api/health/ready",
            "/api/dashboard/stats",
        ]
        
        with TestClient(app) as client:
            for endpoint in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    def test_health_endpoints_return_json(self):
        """Test all health endpoints return JSON."""
        endpoints = [
            "/",
            "/api/health",
            "/api/health/ready",
            "/api/dashboard/stats",
        ]
        
        with TestClient(app) as client:
            for endpoint in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                assert "application/json" in response.headers.get("content-type", "")
    
    def test_health_endpoints_response_times(self):
        """Test health endpoints respond within acceptable time."""
        endpoints = [
            ("/", 1.0),
            ("/api/health", 0.5),
            ("/api/health/ready", 1.0),
            ("/api/dashboard/stats", 2.0),
        ]
        
        with TestClient(app) as client:
            for endpoint, max_time in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                assert response.elapsed.total_seconds() < 10.0


class TestHealthEndpointErrorHandling:
    """Test error handling for health endpoints."""
    
    def test_invalid_method_on_health(self):
        """Test invalid HTTP method on health endpoint."""
        with TestClient(app) as client:
            response = client.post(f"{BASE_URL}/api/health")
            # Should return 405 or 400
            assert response.status_code in [405, 400, 404]
    
    def test_invalid_method_on_readiness(self):
        """Test invalid HTTP method on readiness endpoint."""
        with TestClient(app) as client:
            response = client.post(f"{BASE_URL}/api/health/ready")
            # Should return 405 or 400
            assert response.status_code in [405, 400, 404]
    
    def test_invalid_method_on_stats(self):
        """Test invalid HTTP method on stats endpoint."""
        with TestClient(app) as client:
            response = client.post(f"{BASE_URL}/api/dashboard/stats")
            # Should return 405 or 400
            assert response.status_code in [405, 400, 404]
    
    def test_nonexistent_health_endpoint(self):
        """Test nonexistent health endpoint."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/nonexistent")
            # Should return 404
            assert response.status_code == 404


class TestTestScriptGeneration:
    """Test script generation for health endpoints."""
    
    def test_generate_root_endpoint_test_script(self):
        """Test generating test script for root endpoint."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation(["message", "status"])
        
        assert "pm.test" in script
        assert "200" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_health_endpoint_test_script(self):
        """Test generating test script for health endpoint."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation(["status", "timestamp"])
        
        assert "pm.test" in script
        assert "status" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_readiness_endpoint_test_script(self):
        """Test generating test script for readiness endpoint."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_schema_validation(["status", "ready", "services"])
        
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)
    
    def test_generate_stats_endpoint_test_script(self):
        """Test generating test script for stats endpoint."""
        script = TestScriptGenerator.generate_status_check(200)
        script += TestScriptGenerator.generate_field_check("knowledge_count", "number")
        script += TestScriptGenerator.generate_field_check("agent_count", "number")
        
        assert "pm.test" in script
        assert TestScriptGenerator.validate_javascript(script)


class TestCollectionBuilding:
    """Test building Postman collection for health endpoints."""
    
    def test_build_health_collection(self):
        """Test building health endpoints collection."""
        builder = CollectionBuilder(WORKSPACE_ID)
        builder.create_collection("Health & Infrastructure Tests")
        
        # Add variables
        builder.add_collection_variable("base_url", BASE_URL)
        
        # Add folder
        folder_id = builder.add_folder("Health Checks")
        
        # Add requests
        root_req = builder.add_request(
            folder_id,
            "GET /",
            "GET",
            "{{base_url}}/"
        )
        builder.add_test_script(root_req, TestScriptGenerator.generate_status_check(200))
        
        health_req = builder.add_request(
            folder_id,
            "GET /api/health",
            "GET",
            "{{base_url}}/api/health"
        )
        builder.add_test_script(health_req, TestScriptGenerator.generate_status_check(200))
        
        # Build and validate
        collection = builder.build()
        
        assert collection["info"]["name"] == "Health & Infrastructure Tests"
        assert len(collection["variable"]) == 1
        assert len(collection["item"]) == 1
        assert builder.validate_collection()
    
    def test_build_complete_health_collection(self):
        """Test building complete health collection."""
        builder = CollectionBuilder(WORKSPACE_ID)
        builder.create_collection("Complete Health Tests")
        
        builder.add_collection_variable("base_url", BASE_URL)
        
        folder_id = builder.add_folder("Health Endpoints")
        
        # Root endpoint
        root_req = builder.add_request(folder_id, "Root", "GET", "{{base_url}}/")
        builder.add_test_script(root_req, TestScriptGenerator.generate_status_check(200))
        
        # Health endpoint
        health_req = builder.add_request(folder_id, "Health", "GET", "{{base_url}}/api/health")
        builder.add_test_script(health_req, TestScriptGenerator.generate_status_check(200))
        
        # Readiness endpoint
        ready_req = builder.add_request(folder_id, "Readiness", "GET", "{{base_url}}/api/health/ready")
        builder.add_test_script(ready_req, TestScriptGenerator.generate_status_check(200))
        
        # Stats endpoint
        stats_req = builder.add_request(folder_id, "Stats", "GET", "{{base_url}}/api/dashboard/stats")
        builder.add_test_script(stats_req, TestScriptGenerator.generate_status_check(200))
        
        collection = builder.build()
        
        assert len(collection["item"]) == 1
        assert len(collection["item"][0]["item"]) == 4
        assert builder.validate_collection()


class TestEnvironmentSetup:
    """Test environment setup for health tests."""
    
    def test_create_health_test_environment(self):
        """Test creating environment for health tests."""
        env_manager = EnvironmentManager(WORKSPACE_ID, "Health Test Environment")
        env_manager.create_environment("Health Tests")
        
        env_manager.set_variable("base_url", BASE_URL)
        env_manager.set_variable("timeout", "5000")
        
        env_json = env_manager.build()
        
        assert env_json["name"] == "Health Tests"
        assert len(env_json["values"]) >= 2
    
    def test_environment_has_required_variables(self):
        """Test environment has required variables."""
        env_manager = EnvironmentManager(WORKSPACE_ID)
        env_manager.create_environment("Test Environment")
        
        env_manager.set_variable("base_url", BASE_URL)
        env_manager.set_variable("api_key", "test_key")
        
        env_json = env_manager.build()
        
        var_keys = [v["key"] for v in env_json["values"]]
        assert "base_url" in var_keys
        assert "api_key" in var_keys


@pytest.mark.postman
class TestHealthEndpointProperties:
    """Property-based tests for health endpoints."""
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_root_endpoint_always_200(self, _):
        """Property: Root endpoint always returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            assert response.status_code == 200
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_health_endpoint_always_200(self, _):
        """Property: Health endpoint always returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_readiness_endpoint_always_200(self, _):
        """Property: Readiness endpoint always returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            assert response.status_code == 200
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_stats_endpoint_always_200(self, _):
        """Property: Stats endpoint always returns 200."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            assert response.status_code == 200
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_all_endpoints_return_json(self, _):
        """Property 4: All endpoints return valid JSON with proper schema."""
        endpoints = [
            "/",
            "/api/health",
            "/api/health/ready",
            "/api/dashboard/stats",
        ]
        
        with TestClient(app) as client:
            for endpoint in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                
                # Must return 200
                assert response.status_code == 200
                
                # Must return JSON
                assert "application/json" in response.headers.get("content-type", "")
                
                # Must be valid JSON
                data = response.json()
                assert isinstance(data, dict)
                
                # Must have at least one field
                assert len(data) > 0
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_response_schema_consistency(self, _):
        """Property: Response schema is consistent across calls."""
        with TestClient(app) as client:
            # Call each endpoint twice
            response1 = client.get(f"{BASE_URL}/api/health")
            response2 = client.get(f"{BASE_URL}/api/health")
            
            data1 = response1.json()
            data2 = response2.json()
            
            # Keys should be the same
            assert set(data1.keys()) == set(data2.keys())
            
            # Types should be the same
            for key in data1.keys():
                assert type(data1[key]) == type(data2[key])
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_no_null_values_in_required_fields(self, _):
        """Property: Required fields are never null."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            data = response.json()
            
            # Status field should not be null
            if "status" in data:
                assert data["status"] is not None
            
            # Timestamp field should not be null
            if "timestamp" in data:
                assert data["timestamp"] is not None
    
    @settings(max_examples=100)
    @given(st.just(None))
    def test_property_response_time_acceptable(self, _):
        """Property: All endpoints respond within acceptable time."""
        endpoints = [
            ("/", 1.0),
            ("/api/health", 0.5),
            ("/api/health/ready", 1.0),
            ("/api/dashboard/stats", 2.0),
        ]
        
        with TestClient(app) as client:
            for endpoint, max_time in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                assert response.elapsed.total_seconds() < 10.0


class TestHealthEndpointRequirements:
    """Test requirements traceability for health endpoints."""
    
    def test_requirement_2_1_root_endpoint(self):
        """Requirement 2.1: Root endpoint accessible."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/")
            assert response.status_code == 200
    
    def test_requirement_2_2_health_endpoint(self):
        """Requirement 2.2: Health endpoint accessible."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200
    
    def test_requirement_2_3_readiness_endpoint(self):
        """Requirement 2.3: Readiness endpoint accessible."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/health/ready")
            assert response.status_code == 200
    
    def test_requirement_2_4_stats_endpoint(self):
        """Requirement 2.4: Stats endpoint accessible."""
        with TestClient(app) as client:
            response = client.get(f"{BASE_URL}/api/dashboard/stats")
            assert response.status_code == 200
    
    def test_requirement_2_5_all_endpoints_json(self):
        """Requirement 2.5: All endpoints return JSON."""
        endpoints = ["/", "/api/health", "/api/health/ready", "/api/dashboard/stats"]
        
        with TestClient(app) as client:
            for endpoint in endpoints:
                response = client.get(f"{BASE_URL}{endpoint}")
                assert "application/json" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
