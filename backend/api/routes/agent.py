"""API routes for Agent management."""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request

from backend.models.schemas import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
)
from backend.services.agent_service import AgentService, get_agent_service, ElevenLabsAgentError
from backend.middleware.rate_limit import limiter, RATE_LIMITS

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("", response_model=AgentResponse)
@limiter.limit(RATE_LIMITS["agent"])
async def create_agent(
    agent_data: AgentCreateRequest,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    """Create a new agent."""
    try:
        agent = await service.create_agent(agent_data)
        return agent
    except ElevenLabsAgentError as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("", response_model=AgentListResponse)
async def list_agents(
    service: AgentService = Depends(get_agent_service),
):
    """List all agents."""
    return await service.get_agents()


@router.put("/{agent_id}", response_model=AgentResponse)
@limiter.limit(RATE_LIMITS["agent"])
async def update_agent(
    agent_id: str,
    update_data: AgentUpdateRequest,
    request: Request,
    service: AgentService = Depends(get_agent_service),
):
    """Update an existing agent."""
    try:
        updated_agent = await service.update_agent(agent_id, update_data)
        return updated_agent
    except KeyError:
        raise HTTPException(status_code=404, detail="Agent not found")
    except ElevenLabsAgentError as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    service: AgentService = Depends(get_agent_service),
):
    """Delete an agent."""
    try:
        success = await service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "success", "message": "Agent deleted"}
    except ElevenLabsAgentError as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/system-prompts")
async def get_system_prompts(
    service: AgentService = Depends(get_agent_service),
):
    """Get all system prompts by answer style.
    
    Returns:
        dict: Mapping of style value to system prompt text.
    """
    return service.get_system_prompts()
