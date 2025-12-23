# Create agent

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
client.conversational_ai.agents.create()
```

## Structure

The Python SDK uses `client.conversational_ai.agents` to access Agent related functionality.

## Request

(Parameters were not fully listed in the snippet, but include `agent_id` in response).

[Try it](https://elevenlabs.io/docs/api-reference/agents/create?explorer=true)

# Get Agent

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
response = client.conversational_ai.get_agent(
    agent_id="agent_id"
)
print(response)
```

## Response

```json
{
  "agent_id": "agent_7101k5zvyjhmfg983brhmhkd98n6",
  "name": "My Agent",
  "conversation_config": {
    "asr": {
      "quality": "high",
      "provider": "elevenlabs",
      "user_input_audio_format": "pcm_16000",
      "keywords": []
    }
  },
  "metadata": {},
  "workflow": {}
}
```

# Delete Agent

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
client.conversational_ai.delete_agent(
    agent_id="agent_id"
)
```

## Response

Returns `200 OK` on success.
