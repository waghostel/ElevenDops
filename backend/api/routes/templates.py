"""Templates API routes for prompt template management."""

from typing import List

from fastapi import APIRouter, HTTPException, Depends

from backend.models.schemas import (
    TemplateInfoResponse,
    CustomTemplateCreate,
    CustomTemplateUpdate,
    CustomTemplateResponse
)
from backend.services.prompt_template_service import (
    PromptTemplateService,
    get_prompt_template_service,
)
from backend.services.data_service import get_data_service

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=List[TemplateInfoResponse])
async def list_templates() -> List[TemplateInfoResponse]:
    """List all available content type templates (including custom ones).
    
    Returns:
        List of template metadata including ID, name, description, and preview.
    """
    service = get_prompt_template_service()
    templates = await service.list_templates()
    
    return [
        TemplateInfoResponse(
            template_id=t.template_id,
            display_name=t.display_name,
            description=t.description,
            category=t.category,
            preview=t.preview,
        )
        for t in templates
    ]


@router.post("", response_model=CustomTemplateResponse)
async def create_custom_template(
    template: CustomTemplateCreate,
) -> CustomTemplateResponse:
    """Create a new custom template.
    
    Args:
        template: Custom template data.
        
    Returns:
        Created custom template.
    """
    # Use get_data_service() to respect environment variables (mock vs real DB)
    db_service = get_data_service()
    try:
        return await db_service.create_custom_template(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/{template_id}", response_model=CustomTemplateResponse)
async def update_custom_template(
    template_id: str,
    template: CustomTemplateUpdate,
) -> CustomTemplateResponse:
    """Update a custom template.
    
    Args:
        template_id: Template ID to update.
        template: Updated template data.
        
    Returns:
        Updated custom template.
    """
    db_service = get_data_service()
    result = await db_service.update_custom_template(template_id, template)
    if not result:
        raise HTTPException(status_code=404, detail="Template not found")
    return result


@router.delete("/{template_id}")
async def delete_custom_template(template_id: str):
    """Delete a custom template.
    
    Args:
        template_id: Template ID to delete.
    """
    db_service = get_data_service()
    success = await db_service.delete_custom_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or could not be deleted")
    return {"status": "success", "message": "Template deleted"}


@router.get("/{template_id}")
async def get_template(template_id: str) -> dict:
    """Get full template content for preview.
    
    Args:
        template_id: The template identifier.
        
    Returns:
        Dictionary containing the full template content.
    """
    service = get_prompt_template_service()
    
    try:
        content = await service.get_template(template_id)
        return {"template_id": template_id, "content": content}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/preview")
async def preview_combined_prompt(
    template_ids: List[str],
    quick_instructions: str = None,
) -> dict:
    """Preview the combined prompt without generating a script.
    
    This endpoint allows users to see how templates will be combined
    before actually generating a script.
    
    Args:
        template_ids: List of template IDs in display order.
        quick_instructions: Optional additional instructions.
        
    Returns:
        Dictionary containing the combined prompt.
    """
    service = get_prompt_template_service()
    
    combined_prompt = await service.build_prompt(
        template_ids=template_ids,
        quick_instructions=quick_instructions,
    )
    
    return {
        "template_ids": template_ids,
        "quick_instructions": quick_instructions,
        "combined_prompt": combined_prompt,
        "character_count": len(combined_prompt),
    }
