# Get Conversation Details

Retrieve transcript and metadata for a specific conversation.

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)

response = client.conversational_ai.conversations.get(
    conversation_id="123"
)
print(response)
```

## Response Structure

```json
{
  "agent_id": "123",
  "conversation_id": "123",
  "status": "processing",
  "transcript": [
    {
      "role": "user",
      "time_in_call_secs": 10,
      "message": "Hello, how are you?"
    },
    {
      "role": "agent",
      "time_in_call_secs": 12,
      "message": "I'm doing well, thank you."
    }
  ],
  "metadata": {
    "start_time_unix_secs": 1714423232,
    "call_duration_secs": 10
  },
  "analysis": {
    // (Likely structure if Data Collection/Success criteria are enabled)
  },
  "has_audio": true,
  "has_user_audio": true,
  "has_response_audio": true
}
```
