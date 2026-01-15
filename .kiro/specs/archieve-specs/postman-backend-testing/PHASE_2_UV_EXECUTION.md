# Phase 2: Core Infrastructure - Parallel Execution with UV

**Status:** READY FOR EXECUTION
**Date:** January 15, 2026
**Package Manager:** UV
**Execution Strategy:** Parallel (3 concurrent tasks)
**Estimated Duration:** 2-3 hours

---

## Quick Start Commands

### Verify UV Installation
```bash
uv --version
```

### Install Dependencies
```bash
# Install all dependencies including dev dependencies
uv sync

# Or install specific packages
uv pip install pytest-xdist hypothesis httpx pydantic
```

### Run Phase 2 in Parallel
```bash
# Using pytest-xdist with UV
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v

# With detailed logging
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v -s --log-cli-level=DEBUG

# With coverage
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v --cov=backend --cov-report=html
```

---

## Phase 2 Tasks Overview

### Task 2: Configuration Management (2-3 hours)
**Files to Create:**
- `backend/models/postman_config.py` - PostmanConfig Pydantic model
- `backend/services/postman_config_service.py` - Configuration loading service
- `tests/postman/task_2_test.py` - Tests and property tests

**Key Components:**
- PostmanConfig model with validation
- Configuration file loading from `.postman.json`
- Property test: Configuration Loading Completeness
- Unit tests for edge cases

---

### Task 3: Postman Power Integration (2-3 hours)
**Files to Create:**
- `backend/services/postman_power_client.py` - PostmanPowerClient wrapper
- `tests/postman/task_3_test.py` - Unit tests

**Key Components:**
- PostmanPowerClient class
- Methods: activate_power(), get_collection(), get_environment(), run_collection()
- Unit tests for all methods

---

### Task 4: Backend Health Verification (2-3 hours)
**Files to Create:**
- `backend/services/health_check_service.py` - Health check utility
- `tests/postman/task_4_test.py` - Tests and property tests

**Key Components:**
- check_backend_health() function
- Retry logic with exponential backoff
- Property test: Backend Health Verification
- Unit tests for edge cases

---

## Parallel Execution Workflow

```
Phase 1 (Complete) ✅
    │
    ├─ Task 2 (Config Management)     ─┐
    ├─ Task 3 (Postman Power)         ─┼─ Run in Parallel (2-3 hrs)
    └─ Task 4 (Health Check)          ─┘
         │
         └─ Task 5 (Checkpoint)
```

---

## Execution Steps with UV

### Step 1: Verify Environment
```bash
# Check UV is installed
uv --version

# Check Python version
uv run python --version

# Verify Phase 1 tests pass
uv run pytest tests/postman/test_phase_1_setup.py -v
```

### Step 2: Install Dependencies
```bash
# Sync all dependencies
uv sync

# Verify pytest-xdist is available
uv run pytest --version
uv run pytest --co -q tests/postman/
```

### Step 3: Create Task Test Files
The subagent will create:
- `tests/postman/task_2_test.py`
- `tests/postman/task_3_test.py`
- `tests/postman/task_4_test.py`

### Step 4: Run Parallel Execution
```bash
# Execute all three tasks in parallel
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v

# Monitor with live output
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v -s
```

### Step 5: Run Checkpoint
```bash
# After all parallel tasks complete
uv run pytest tests/postman/checkpoint_5_test.py -v
```

---

## Subagent Execution Plan

The subagent will:

1. **Create Task 2 Implementation**
   - Create `backend/models/postman_config.py` with PostmanConfig model
   - Create `backend/services/postman_config_service.py` with configuration loading
   - Create `tests/postman/task_2_test.py` with property and unit tests
   - Run: `uv run pytest tests/postman/task_2_test.py -v`

2. **Create Task 3 Implementation**
   - Create `backend/services/postman_power_client.py` with PostmanPowerClient
   - Create `tests/postman/task_3_test.py` with unit tests
   - Run: `uv run pytest tests/postman/task_3_test.py -v`

3. **Create Task 4 Implementation**
   - Create `backend/services/health_check_service.py` with health check utility
   - Create `tests/postman/task_4_test.py` with property and unit tests
   - Run: `uv run pytest tests/postman/task_4_test.py -v`

4. **Execute Parallel Tests**
   - Run: `uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v`

5. **Verify Results**
   - Check all tests pass
   - Verify no orphaned test data
   - Generate summary report

---

## UV Commands Reference

```bash
# Sync dependencies
uv sync

# Run pytest
uv run pytest [options]

# Run Python script
uv run python script.py

# Install package
uv pip install package_name

# List installed packages
uv pip list

# Show environment info
uv run python -c "import sys; print(sys.version)"
```

---

## Expected Outcomes

### After Phase 2 Completion

✅ **Task 2 Complete**
- PostmanConfig model with validation
- Configuration loading system
- Property tests passing
- Unit tests passing

✅ **Task 3 Complete**
- PostmanPowerClient wrapper
- All methods implemented
- Unit tests passing

✅ **Task 4 Complete**
- Health check utility with retry logic
- Property tests passing
- Unit tests passing

✅ **All Tests Passing**
- No failures
- No orphaned data
- Ready for Phase 3 checkpoint

---

## Performance Metrics

### Parallel Execution (with UV)
- **Task 2:** 2-3 hours
- **Task 3:** 2-3 hours
- **Task 4:** 2-3 hours
- **Total:** 2-3 hours (parallel)
- **Speedup:** 3x faster than sequential

### Resource Usage
- **CPU Cores:** 3 (one per task)
- **Memory:** ~3 GB total
- **Firestore Connections:** 3
- **Test Data Prefixes:** Task_2_*, Task_3_*, Task_4_*

---

## Troubleshooting with UV

### Issue: "uv: command not found"
```bash
# Install UV
pip install uv

# Or use with Python
python -m uv --version
```

### Issue: "pytest not found"
```bash
# Sync dependencies
uv sync

# Or install pytest
uv pip install pytest pytest-xdist
```

### Issue: "Worker crashed"
```bash
# Reduce parallel workers
uv run pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 2 -v
```

### Issue: "Firestore connection timeout"
```bash
# Increase timeout in conftest.py
# Or run tasks sequentially
uv run pytest tests/postman/task_2_test.py -v
uv run pytest tests/postman/task_3_test.py -v
uv run pytest tests/postman/task_4_test.py -v
```

---

## Next Steps

1. ✅ Review this execution plan
2. ✅ Confirm UV is installed and working
3. ✅ Invoke subagent to execute Phase 2
4. ✅ Monitor parallel execution
5. ✅ Verify all tests pass
6. ✅ Run Phase 3 checkpoint
7. ✅ Continue with Phase 4 (Tasks 6-9 in parallel)

---

## References

- **Dependency Graph:** See `dependency-graph.txt`
- **Quick Start Guide:** See `QUICK_START_PARALLEL.md`
- **Phase 1 Complete:** See `PHASE_1_COMPLETE.md`
- **Full Execution Plan:** See `PHASE_2_EXECUTION_PLAN.md`

