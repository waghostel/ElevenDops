# Backend Test Error Report
**Generated:** 2025-12-22  
**Total Tests:** 167 | **Passed:** 148 | **Failed:** 11 | **Skipped:** 8

---

## 🔴 URGENT - Critical Production Issues

### [ ] 1. Audio API Error Handling Returns Wrong Status Code
**File:** `tests/test_audio_api_props.py::test_audio_generate_error_handling`  
**Issue:** API returns HTTP 500 instead of expected HTTP 502 for ElevenLabs errors  
**Impact:** Incorrect error responses to clients, breaks API contract  
**Root Cause:** Async mock not awaited properly - `'coroutine' object has no attribute 'audio_id'`  
**Fix Location:** `backend/api/audio.py` - Error handling in audio generation endpoint

### [ ] 2. Production Config Validation Missing GCP Project Check
**Files:** 
- `tests/test_config_props.py::test_production_mode_raises_for_missing_gcp_project`
- `tests/test_config_props.py::test_production_mode_raises_for_all_missing_critical_vars`

**Issue:** Production mode doesn't validate `GOOGLE_CLOUD_PROJECT` environment variable  
**Impact:** App could start in production without proper GCP configuration, leading to runtime failures  
**Fix Location:** `backend/config.py` - Add `GOOGLE_CLOUD_PROJECT` to critical config validation

### [ ] 3. Agent Answer Style Mapping Uses Chinese Instead of English Keywords
**File:** `tests/test_agent_service_props.py::test_answer_style_mapping`  
**Issue:** System prompts are in Chinese, tests expect English keywords ("professional", "friendly", "educational")  
**Impact:** Test-code mismatch - either tests or prompts need alignment  
**Fix Location:** `backend/services/elevenlabs_service.py` or update test expectations

---

## 🟡 MEDIUM - Infrastructure & Integration Issues

### [ ] 4. Docker Services Not Running (Docker Desktop Issue)
**File:** `tests/test_infrastructure_integration.py::test_docker_services_availability`  
**Issue:** `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`  
**Impact:** Cannot run integration tests with Firestore/GCS emulators  
**Environment:** Docker Desktop not running on Windows  
**Action:** Start Docker Desktop before running integration tests

### [ ] 5. Firestore Emulator Default Setting Incorrect
**File:** `tests/test_infrastructure_props.py::test_settings_defaults`  
**Issue:** `use_firestore_emulator` defaults to `False`, expected `True` for local dev  
**Impact:** Local development requires manual config override  
**Fix Location:** `backend/config.py` - Change default value for `use_firestore_emulator`

### [ ] 6. Streamlit Page Link Error in Sidebar
**Files:** 
- `tests/test_education_audio_integration.py::test_page_loads_and_displays_documents`
- `tests/test_education_audio_integration.py::test_script_generation_flow`
- `tests/test_education_audio_integration.py::test_audio_generation_flow`
- `tests/test_education_audio_integration.py::test_reset_on_document_change`

**Issue:** `KeyError: 'url_pathname'` in `streamlit_app/components/sidebar.py:54`  
**Impact:** Sidebar navigation broken in test environment  
**Root Cause:** `st.page_link("app.py", ...)` incompatible with Streamlit testing framework  
**Fix Location:** `streamlit_app/components/sidebar.py` - Use conditional logic for test environment

---

## 🟢 LOW - Performance & Test Optimization

### [ ] 7. Hypothesis Test Performance Issue
**File:** `tests/properties/test_agent_creation_props.py::test_knowledge_base_filtering_by_sync_status`  
**Issue:** Input generation too slow - only 2 valid inputs in 1.48 seconds  
**Impact:** Slow test execution, may timeout in CI/CD  
**Fix:** Add `@settings(suppress_health_check=[HealthCheck.too_slow])` or reduce data generation size

---

## ⚠️ Warnings (Non-Blocking)

### [ ] 8. Async Mock Coroutine Not Awaited
**Files:**
- `tests/properties/test_dashboard_stats_props.py::test_error_fallback`
- `tests/test_audio_api_props.py::test_audio_generate_error_handling`

**Issue:** `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited`  
**Impact:** Memory leaks in tests, potential false positives  
**Fix:** Properly await async mocks or use `AsyncMock` correctly

---

## ✅ Summary

**Pass Rate:** 88.6% (148/167)  
**Critical Issues:** 3  
**Medium Issues:** 4  
**Low Issues:** 1  

**Recommended Priority:**
1. Fix audio API error handling (breaks API contract)
2. Add GCP project validation for production
3. Resolve answer style mapping test/code mismatch
4. Fix Streamlit sidebar for test compatibility
5. Update Firestore emulator default setting
6. Optimize Hypothesis test performance
7. Fix async mock warnings
