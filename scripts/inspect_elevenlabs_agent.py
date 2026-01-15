import os
import json
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_agent():
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.error("ELEVENLABS_API_KEY not found in .env")
        return

    client = ElevenLabs(api_key=api_key)

    try:
        # List agents to find Dr.eye
        response = client.conversational_ai.agents.list()
        agents = response.agents
        
        target_agent = None
        for agent in agents:
            if agent.name == "Dr.eye":
                target_agent = agent
                break
        
        if not target_agent:
            logger.error("Agent 'Dr.eye' not found.")
            return

        logger.info(f"Found agent: {target_agent.name} ({target_agent.agent_id})")

        # Get full details
        full_agent = client.conversational_ai.agents.get(agent_id=target_agent.agent_id)
        
        print("-" * 50)
        print("LANGUAGE CONFIG CHECK:")
        print("-" * 50)
        
        if hasattr(full_agent, "conversation_config"):
            config = full_agent.conversation_config
            agent_config = getattr(config, "agent", None)
            
            if agent_config:
                print(f"agent.language: {getattr(agent_config, 'language', 'N/A')}")
                print(f"agent.language_presets: {getattr(agent_config, 'language_presets', 'N/A')}")
            else:
                print("config.agent is None")
                
            # Check if it's top level on config (unlikely but checking)
            print(f"config.language_presets: {getattr(config, 'language_presets', 'N/A')}")
            
        else:
            print("No conversation_config found")
        print("-" * 50)

    except Exception as e:
        logger.error(f"Error inspecting agent: {e}")

if __name__ == "__main__":
    inspect_agent()
