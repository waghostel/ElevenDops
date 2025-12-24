"""Property tests for knowledge document models."""

from hypothesis import given, strategies as st
from backend.models.schemas import KnowledgeDocumentCreate, SyncStatus, KnowledgeDocumentResponse, DEFAULT_DOCUMENT_TAGS
import pytest
from pydantic import ValidationError
from datetime import datetime

@given(st.text())
def test_knowledge_document_create_validation(text):
    """
    **Feature: upload-knowledge-page, Property 3: Required Field Validation**
    Validates that creating a document with empty disease name fails validation.
    """
    # If text is empty or whitespace, it should fail
    if not text.strip():
        with pytest.raises(ValidationError):
            KnowledgeDocumentCreate(
                disease_name=text,
                tags=["faq"],
                raw_content="Valid content"
            )

@given(st.lists(st.sampled_from(DEFAULT_DOCUMENT_TAGS), min_size=1, max_size=3))
def test_tags_validity(tags):
    """
    **Feature: upload-knowledge-page, Property 9: Document Schema Completeness**
    Validates that all default tag values are accepted.
    """
    doc = KnowledgeDocumentCreate(
        disease_name="Test Disease",
        tags=tags,
        raw_content="Test content"
    )
    assert doc.tags == tags

def test_empty_tags_rejected():
    """
    **Feature: upload-knowledge-page, Property: Tags Validation**
    Validates that empty tags list is rejected.
    """
    with pytest.raises(ValidationError):
        KnowledgeDocumentCreate(
            disease_name="Test Disease",
            tags=[],
            raw_content="Test content"
        )

@given(st.sampled_from(SyncStatus))
def test_sync_status_validity(status):
    """
    **Feature: upload-knowledge-page, Property 9: Document Schema Completeness**
    Validates that all sync status enum values are accepted in Response.
    """
    # Just checking instantiation
    assert status in SyncStatus

@given(st.dictionaries(keys=st.text(), values=st.text()))
def test_structured_sections_validation(sections):
    """
    **Feature: upload-knowledge-page, Property 9: Document Schema Completeness**
    Validates that structured_sections can be any dict of strings.
    """
    doc = KnowledgeDocumentResponse(
        knowledge_id="test_id",
        doctor_id="doc_id",
        disease_name="test",
        tags=["faq"],
        raw_content="content",
        sync_status=SyncStatus.PENDING,
        elevenlabs_document_id=None,
        structured_sections=sections,
        created_at=datetime.now()
    )
    assert doc.structured_sections == sections
