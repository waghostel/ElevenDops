# Backend Test Execution Report

## Execution Summary

- **Date:** 2026-01-14
- **Command:** `uv run pytest tests --hypothesis-profile=fast --ignore=tests/test_frontend_e2e.py --ignore=tests/test_frontend_api_props.py --ignore=tests/test_storage_service_props.py`
- **Total Tests:** ~307
- **Passed:** 292
- **Failed:** 12
- **Skipped:** 3
- **Warnings:** 2

## Issues Identified

### 1. Hypothesis Configuration Error

The file `tests/test_storage_service_props.py` contained a collection error:

```
Interrupted: 1 error during collection
```

This is likely caused by the usage of `@settings` on a class, which is deprecated or incorrect in the installed version of Hypothesis. This file was excluded from the main run to allow other tests to proceed.

### 2. Gemini Model Version Mismatch

Several tests failed with `AssertionError` related to Gemini model names:

```
AssertionError: assert 'gemini-3-flash-preview' == 'gemini-2.5-flash-lite'
```

This indicates that the application configuration (likely `backend/config.py`) or default values have been updated to use `gemini-3-flash-preview`, but the tests (e.g., `tests/test_infrastructure_props.py` or `tests/properties/test_script_generation_props.py`) still expect `gemini-2.5-flash-lite`.

### 3. Property Test Failures

There were failures in `tests/properties/test_storage_service_props.py`.

## Recommendations

1.  **Fix Hypothesis Usage:** Update `tests/test_storage_service_props.py` to apply `@settings` to individual test methods or register a profile.
2.  **Update Test Expectations:** Update the tests to match the current default Gemini model (`gemini-3-flash-preview`).
3.  **Investigate Storage Property Failures:** Analyze `tests/properties/test_storage_service_props.py` failures.

## Verified Components

The following components passed their tests:

- `tests/test_backend_api_props.py` (Backend API Client)
- `tests/test_agent_*.py` (Agent Logic)
- Most other property-based tests.
