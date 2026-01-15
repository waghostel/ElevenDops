import os
import json
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

def inspect_agent():
    load_dotenv()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    try:
        response = client.conversational_ai.agents.list()
        for agent in response.agents:
            if agent.name == "Dr.eye":
                full_agent = client.conversational_ai.agents.get(agent_id=agent.agent_id)
                
                if hasattr(full_agent, "model_dump"):
                    data = full_agent.model_dump()
                else:
                    data = dict(full_agent)
                
                with open("agent_dump.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, default=str)
                
                print("Dumped agent to agent_dump.json")
                return

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_agent()
