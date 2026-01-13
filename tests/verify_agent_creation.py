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

def test_create_agent(name, language, model_id, languages_list=None):
    print(f"\n--- Testing: lang={language}, model={model_id}, list={languages_list} ---")
    agent_name = f"Test_{name}_{uuid.uuid4().hex[:6]}"
    
    agent_config = {
        "prompt": {"prompt": "You are a test agent."},
        "first_message": "Hello.",
        "language": language
    }
    
    if languages_list and len(languages_list) > 1:
        agent_config["language_presets"] = {
            lang: {"voice_id": voice_id} for lang in languages_list
        }

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
        # Try to print body if available
        if hasattr(e, 'body'):
            print(f"   Body: {e.body}")
        return False

print("Starting Verification...")

# 1. The Failing Case: English + Turbo v2.5
test_create_agent("Fail_En_V25", "en", "eleven_turbo_v2_5", ["en"])

# 2. English + Turbo v2
test_create_agent("Success_En_V2", "en", "eleven_turbo_v2", ["en"])

# 3. Multilingual: English + French, Primary=En, Model=Turbo v2.5
test_create_agent("Multi_EnFr_V25", "en", "eleven_turbo_v2_5", ["en", "fr"])

# 4. Multilingual: English + French, Primary=Fr, Model=Turbo v2.5
test_create_agent("Multi_FrEn_V25", "fr", "eleven_turbo_v2_5", ["fr", "en"])
