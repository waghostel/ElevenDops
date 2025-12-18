
import elevenlabs
from elevenlabs.client import ElevenLabs
import inspect

print(f"ElevenLabs version: {elevenlabs.__version__}")

try:
    client = ElevenLabs(api_key="dummy")
    
    if hasattr(client, "conversational_ai"):
        cai = client.conversational_ai
        if hasattr(cai, "knowledge_base"):
            kb = cai.knowledge_base
            print("KB attributes:", [d for d in dir(kb) if not d.startswith("_")])
            
            # Check deeper if there is a 'document' or 'documents' attribute
            if hasattr(kb, "document"):
                 print("KB.document attributes:", [d for d in dir(kb.document) if not d.startswith("_")])
            
            if hasattr(kb, "documents"):
                 print("KB.documents attributes:", [d for d in dir(kb.documents) if not d.startswith("_")])
                 
        else:
            print("no knowledge_base")
    else:
        print("no conversational_ai")

except Exception as e:
    print(f"Error: {e}")
