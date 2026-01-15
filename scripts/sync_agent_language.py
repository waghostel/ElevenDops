import sys
import os
import asyncio
import logging
from typing import Optional

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from backend.services.elevenlabs_service import get_elevenlabs_service, ElevenLabsService
from backend.services.data_service import get_data_service
from backend.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_dr_eye_language():
    """Fetch Dr.eye agent from ElevenLabs and update local Firestore."""
    settings = get_settings()
    
    # 1. Initialize Services
    logger.info("Initializing services...")
    elevenlabs_service: ElevenLabsService = get_elevenlabs_service()
    data_service = get_data_service()
    
    # Check API key
    if not settings.elevenlabs_api_key and not settings.use_mock_elevenlabs:
        logger.error("No ELEVENLABS_API_KEY found and Mock mode is OFF. Please set the API key.")
        return

    # 2. List Agents from ElevenLabs
    logger.info("Fetching agents from ElevenLabs...")
    try:
        # The service doesn't have a direct 'list_agents' that returns raw ElevenLabs objects
        # It usually returns local objects. We need to use the underlying client.
        if elevenlabs_service.use_mock:
            logger.info("Using MOCK ElevenLabs service. Creating mock Dr.eye data.")
            elevenlabs_agents = [{
                "agent_id": "mock_dr_eye_id",
                "name": "Dr.eye",
                "conversation_config": {
                    "agent": {
                        "language": "en",
                        "language_presets": {
                            "zh": {},
                            "es": {},
                            "fr": {},
                            "de": {},
                            "ja": {},
                            "ko": {}
                        }
                    }
                }
            }]
        else:
            # Try list() instead of get_all()
            try:
                # Some SDK versions use list()
                response = elevenlabs_service.client.conversational_ai.agents.list()
                elevenlabs_agents = response.agents
            except AttributeError:
                 # Fallback for debugging
                 logger.error(f"Available methods on agents client: {dir(elevenlabs_service.client.conversational_ai.agents)}")
                 raise
            
    except Exception as e:
        logger.error(f"Failed to fetch from ElevenLabs: {e}")
        return

    # 3. Find Dr.eye
    target_name = "Dr.eye"
    found_agent_summary = None
    
    for agent in elevenlabs_agents:
        # Handle both object and dict access depending on SDK version/Mock
        a_name = agent.name if hasattr(agent, "name") else agent.get("name")
        if a_name and target_name.lower() in a_name.lower():
            found_agent_summary = agent
            break
            
    if not found_agent_summary:
        logger.error(f"Agent '{target_name}' not found in ElevenLabs.")
        if elevenlabs_agents:
            # Helper to get name safely
            def get_name(a): return a.name if hasattr(a, "name") else a.get("name")
            logger.info("Available agents: " + ", ".join([get_name(a) for a in elevenlabs_agents]))
        return

    # Extract ID from summary
    if hasattr(found_agent_summary, "agent_id"):
        el_agent_id = found_agent_summary.agent_id
    else:
        el_agent_id = found_agent_summary["agent_id"]

    logger.info(f"Found agent summary for '{target_name}' (ID: {el_agent_id}). Fetching full details...")

    # Fetch full agent details to get conversation_config
    if elevenlabs_service.use_mock:
         # In mock mode, we already constructed the full object in the list
         elevenlabs_agent = found_agent_summary
    else:
        try:
             elevenlabs_agent = elevenlabs_service.client.conversational_ai.agents.get(agent_id=el_agent_id)
        except Exception as e:
             logger.error(f"Failed to fetch full agent details for {el_agent_id}: {e}")
             return

    # Extract Language info from FULL agent object
    # SDK object access
    if hasattr(elevenlabs_agent, "conversation_config"):
        config = elevenlabs_agent.conversation_config
        # config might be an object or dict
        agent_config = config.agent if hasattr(config, "agent") else config.get("agent", {})
        # agent_config might be object or dict
        if hasattr(agent_config, "language"):
            primary_lang = agent_config.language
            presets = getattr(agent_config, "language_presets", {})
        else:
            primary_lang = agent_config.get("language")
            presets = agent_config.get("language_presets", {})
    else:
        # Dict access (mock or legacy)
        config = elevenlabs_agent.get("conversation_config", {})
        agent_config = config.get("agent", {})
        primary_lang = agent_config.get("language")
        presets = agent_config.get("language_presets", {})

    # Construct language list
    # Primary first, then presets keys
    if not primary_lang:
        primary_lang = "en"
        
    detected_languages = [primary_lang]
    if presets:
        # presets is a dict of lang_code -> config
        detected_languages.extend([k for k in presets.keys() if k != primary_lang])
    
    logger.info(f"Found '{target_name}' in ElevenLabs.")
    logger.info(f"  ID: {el_agent_id}")
    logger.info(f"  Primary Language: {primary_lang}")
    logger.info(f"  All Languages: {detected_languages}")

    # 4. Find Local Agent
    logger.info("Fetching local agents from Firestore...")
    local_agents = await data_service.get_agents()
    target_local_agent = None
    
    for agent in local_agents:
        if agent.elevenlabs_agent_id == el_agent_id:
            target_local_agent = agent
            logger.info("Found match by ElevenLabs ID.")
            break
        elif agent.name.lower() == target_name.lower():
            target_local_agent = agent
            logger.info("Found match by Name.")
            break
            
    if not target_local_agent:
        logger.error(f"Agent '{target_name}' not found in local Firestore.")
        return

    logger.info(f"Local Agent Current Languages: {target_local_agent.languages}")

    # 5. Update Local Agent
    if target_local_agent.languages != detected_languages:
        logger.info("Mismatch detected. Updating local record...")
        
        # Update the object
        updated_agent = target_local_agent.model_copy(update={"languages": detected_languages})
        
        # Save
        await data_service.save_agent(updated_agent)
        logger.info("Successfully updated Firestore record.")
    else:
        logger.info("Languages already match. No update needed.")

    # 6. Output useful Info for the user
    print("\n" + "="*50)
    print("SYNC COMPLETE")
    print(f"Agent: {target_name}")
    print(f"ElevenLabs ID: {el_agent_id}")
    print(f"Synced Languages: {detected_languages}")
    print("="*50 + "\n")

    print("To verify via CURL, use this command:")
    print(f'curl -X GET "https://api.elevenlabs.io/v1/convai/agents/{el_agent_id}" -H "xi-api-key: {settings.elevenlabs_api_key or "YOUR_API_KEY"}"')


if __name__ == "__main__":
    if hasattr(asyncio, "run"):
        asyncio.run(sync_dr_eye_language())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sync_dr_eye_language())
