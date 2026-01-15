import os
import json
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Disable all logging
logging.getLogger().setLevel(logging.CRITICAL)

def inspect_agent():
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ELEVENLABS_API_KEY not found in .env")
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
            print("Agent 'Dr.eye' not found.")
            return

        print(f"Found agent: {target_agent.name} ({target_agent.agent_id})")

        # Get full details
        full_agent = client.conversational_ai.agents.get(agent_id=target_agent.agent_id)
        
        print("\n" + "="*50)
        
        if hasattr(full_agent, "conversation_config"):
            config = full_agent.conversation_config
            agent_config = getattr(config, "agent", None)
            
            if agent_config:
                # Use dir() to see all available attributes if standard access fails
                print(f"Agent Config Available Attributes: {[a for a in dir(agent_config) if not a.startswith('_')]}")
                print("-" * 20)
                print(f"agent.language: {getattr(agent_config, 'language', 'MISSING')}")
                print(f"agent.language_presets: {getattr(agent_config, 'language_presets', 'MISSING')}")
            else:
                print("config.agent is None")
        else:
            print("No conversation_config found")
            
        print("="*50 + "\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_agent()
