# Postman Backend Testing Guide

This guide details the backend testing infrastructure for the ElevenDops project, designed to ensure API reliability through a hybrid approach of Python-based property testing and Postman collection orchestration.

## Overview

The testing system consists of two main pillars:

1.  **Python Tests (`tests/postman/`)**: These tests use `pytest` and `hypothesis` to generate test data, validate properties (like idempotence and schema compliance), and unit test the testing utilities themselves.
2.  **Postman Orchestration**: A structured way to run API tests that mirrors real-world usage. _Currently, this is simulated via `TestOrchestrator` but is designed to be replaced with actual Newman executions._

## Setup

### Prerequisites

- Python 3.10+
- `uv` package manager (recommended) or `pip`
- Local backend running on `http://localhost:8000`

### Installation

Ensure dev dependencies are installed:

```bash
uv sync
# OR
pip install -e ".[dev]"
```

## Running Tests

### 1. Running Python Tests

These tests verify the logic of the test generators, health checks, and property validation.

```bash
pytest tests/postman
```

### 2. Running the CLI Runner

The CLI runner simulates the execution of Postman collections. It verifies that the orchestration logic (health check -> run collection -> report) works as expected.

```bash
# Run the full suite with health check
python -m tests.postman.cli_runner run --check-health

# Run a specific folder (Simulated)
python -m tests.postman.cli_runner run --folder "Health & Infrastructure"
```

## Architecture

### Components

- **`TestOrchestrator` (`test_orchestrator.py`)**: The central controller. It manages the lifecycle of a test run.

  - _Current State_: Simulates Postman runs by returning mock `TestResult` objects.
  - _Future Goal_: Integrate with `newman` (the Postman CLI) to execute the actual `.postman.json` collection against the backend.

- **`CollectionBuilder` (`create_full_collection.py`)**: Programmatically generates the `.postman.json` file. This ensures that our API definition in code matches the test collection.

- **`ResultsReporter` (`results_reporter.py`)**: Parses results and generates markdown summaries (`test_report.md`).

### Test Data Management

The system uses a `TestDataManager` to track resources created during tests (Agents, Audio files, etc.) and ensures they are cleaned up, maintaining test idempotence.

## Extending the System

### Adding New Tests

1.  **Define the Request**: Update `CollectionBuilder` to include the new API endpoint.
2.  **Add Property Test**: Create a new test file in `tests/postman/` (e.g., `task_NN_test.py`) to verify specific properties of that endpoint (e.g., "created resource is always retrievable").

### Switching to Real Postman Execution

To move from simulation to real execution:

1.  Install Newman: `npm install -g newman`
2.  Update `TestOrchestrator.run_test_collection` to use `subprocess.run` to call `newman run`.
3.  Parse the Newman JSON report in `ResultsReporter`.
