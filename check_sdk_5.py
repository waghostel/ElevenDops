
import elevenlabs
from elevenlabs.client import ElevenLabs
import inspect

try:
    client = ElevenLabs(api_key="dummy")
    method = client.conversational_ai.add_to_knowledge_base
    print(f"Signature: {inspect.signature(method)}")
    print(f"Docstring: {method.__doc__}")

except Exception as e:
    print(f"Error: {e}")
