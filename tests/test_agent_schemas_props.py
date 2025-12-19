"""Property-based tests for Agent schemas."""

from hypothesis import given, strategies as st
import pytest
from pydantic import ValidationError

from backend.models.schemas import AgentCreateRequest, AnswerStyle, AgentResponse


@given(name=st.text(min_size=1, max_size=100))
def test_agent_create_request_valid_name(name):
    """Property: AgentCreateRequest accepts valid names."""
    # Ensure name is not just whitespace
    if not name.strip():
        return

    request = AgentCreateRequest(
        name=name,
        voice_id="voice123",
        answer_style=AnswerStyle.PROFESSIONAL,
        doctor_id="doc123"
    )
    assert request.name == name


@given(name=st.one_of(
    st.just(""),
    st.text(alphabet=" \t\n\r", min_size=1, max_size=10)
))
def test_agent_create_request_whitespace_name_rejected(name):
    """
    **Feature: agent-setup-page, Property 1: Whitespace-only names are rejected**
    
    Validates: Requirements 1.3
    """
    with pytest.raises(ValidationError):
        AgentCreateRequest(
            name=name,
            voice_id="voice123",
            answer_style=AnswerStyle.PROFESSIONAL,
            doctor_id="doc123"
        )


@given(answer_style=st.sampled_from(AnswerStyle))
def test_answer_style_enum(answer_style):
    """Property: AnswerStyle enum values are valid."""
    assert answer_style in [AnswerStyle.PROFESSIONAL, AnswerStyle.FRIENDLY, AnswerStyle.EDUCATIONAL]
