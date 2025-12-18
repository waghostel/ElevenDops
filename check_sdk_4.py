
import elevenlabs
from elevenlabs.client import ElevenLabs

try:
    client = ElevenLabs(api_key="dummy")
    cai = client.conversational_ai
    
    if hasattr(cai, "knowledge_base"):
        print(f"cai.knowledge_base type: {type(cai.knowledge_base)}")
        print(f"cai.knowledge_base dir: {[d for d in dir(cai.knowledge_base) if not d.startswith('_')]}")
    else:
        print("cai has no knowledge_base attribute")
        
    if hasattr(cai, "add_to_knowledge_base"):
         print("cai has add_to_knowledge_base method")

except Exception as e:
    print(f"Error: {e}")
