import elevenlabs
from elevenlabs.client import ElevenLabs

print(f"ElevenLabs version: {elevenlabs.__version__}")

try:
    client = ElevenLabs(api_key="dummy")
    # Check conversational_ai structure
    if hasattr(client, "conversational_ai"):
        print("has conversational_ai")
        cai = client.conversational_ai
        if hasattr(cai, "knowledge_base"):
            print("has knowledge_base")
            kb = cai.knowledge_base
            print(f"KB methods: {dir(kb)}")
            # Check for documents attribute if strict hierarchy
            if hasattr(kb, "documents"):
                 print(f"KB Documents methods: {dir(kb.documents)}")
            
            # Check for create_document directly on KB or documents
        else:
            print("no knowledge_base")
    else:
        print("no conversational_ai")

except Exception as e:
    print(f"Error: {e}")
