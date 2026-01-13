import os
import uuid
import logging
from dotenv import load_dotenv
try:
    from elevenlabs import ElevenLabs
except ImportError:
    from elevenlabs.client import ElevenLabs

# Load environment
load_dotenv(override=True)
api_key = os.getenv("ELEVENLABS_API_KEY")

if not api_key:
    print("SKIPPING TEST: No ELEVENLABS_API_KEY found.")
    exit(0)

client = ElevenLabs(api_key=api_key)
voice_id = "UgBBYS2sOqTuMpoF3BR0" # Default 'Mark' voice

def test_create_agent_custom(name, model_id, config_override):
    print(f"\n--- Testing: {name}, model={model_id} ---")
    print(f"Config: {config_override}")
    agent_name = f"Test_{name}_{uuid.uuid4().hex[:6]}"
    
    # Base config
    agent_config = {
        "prompt": {"prompt": "You are a test agent."},
        "first_message": "Hello."
    }
    # Apply overrides
    agent_config.update(config_override)

    try:
        response = client.conversational_ai.agents.create(
            name=agent_name,
            conversation_config={
                "agent": agent_config,
                "tts": {
                    "voice_id": voice_id,
                    "model_id": model_id
                }
            }
        )
        print(f"SUCCESS! Agent ID: {response.agent_id}")
        # Cleanup
        client.conversational_ai.agents.delete(response.agent_id)
        return True
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        if hasattr(e, 'body'):
            print(f"   Body: {e.body}")
        return False

print("Starting Cleaner Verification...")

# 1. Hypothesis: If we omit 'language' entirely for v2.5, does it default to auto/universal?
test_create_agent_custom("No_Lang_V25", "eleven_turbo_v2_5", {})

# 2. Hypothesis: If we set language='en' AND provide language_presets, maybe it works?
# (This failed before, but let's be precise)
test_create_agent_custom("En_Presets_V25", "eleven_turbo_v2_5", {
    "language": "en",
    "language_presets": {
        "en": {"voice_id": voice_id},
        "fr": {"voice_id": voice_id}
    }
})

# 3. Hypothesis: If we set language='en' but NO language_presets, it failed.
# What if we set language to None explicitly? (Likely same as omit)
test_create_agent_custom("None_Lang_V25", "eleven_turbo_v2_5", {"language": None})
