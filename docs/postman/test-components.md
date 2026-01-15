# Test Components

## CollectionBuilder

Programmatically builds Postman collections with folders, requests, and test scripts.

```python
from backend.services.collection_builder import CollectionBuilder

builder = CollectionBuilder("workspace-id")
builder.create_collection("API Tests", "Comprehensive tests")

folder_id = builder.add_folder("Health")
builder.add_request(folder_id, "Check Health", "GET", "{{base_url}}/api/health")
collection = builder.build()
```

## TestScriptGenerator

Generates JavaScript test scripts for Postman.

```python
from backend.services.test_script_generator import TestScriptGenerator

# Status check
script = TestScriptGenerator.generate_status_check(200)

# Field validation
script = TestScriptGenerator.generate_field_check("status", "healthy")

# Save variable
script = TestScriptGenerator.generate_variable_save("created_id", "id")
```

## TestDataGenerator

Creates valid test data for API requests.

```python
from backend.services.test_data_generator import TestDataGenerator

doc = TestDataGenerator.generate_knowledge_document()
audio = TestDataGenerator.generate_audio_request(knowledge_id)
agent = TestDataGenerator.generate_agent_config()
```

## EnvironmentManager

Manages Postman environment variables.

```python
from backend.services.environment_manager import EnvironmentManager

env = EnvironmentManager("workspace-id", "Test Environment")
env.set_variable("base_url", "http://localhost:8000")
env.set_variable("api_key", "secret", is_secret=True)
env_json = env.build()
```

## TestOrchestrator

Coordinates test execution and health checks.

## ResultsReporter

Parses test results and generates summaries.
