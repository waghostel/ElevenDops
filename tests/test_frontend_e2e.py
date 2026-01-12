
import os
import pytest
from streamlit.testing.v1 import AppTest
import httpx
import time

# Skip unless we are running in "Real GCP" mode which means "Real Backend" for this context
# The user wants to verify IAM Service Account against the running backend.
# We reuse TEST_REAL_GCP flag as it disables the mocks in conftest.py
@pytest.mark.skipif(os.environ.get("TEST_REAL_GCP") != "true", reason="Skipping E2E test unless TEST_REAL_GCP=true")
def test_frontend_e2e_connectivity():
    """
    E2E Test to verify frontend can talk to the backend using the IAM Service Account.
    This test assumes the backend is already running at localhost:8000.
    """
    
    # 0. Fast-fail check if backend is reachable
    try:
        resp = httpx.get("http://localhost:8000/api/health", timeout=5.0)
        resp.raise_for_status()
        health_data = resp.json()
        print(f"Backend is healthy: {health_data}")
    except Exception as e:
        pytest.fail(f"Backend is not reachable at http://localhost:8000. Is it running? Error: {e}")

    # 1. Initialize AppTest
    at = AppTest.from_file("streamlit_app/pages/3_Education_Audio.py", default_timeout=60)
    
    # Ensure we use the real backend URL
    # AppTest shares process env, but let's be explicit if needed, though env var propagation is standard.
    
    # Run the app
    at.run()
    
    # 2. Verify Page Loaded
    assert not at.exception, f"App failed to load with exception: {at.exception}"
    assert "Patient Education Audio" in at.title[0].value
    
    # 3. Verify Documents Loaded (Connectivity Check)
    # The document selector is usually the first selectbox or has a specific label.
    # We look for "Choose a condition/procedure:"
    doc_sb = next((sb for sb in at.selectbox if "Choose a condition" in sb.label), None)
    
    assert doc_sb is not None, "Document selector not found. Frontend layout might have changed."
    
    # If we have options, it means backend communication for documents worked!
    if not doc_sb.options:
        # Check if we have the "No knowledge documents found" info message
        # This is also a valid "success" for connectivity, just means empty DB.
        info_msgs = [info.value for info in at.info]
        no_docs_msg = any("No knowledge documents found" in msg for msg in info_msgs)
        
        if no_docs_msg:
            print("Successfully connected to backend, but no documents found.")
            return # Test passes, connectivity is verified.
        else:
            pytest.fail("Document selector is empty and no 'No documents found' message. potential sync error?")
    
    print(f"Found {len(doc_sb.options)} documents: {doc_sb.options}")
    
    # 4. smoke Test Generation (Optional)
    # Only if we have a document
    if doc_sb.options:
        # Select the first document
        doc_sb.select_index(0).run()
        
        # Check if Script Editor Appears
        # "Generate Script" button should be visible
        gen_btn = next((b for b in at.button if b.key == "generate_script_btn"), None)
        assert gen_btn is not None, "Generate Script button not found"
        
        # We generally avoid running full generation in automated E2E to save cost/time
        # unless specifically asked. The prompt asked to "verify if all the feature works".
        # We will try to Generate Script as it verifies Gemini integration (IAM permissions).
        
        print("Attempting to generate script...")
        gen_btn.click().run()
        
        # Verify script generation
        # This might take time. AppTest waits for script execution, but streaming might be tricky.
        # The script uses `st.empty()` and modifies session state.
        # We check `st.session_state.generated_script`.
        
        if at.exception:
             pytest.fail(f"Exception during script generation: {at.exception}")
             
        # Check result
        gen_script = at.session_state["generated_script"] if "generated_script" in at.session_state else None
        
        if not gen_script:
             # Try to find if editor area has value
             gen_id = at.session_state["generation_id"] if "generation_id" in at.session_state else 0
             editor_key = f"script_editor_area_{gen_id}"
             editor_val = at.session_state[editor_key] if editor_key in at.session_state else None
             
             if not editor_val:
                 # Also check for values in text_area elements directly
                 text_areas = [ta.value for ta in at.text_area if ta.key == editor_key]
                 if not text_areas or not text_areas[0]:
                    # Collect debug info
                    toasts = [t.message for t in at.toast]
                    warnings = [w.value for w in at.warning]
                    infos = [i.value for i in at.info]
                    errors = [e.value for e in at.error]
                    
                    print(f"DEBUG: Toasts: {repr(toasts)}")
                    print(f"DEBUG: Warnings: {repr(warnings)}")
                    print(f"DEBUG: Infos: {repr(infos)}")
                    print(f"DEBUG: Errors: {repr(errors)}")
                    
                    # Check for error console log if accessible
                    # It might be in session state or visible elements
                    
                    pytest.fail(f"Script generation didn't produce output. generated_script empty. Toasts: {toasts}, Warnings: {warnings}")
             
        print("Script generation successful!")
