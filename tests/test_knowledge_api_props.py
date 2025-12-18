"""Property tests for Knowledge API."""

import pytest
from hypothesis import given, strategies as st
from backend.services.data_service import MockDataService
from backend.models.schemas import KnowledgeDocumentCreate, DocumentType, SyncStatus

@pytest.mark.asyncio
async def test_knowledge_id_uniqueness():
    """
    **Feature: upload-knowledge-page, Property 8: Unique Knowledge ID Generation**
    """
    service = MockDataService()
    doc_create = KnowledgeDocumentCreate(
        disease_name="Test",
        document_type=DocumentType.FAQ,
        raw_content="Test content"
    )
    
    # Create multiple documents
    doc1 = await service.create_knowledge_document(doc_create)
    doc2 = await service.create_knowledge_document(doc_create)
    
    assert doc1.knowledge_id != doc2.knowledge_id

@pytest.mark.asyncio
async def test_document_metadata_persistence():
    """
    **Feature: upload-knowledge-page, Property 4: Document Metadata Persistence**
    """
    service = MockDataService()
    doc_create = KnowledgeDocumentCreate(
        disease_name="Specific Name",
        document_type=DocumentType.POST_CARE,
        raw_content="Content"
    )
    
    created = await service.create_knowledge_document(doc_create)
    retrieved = await service.get_knowledge_document(created.knowledge_id)
    
    assert retrieved.disease_name == "Specific Name"
    assert retrieved.document_type == DocumentType.POST_CARE

@pytest.mark.asyncio
async def test_structured_parsing():
    """
    **Feature: upload-knowledge-page, Property: Structured Content Parsing**
    Verifies that markdown is parsed into sections.
    """
    service = MockDataService()
    markdown = """
    Intro text
    
    # Header 1
    Section 1 content
    
    ## Header 2
    Section 2 content
    """
    
    doc_create = KnowledgeDocumentCreate(
        disease_name="Parsing Test",
        document_type=DocumentType.FAQ,
        raw_content=markdown
    )
    
    created = await service.create_knowledge_document(doc_create)
    
    assert created.structured_sections is not None
    # Assuming simple parser logic
    assert "Header 1" in created.structured_sections
    assert "Section 1 content" in created.structured_sections["Header 1"]
