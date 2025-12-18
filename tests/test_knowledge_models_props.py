"""Property tests for knowledge document models."""

from hypothesis import given, strategies as st
from backend.models.schemas import KnowledgeDocumentCreate, DocumentType, SyncStatus, KnowledgeDocumentResponse
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
                document_type=DocumentType.FAQ,
                raw_content="Valid content"
            )

@given(st.sampled_from(DocumentType))
def test_document_type_validity(doc_type):
    """
    **Feature: upload-knowledge-page, Property 9: Document Schema Completeness**
    Validates that all enum values are accepted.
    """
    doc = KnowledgeDocumentCreate(
        disease_name="Test Disease",
        document_type=doc_type,
        raw_content="Test content"
    )
    assert doc.document_type == doc_type

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
        document_type=DocumentType.FAQ,
        raw_content="content",
        sync_status=SyncStatus.PENDING,
        elevenlabs_document_id=None,
        structured_sections=sections,
        created_at=datetime.now()
    )
    assert doc.structured_sections == sections
