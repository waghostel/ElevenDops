
from hypothesis import given, strategies as st
from pydantic import ValidationError
import pytest
from backend.models.schemas import PatientSessionCreate

# **Feature: patient-test-page, Property 1: Patient ID Validation and Storage**
# **Validates: Requirements 1.2, 1.4**
@given(patient_id=st.from_regex(r'^[a-zA-Z0-9]+$', fullmatch=True))
def test_property_1_valid_patient_id(patient_id):
    """
    Property 1: Patient ID Validation and Storage (Valid Case)
    For any ASCII alphanumeric string input as Patient_ID, it should be accepted.
    """
    model = PatientSessionCreate(patient_id=patient_id, agent_id="test_agent")
    assert model.patient_id == patient_id

@given(patient_id=st.text())
def test_property_1_invalid_patient_id(patient_id):
    """
    Property 1: Patient ID Validation and Storage (Invalid Case)
    For any string input as Patient_ID, if the string contains non-alphanumeric characters
    or is empty, it should be rejected.
    """
    # Define what is valid to skip those cases (strictly ASCII alphanumeric)
    is_valid = len(patient_id) > 0 and patient_id.isalnum() and all(ord(c) < 128 for c in patient_id)
    
    if is_valid:
        return

    with pytest.raises(ValidationError):
        PatientSessionCreate(patient_id=patient_id, agent_id="test_agent")


