
import elevenlabs
from elevenlabs.client import ElevenLabs

try:
    client = ElevenLabs(api_key="dummy")
    print("Client attributes:", [d for d in dir(client) if not d.startswith("_")])
    
    if hasattr(client, "conversational_ai"):
        print("ConvAI attributes:", [d for d in dir(client.conversational_ai) if not d.startswith("_")])
    
    if hasattr(client, "knowledge_base"):
         print("Client.knowledge_base attributes:", [d for d in dir(client.knowledge_base) if not d.startswith("_")])

except Exception as e:
    print(f"Error: {e}")
