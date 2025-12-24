"""Property tests for Knowledge API."""

import pytest
from hypothesis import given, strategies as st
from backend.services.data_service import MockDataService
from backend.models.schemas import KnowledgeDocumentCreate, SyncStatus, DEFAULT_DOCUMENT_TAGS

@pytest.mark.asyncio
async def test_knowledge_id_uniqueness():
    """
    **Feature: upload-knowledge-page, Property 8: Unique Knowledge ID Generation**
    """
    service = MockDataService()
    doc_create = KnowledgeDocumentCreate(
        disease_name="Test",
        tags=["faq"],
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
        tags=["post_care", "faq"],
        raw_content="Content"
    )
    
    created = await service.create_knowledge_document(doc_create)
    retrieved = await service.get_knowledge_document(created.knowledge_id)
    
    assert retrieved.disease_name == "Specific Name"
    assert retrieved.tags == ["post_care", "faq"]

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
        tags=["faq"],
        raw_content=markdown
    )
    
    created = await service.create_knowledge_document(doc_create)
    
    assert created.structured_sections is not None
    # Assuming simple parser logic
    assert "Header 1" in created.structured_sections
    assert "Section 1 content" in created.structured_sections["Header 1"]

@pytest.mark.asyncio
async def test_multiple_tags_persistence():
    """
    **Feature: upload-knowledge-page, Property: Multiple Tags Support**
    Verifies that documents can have multiple tags.
    """
    service = MockDataService()
    doc_create = KnowledgeDocumentCreate(
        disease_name="Multi-Tag Test",
        tags=["before_visit", "diagnosis", "procedure"],
        raw_content="Content with multiple tags"
    )
    
    created = await service.create_knowledge_document(doc_create)
    retrieved = await service.get_knowledge_document(created.knowledge_id)
    
    assert len(retrieved.tags) == 3
    assert "before_visit" in retrieved.tags
    assert "diagnosis" in retrieved.tags
    assert "procedure" in retrieved.tags
