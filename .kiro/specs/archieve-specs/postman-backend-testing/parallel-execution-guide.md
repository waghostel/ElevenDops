# Parallel Execution Guide - Postman Backend Testing

## Quick Start

### For Developers (Local Development)
```bash
# Phase 1: Foundation (sequential)
python -m pytest tests/postman/task_1_test.py -v

# Phase 2: Core Infrastructure (parallel)
pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n auto

# Phase 4: Components (parallel)
pytest tests/postman/task_6_test.py tests/postman/task_7_test.py tests/postman/task_8_test.py tests/postman/task_9_test.py -n auto

# Phase 6: API Tests (parallel)
pytest tests/postman/task_11_test.py tests/postman/task_12_test.py tests/postman/task_13_test.py tests/postman/task_14_test.py tests/postman/task_15_test.py tests/postman/task_16_test.py tests/postman/task_17_test.py tests/postman/task_18_test.py tests/postman/task_19_test.py -n auto
```

### For CI/CD (GitHub Actions)
See `.github/workflows/postman-tests.yml` for matrix strategy

---

## Detailed Execution Plan

### Phase 1: Foundation (30 minutes)
**Status:** SEQUENTIAL (blocking all other tasks)

```bash
# Task 1: Set up project structure and dependencies
python -m pytest tests/postman/task_1_test.py -v

# Verify:
# ✅ tests/postman/ directory created
# ✅ postman_test_helpers.py created
# ✅ pyproject.toml updated with httpx, hypothesis, pytest
```

**Checkpoint:** All files created and dependencies installed

---

### Phase 2: Core Infrastructure (2-3 hours)
**Status:** PARALLEL (3 independent tasks)

#### Option A: Python Threading (Recommended for MVP)

```python
# run_phase_2.py
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys

def run_task(task_num):
    """Run a single task and return result"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/postman/task_{task_num}_test.py", "-v"],
        capture_output=True,
        text=True
    )
    return task_num, result.returncode, result.stdout, result.stderr

def main():
    tasks = [2, 3, 4]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_task, task): task for task in tasks}
        
        results = {}
        for future in as_completed(futures):
            task_num, returncode, stdout, stderr = future.result()
            results[task_num] = (returncode, stdout, stderr)
            
            if returncode == 0:
                print(f"✅ Task {task_num} PASSED")
            else:
                print(f"❌ Task {task_num} FAILED")
                print(stderr)
    
    # Check all passed
    if all(rc == 0 for rc, _, _ in results.values()):
        print("\n✅ Phase 2 PASSED - All tasks completed successfully")
        return 0
    else:
        print("\n❌ Phase 2 FAILED - Some tasks failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run:**
```bash
python run_phase_2.py
```

#### Option B: Pytest Parallel Plugin

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run Phase 2 in parallel
pytest tests/postman/task_2_test.py tests/postman/task_3_test.py tests/postman/task_4_test.py -n 3 -v
```

#### Option C: GitHub Actions Matrix

```yaml
# .github/workflows/phase-2.yml
name: Phase 2 - Core Infrastructure

on: [push, pull_request]

jobs:
  phase-2:
    strategy:
      matrix:
        task: [2, 3, 4]
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e . pytest hypothesis httpx
      
      - name: Run Task ${{ matrix.task }}
        run: pytest tests/postman/task_${{ matrix.task }}_test.py -v
```

**Checkpoint:** All Phase 2 tests pass

---

### Phase 3: Checkpoint (15 minutes)
**Status:** SEQUENTIAL (validation only)

```bash
# Task 5: Checkpoint
python -m pytest tests/postman/checkpoint_5_test.py -v

# Verify:
# ✅ All Phase 2 tests passed
# ✅ Configuration loaded correctly
# ✅ Postman Power client initialized
# ✅ Backend health verified
```

---

### Phase 4: Component Implementation (3-4 hours)
**Status:** PARALLEL (4 independent tasks)

```bash
# Option A: Pytest Parallel
pytest tests/postman/task_6_test.py tests/postman/task_7_test.py tests/postman/task_8_test.py tests/postman/task_9_test.py -n 4 -v

# Option B: Python Threading
python run_phase_4.py

# Option C: GitHub Actions Matrix
# See .github/workflows/phase-4.yml
```

**Checkpoint:** All Phase 4 tests pass

---

### Phase 5: Checkpoint (15 minutes)
**Status:** SEQUENTIAL (validation only)

```bash
# Task 10: Checkpoint
python -m pytest tests/postman/checkpoint_10_test.py -v

# Verify:
# ✅ All Phase 4 tests passed
# ✅ EnvironmentManager working
# ✅ TestScriptGenerator working
# ✅ TestDataGenerator working
# ✅ CollectionBuilder working
```

---

### Phase 6: API Test Implementation (6-8 hours)
**Status:** PARALLEL (9 independent tasks)

#### Important: Test Data Isolation

Before running Phase 6 in parallel, ensure test data isolation:

```python
# tests/postman/conftest.py
import pytest
import os
from threading import current_thread

@pytest.fixture(scope="function")
def test_data_prefix():
    """Generate unique prefix for test data"""
    task_id = os.environ.get("PYTEST_XDIST_WORKER", "main")
    thread_id = current_thread().ident
    return f"Test_{task_id}_{thread_id}_"

@pytest.fixture(autouse=True)
def cleanup_test_data(test_data_prefix):
    """Cleanup test data after each test"""
    yield
    # Cleanup logic here
    pass
```

#### Run Phase 6

```bash
# Option A: Pytest Parallel (Recommended)
pytest tests/postman/task_11_test.py tests/postman/task_12_test.py tests/postman/task_13_test.py tests/postman/task_14_test.py tests/postman/task_15_test.py tests/postman/task_16_test.py tests/postman/task_17_test.py tests/postman/task_18_test.py tests/postman/task_19_test.py -n 9 -v

# Option B: Python Threading with Staggered Start
python run_phase_6.py --stagger 200ms

# Option C: GitHub Actions Matrix
# See .github/workflows/phase-6.yml
```

**Checkpoint:** All Phase 6 tests pass

---

### Phase 7: Checkpoint (15 minutes)
**Status:** SEQUENTIAL (validation only)

```bash
# Task 20: Checkpoint
python -m pytest tests/postman/checkpoint_20_test.py -v

# Verify:
# ✅ All Phase 6 tests passed
# ✅ All API endpoints tested
# ✅ All property tests passed (100+ iterations each)
# ✅ No orphaned test data
```

---

### Phase 8: Integration & Orchestration (4-5 hours)
**Status:** SEQUENTIAL (dependent chain)

```bash
# Task 21: Integration Workflow Tests
pytest tests/postman/task_21_test.py -v

# Task 22: Cleanup Requests
pytest tests/postman/task_22_test.py -v

# Task 23: Test Orchestration Component
pytest tests/postman/task_23_test.py -v

# Task 24: Results Reporter Component
pytest tests/postman/task_24_test.py -v
```

---

### Phase 9: CLI & Final Assembly (3-4 hours)
**Status:** SEQUENTIAL (dependent chain)

```bash
# Task 25: CLI Test Runner
pytest tests/postman/task_25_test.py -v

# Task 26: Test Idempotence
pytest tests/postman/task_26_test.py -v

# Task 27: Complete Test Collection
pytest tests/postman/task_27_test.py -v

# Task 28: Final Integration Testing
pytest tests/postman/task_28_test.py -v

# Task 29: Documentation and CI/CD Integration
pytest tests/postman/task_29_test.py -v

# Task 30: Final Checkpoint
pytest tests/postman/task_30_test.py -v
```

---

## Parallel Execution Scripts

### Python Threading Script (run_phase_2.py)

```python
#!/usr/bin/env python3
"""
Run Phase 2 tasks in parallel using ThreadPoolExecutor
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import sys
import time
from typing import Dict, Tuple

def run_task(task_num: int) -> Tuple[int, int, str, str]:
    """Run a single task and return result"""
    print(f"[Task {task_num}] Starting...")
    start_time = time.time()
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/postman/task_{task_num}_test.py", "-v"],
        capture_output=True,
        text=True
    )
    
    duration = time.time() - start_time
    print(f"[Task {task_num}] Completed in {duration:.1f}s")
    
    return task_num, result.returncode, result.stdout, result.stderr

def main():
    tasks = [2, 3, 4]
    results: Dict[int, Tuple[int, str, str]] = {}
    
    print("=" * 60)
    print("Phase 2: Core Infrastructure (Parallel Execution)")
    print("=" * 60)
    print(f"Running {len(tasks)} tasks in parallel...\n")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_task, task): task for task in tasks}
        
        for future in as_completed(futures):
            task_num, returncode, stdout, stderr = future.result()
            results[task_num] = (returncode, stdout, stderr)
            
            if returncode == 0:
                print(f"✅ Task {task_num} PASSED")
            else:
                print(f"❌ Task {task_num} FAILED")
                if stderr:
                    print(f"   Error: {stderr[:200]}")
    
    print("\n" + "=" * 60)
    print("Phase 2 Summary")
    print("=" * 60)
    
    passed = sum(1 for rc, _, _ in results.values() if rc == 0)
    failed = len(results) - passed
    
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    
    if failed == 0:
        print("\n✅ Phase 2 PASSED - All tasks completed successfully")
        return 0
    else:
        print("\n❌ Phase 2 FAILED - Some tasks failed")
        for task_num, (rc, stdout, stderr) in results.items():
            if rc != 0:
                print(f"\nTask {task_num} output:")
                print(stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### GitHub Actions Workflow (phase-6.yml)

```yaml
name: Phase 6 - API Test Implementation

on: [push, pull_request]

jobs:
  phase-6:
    strategy:
      matrix:
        task: [11, 12, 13, 14, 15, 16, 17, 18, 19]
      max-parallel: 9
    
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest hypothesis httpx pytest-xdist
      
      - name: Run Task ${{ matrix.task }}
        env:
          PYTEST_XDIST_WORKER: task-${{ matrix.task }}
        run: pytest tests/postman/task_${{ matrix.task }}_test.py -v
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-task-${{ matrix.task }}
          path: test-results/
```

---

## Monitoring and Debugging

### Real-time Monitoring

```bash
# Monitor test execution with live output
pytest tests/postman/ -n auto -v --tb=short

# Monitor with detailed logging
pytest tests/postman/ -n auto -v --log-cli-level=DEBUG

# Monitor with coverage
pytest tests/postman/ -n auto --cov=backend --cov-report=html
```

### Debugging Failed Tasks

```bash
# Run single task with full output
pytest tests/postman/task_12_test.py -v -s --tb=long

# Run with pdb debugger
pytest tests/postman/task_12_test.py -v --pdb

# Run with detailed logging
pytest tests/postman/task_12_test.py -v --log-cli-level=DEBUG
```

### Cleanup After Failed Runs

```bash
# Cleanup test data
python -m pytest tests/postman/cleanup_test.py -v

# Verify cleanup
python -c "from backend.services.firestore_data_service import FirestoreDataService; \
           fs = FirestoreDataService(); \
           orphaned = fs.find_orphaned_test_data(); \
           print(f'Orphaned records: {len(orphaned)}')"
```

---

## Performance Optimization

### Staggered Start (Reduce Rate Limiting)

```python
# run_phase_6_staggered.py
import time
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys

def run_task_staggered(task_num: int, delay: float):
    """Run task with initial delay"""
    time.sleep(delay)
    return subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/postman/task_{task_num}_test.py", "-v"],
        capture_output=True,
        text=True
    )

tasks = list(range(11, 20))  # Tasks 11-19
stagger_delay = 0.2  # 200ms between starts

with ThreadPoolExecutor(max_workers=9) as executor:
    futures = [
        executor.submit(run_task_staggered, task, i * stagger_delay)
        for i, task in enumerate(tasks)
    ]
    
    for future in futures:
        result = future.result()
        print(f"Task completed with return code: {result.returncode}")
```

### Connection Pooling

```python
# conftest.py
import pytest
from backend.services.firestore_data_service import FirestoreDataService

@pytest.fixture(scope="session")
def firestore_pool():
    """Create connection pool for all tests"""
    pool = FirestoreDataService.create_connection_pool(max_connections=16)
    yield pool
    pool.close()

@pytest.fixture
def firestore_client(firestore_pool):
    """Get client from pool"""
    return firestore_pool.get_client()
```

---

## Troubleshooting

### Issue: Tests fail with "Rate limit exceeded"
**Solution:** Reduce parallel workers or add stagger delay
```bash
pytest tests/postman/ -n 4 -v  # Reduce from 9 to 4
```

### Issue: Tests fail with "Firestore connection timeout"
**Solution:** Increase connection pool size
```python
# conftest.py
FirestoreDataService.create_connection_pool(max_connections=32)
```

### Issue: Tests fail with "Orphaned test data"
**Solution:** Run cleanup before tests
```bash
pytest tests/postman/cleanup_test.py -v
pytest tests/postman/ -n auto -v
```

### Issue: Checkpoint fails with "Some tasks incomplete"
**Solution:** Check individual task logs
```bash
pytest tests/postman/task_12_test.py -v -s --tb=long
```

---

## Best Practices

1. **Always run Phase 1 first** - Foundation must be complete
2. **Run checkpoints sequentially** - Ensure all tasks passed
3. **Use unique test data prefixes** - Prevent conflicts
4. **Implement cleanup hooks** - Prevent orphaned data
5. **Monitor backend load** - Avoid rate limiting
6. **Stagger parallel starts** - Reduce peak load
7. **Use connection pooling** - Improve performance
8. **Log all test data** - Enable debugging
9. **Verify cleanup** - Check for orphaned records
10. **Document failures** - Track issues for improvement

---

## Summary

| Phase | Tasks | Duration | Type | Speedup |
|-------|-------|----------|------|---------|
| 1 | 1 | 30 min | Sequential | - |
| 2 | 2,3,4 | 2-3 hrs | **Parallel** | 2-3x |
| 3 | 5 | 15 min | Sequential | - |
| 4 | 6,7,8,9 | 3-4 hrs | **Parallel** | 2-3x |
| 5 | 10 | 15 min | Sequential | - |
| 6 | 11-19 | 6-8 hrs | **Parallel** | 2.5-3x |
| 7 | 20 | 15 min | Sequential | - |
| 8 | 21-24 | 4-5 hrs | Sequential | - |
| 9 | 25-30 | 3-4 hrs | Sequential | - |
| **TOTAL** | **30** | **20-25 hrs** | **Mixed** | **2-2.5x** |

