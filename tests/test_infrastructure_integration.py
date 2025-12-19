import pytest
import subprocess
import time
import requests
import os

@pytest.mark.integration
class TestDockerInfrastructure:
    """Integration tests for Docker Compose infrastructure."""

    def test_docker_services_availability(self):
        """
        Feature: local-dev-infrastructure, Property 5: Docker Compose Service Availability
        Validates: Requirements 4.1, 4.2
        Verify both services start and become healthy within 60 seconds
        """
        
        # Check if docker-compose file exists
        compose_file = "docker-compose.dev.yml"
        assert os.path.exists(compose_file), f"{compose_file} not found"

        try:
            # Start services
            print("Starting Docker services...")
            subprocess.run(
                ["docker-compose", "-f", compose_file, "up", "-d"], 
                check=True, 
                capture_output=True
            )

            # Wait for services to be healthy provided in docker-compose healthchecks
            # We will poll the endpoints manually to confirm accessibility
            
            firestore_url = "http://localhost:8080/"
            gcs_url = "http://localhost:4443/storage/v1/b"
            
            start_time = time.time()
            timeout = 60
            
            firestore_healthy = False
            gcs_healthy = False
            
            while time.time() - start_time < timeout:
                if not firestore_healthy:
                    try:
                        response = requests.get(firestore_url, timeout=1)
                        if response.status_code == 200:
                            firestore_healthy = True
                            print("Firestore Emulator is healthy!")
                    except requests.RequestException:
                        pass
                
                if not gcs_healthy:
                    try:
                        response = requests.get(gcs_url, timeout=1)
                        if response.status_code == 200:
                            gcs_healthy = True
                            print("GCS Emulator is healthy!")
                    except requests.RequestException:
                        pass
                
                if firestore_healthy and gcs_healthy:
                    break
                
                time.sleep(2)
            
            assert firestore_healthy, "Firestore Emulator failed to become healthy within 60 seconds"
            assert gcs_healthy, "GCS Emulator failed to become healthy within 60 seconds"

        finally:
            # Tear down services
            print("\nStopping Docker services...")
            subprocess.run(
                ["docker-compose", "-f", compose_file, "down"], 
                check=True,
                capture_output=True
            )
