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
