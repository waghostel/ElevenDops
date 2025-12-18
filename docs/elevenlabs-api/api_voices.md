# Create PVC voice

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
client.voices.pvc.create(
 name="John Smith",
 language="en"
)
```

## Request

**name**:
<=100 characters

**language**:
<=500 characters
