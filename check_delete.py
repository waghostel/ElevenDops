
import elevenlabs
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key="dummy")
cai = client.conversational_ai

print("Searching for delete/remove methods...")

# Check top level cai
possible = [d for d in dir(cai) if "delete" in d or "remove" in d]
print(f"ConvAI candidates: {possible}")

# Check inside knowledge_base
if hasattr(cai, "knowledge_base"):
    kb = cai.knowledge_base
    possible_kb = [d for d in dir(kb) if "delete" in d or "remove" in d]
    print(f"KB candidates: {possible_kb}")
