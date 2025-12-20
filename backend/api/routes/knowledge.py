"""API routes for knowledge base management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status

from backend.models.schemas import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
    KnowledgeDocumentListResponse,
    SyncStatus,
    ErrorResponse,
)
from backend.services.data_service import get_data_service, DataServiceInterface
from backend.services.elevenlabs_service import (
    get_elevenlabs_service,
    ElevenLabsService,
    ElevenLabsSyncError,
    ElevenLabsDeleteError,
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


async def sync_knowledge_to_elevenlabs(
    knowledge_id: str,
    content: str,
    name: str,
    data_service: DataServiceInterface,
    elevenlabs_service: ElevenLabsService,
):
    """Background task to sync document to ElevenLabs."""
    try:
        # Update status to syncing
        await data_service.update_knowledge_sync_status(knowledge_id, SyncStatus.SYNCING)

        # Create in ElevenLabs
        try:
            elevenlabs_id = elevenlabs_service.create_document(text=content, name=name)
        except ElevenLabsSyncError as e:
            # Re-raise explicit sync error to be caught below with type info if needed
            # But simpler to just let it bubble to the specific except block below
            raise e
        except Exception as e:
            # Wrap generic errors
            raise e

        # Update status to completed
        await data_service.update_knowledge_sync_status(
            knowledge_id, SyncStatus.COMPLETED, elevenlabs_id
        )

    except ElevenLabsSyncError as e:
        # Update status to failed with specific message
        await data_service.update_knowledge_sync_status(
            knowledge_id, 
            SyncStatus.FAILED, 
            error_message=str(e)
        )
    except Exception as e:
        # Update status to failed on generic error
        await data_service.update_knowledge_sync_status(
            knowledge_id, 
            SyncStatus.FAILED, 
            error_message=f"Unexpected error: {str(e)}"
        )


@router.post(
    "",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={500: {"model": ErrorResponse}},
)
async def create_knowledge_document(
    doc: KnowledgeDocumentCreate,
    background_tasks: BackgroundTasks,
    data_service: Annotated[DataServiceInterface, Depends(get_data_service)],
    elevenlabs_service: Annotated[ElevenLabsService, Depends(get_elevenlabs_service)],
):
    """Create a new knowledge document and sync to ElevenLabs.
    
    The document name in ElevenLabs will be formatted as "{disease_name}_{document_type}".
    The content will be parsed into structured sections for future retrieval.
    """
    try:
        # 1. Create in database (pending status)
        # DataService automatically parses structured_sections now.
        created_doc = await data_service.create_knowledge_document(doc)
        
        # Format name for ElevenLabs as per user requirement: "Disease Name_Type"
        # Using string representation of document_type enum value
        elevenlabs_doc_name = f"{doc.disease_name}_{doc.document_type.value}"

        # 2. Trigger background sync
        background_tasks.add_task(
            sync_knowledge_to_elevenlabs,
            created_doc.knowledge_id,
            doc.raw_content,
            elevenlabs_doc_name,
            data_service,
            elevenlabs_service,
        )

        return created_doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge document: {str(e)}",
        )


@router.get("", response_model=KnowledgeDocumentListResponse)
async def list_knowledge_documents(
    data_service: Annotated[DataServiceInterface, Depends(get_data_service)],
):
    """List all knowledge documents."""
    documents = await data_service.get_knowledge_documents()
    return KnowledgeDocumentListResponse(documents=documents, total_count=len(documents))


@router.get(
    "/{knowledge_id}",
    response_model=KnowledgeDocumentResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_knowledge_document(
    knowledge_id: str,
    data_service: Annotated[DataServiceInterface, Depends(get_data_service)],
):
    """Get a specific knowledge document."""
    doc = await data_service.get_knowledge_document(knowledge_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge document {knowledge_id} not found",
        )
    return doc


@router.delete(
    "/{knowledge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def delete_knowledge_document(
    knowledge_id: str,
    data_service: Annotated[DataServiceInterface, Depends(get_data_service)],
    elevenlabs_service: Annotated[ElevenLabsService, Depends(get_elevenlabs_service)],
):
    """Delete a knowledge document from database and ElevenLabs."""
    doc = await data_service.get_knowledge_document(knowledge_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge document {knowledge_id} not found",
        )

    # If synced to ElevenLabs, try to delete there first
    if doc.elevenlabs_document_id:
        try:
            elevenlabs_service.delete_document(doc.elevenlabs_document_id)
        except ElevenLabsDeleteError as e:
            # Log error but verify if we should continue deleting from DB.
            # Spec says "Firestore Deletion Priority: ...Firestore document SHALL still be deleted"
            # So we proceed but maybe log/warn. 
            pass
        except Exception:
            # Swallow other errors to ensure local deletion
            pass

    # Delete from database
    success = await data_service.delete_knowledge_document(knowledge_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document from database",
        )


@router.post(
    "/{knowledge_id}/retry-sync",
    response_model=KnowledgeDocumentResponse,
    responses={404: {"model": ErrorResponse}},
)
async def retry_knowledge_sync(
    knowledge_id: str,
    background_tasks: BackgroundTasks,
    data_service: Annotated[DataServiceInterface, Depends(get_data_service)],
    elevenlabs_service: Annotated[ElevenLabsService, Depends(get_elevenlabs_service)],
):
    """Retry syncing a failed knowledge document."""
    doc = await data_service.get_knowledge_document(knowledge_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge document {knowledge_id} not found",
        )

    if doc.sync_status == SyncStatus.COMPLETED:
        return doc

    elevenlabs_doc_name = f"{doc.disease_name}_{doc.document_type.value}"

    # Set status to PENDING immediately to clear error and show feedback
    await data_service.update_knowledge_sync_status(
        knowledge_id, 
        SyncStatus.PENDING,
        error_message=None # Explicitly clear error
    )
    
    # Trigger background sync
    background_tasks.add_task(
        sync_knowledge_to_elevenlabs,
        doc.knowledge_id,
        doc.raw_content,
        elevenlabs_doc_name,
        data_service,
        elevenlabs_service,
    )
    
    # Return updated doc state
    doc.sync_status = SyncStatus.PENDING
    doc.sync_error_message = None
    return doc
