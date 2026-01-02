# TODO: Replace Hardcoded Doctor ID with Authentication

**Created:** 2026-01-02  
**Priority:** Medium  
**Status:** Pending

## Context

The `doctor_id` is currently hardcoded to `"dr_demo_001"` for testing purposes. This allows all features to work consistently across local development and production during the testing phase.

## Action Required

When implementing real user authentication, update the session state initialization:

**File:** `streamlit_app/pages/3_Education_Audio.py` (around line 76)

```python
# Current (testing):
if "doctor_id" not in st.session_state:
    st.session_state.doctor_id = "dr_demo_001"

# Replace with:
if "doctor_id" not in st.session_state:
    st.session_state.doctor_id = get_authenticated_user_id()  # Your auth logic
```

## Affected Features

- Audio file generation (tagged with `doctor_id`)
- Audio history filtering ("All My Audio" view)
- Future: Document ownership, agent ownership

## Related Files

- `streamlit_app/pages/3_Education_Audio.py`
- `backend/api/routes/audio.py`
- `backend/services/audio_service.py`
