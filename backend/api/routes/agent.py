"""API routes for Agent management."""

from typing import List

from fastapi import APIRouter, HTTPException, Depends

from backend.models.schemas import (
    AgentCreateRequest,
    AgentResponse,
    AgentListResponse,
)
from backend.services.agent_service import AgentService, get_agent_service, ElevenLabsAgentError

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("", response_model=AgentResponse)
async def create_agent(
    request: AgentCreateRequest,
    service: AgentService = Depends(get_agent_service),
):
    """Create a new agent."""
    try:
        agent = await service.create_agent(request)
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
