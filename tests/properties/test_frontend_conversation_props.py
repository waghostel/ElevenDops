
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta
from typing import List

from streamlit_app.services.models import (
    ConversationSummary,
    ConversationDetail,
    ConversationMessage,
    ConversationResponse
)
from streamlit_app.services.backend_api import BackendAPIClient

# Strategies
# Use naive datetimes to avoid comparison issues
datetime_st = st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 1, 1), timezones=st.none())

message_st = st.builds(
    ConversationMessage,
    role=st.sampled_from(["patient", "agent"]),
    content=st.text(min_size=1, max_size=200),
    timestamp=datetime_st,
    audio_data=st.none()
)

summary_st = st.builds(
    ConversationSummary,
    conversation_id=st.uuids().map(str),
    patient_id=st.text(min_size=1, max_size=50),
    agent_id=st.text(min_size=1, max_size=50),
    agent_name=st.text(min_size=1, max_size=50),
    requires_attention=st.booleans(),
    main_concerns=st.lists(st.text(max_size=50), max_size=10),
    total_messages=st.integers(min_value=0, max_value=1000),
    answered_count=st.integers(min_value=0, max_value=1000),
    unanswered_count=st.integers(min_value=0, max_value=1000),
    duration_seconds=st.integers(min_value=0, max_value=3600),
    created_at=datetime_st
)

@settings(suppress_health_check=[HealthCheck.too_slow])
@given(summary=summary_st)
def test_conversation_summary_model(summary):
    """
    **Feature: conversation-logs-page, Property 8: Frontend Model Consistency**
    **Validates: Frontend Data Models**
    """
    assert isinstance(summary.conversation_id, str)
    assert isinstance(summary.requires_attention, bool)
    assert isinstance(summary.main_concerns, list)
    assert isinstance(summary.created_at, datetime)

@settings(suppress_health_check=[HealthCheck.too_slow])
@given(
    summary=summary_st,
    messages=st.lists(message_st, max_size=50),
    answered=st.lists(st.text(max_size=50), max_size=20),
    unanswered=st.lists(st.text(max_size=50), max_size=20)
)
def test_conversation_detail_inheritance(summary, messages, answered, unanswered):
    """
    **Feature: conversation-logs-page, Property 8: Frontend Model Consistency**
    **Validates: ConversationDetail inheritance**
    """
    detail = ConversationDetail(
        conversation_id=summary.conversation_id,
        patient_id=summary.patient_id,
        agent_id=summary.agent_id,
        agent_name=summary.agent_name,
        requires_attention=summary.requires_attention,
        main_concerns=summary.main_concerns,
        total_messages=summary.total_messages,
        answered_count=summary.answered_count,
        unanswered_count=summary.unanswered_count,
        duration_seconds=summary.duration_seconds,
        created_at=summary.created_at,
        messages=messages,
        answered_questions=answered,
        unanswered_questions=unanswered
    )
    
    assert isinstance(detail, ConversationSummary)
    assert detail.messages == messages
    assert detail.answered_questions == answered

# Note: Testing API Client would ideally involve mocking the backend response.
# Since we are using property tests for unit logic, we focus on model integrity here.
# Integration tests cover the actual API calls.
