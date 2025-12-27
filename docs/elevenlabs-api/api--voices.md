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

# Get voices

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
response = client.voices.get_all()
print(response.voices)
```

## Response

```json
{
  "voices": [
    {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "name": "Rachel",
      "samples": [],
      "category": "premade",
      "fine_tuning": {
        "is_allowed_to_fine_tune": false,
        "finetuning_state": "not_started",
        "verification_failures": [],
        "verification_attempts_count": 0,
        "manual_verification_requested": false,
        "language": "en"
      },
      "labels": {},
      "description": null,
      "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/21m00Tcm4TlvDq8ikWAM/bea1b4e0-f8c5-442d-a135-c3ca281y194e.mp3",
      "available_for_tiers": [],
      "settings": null,
      "sharing": null,
      "high_quality_base_model_ids": [],
      "safety_control": null,
      "voice_verification": {
        "requires_verification": false,
        "is_verified": false,
        "verification_failures": [],
        "verification_attempts_count": 0,
        "language": null,
        "verification_attempts": null
      },
      "owner_id": null,
      "permission_on_resource": null
    }
  ]
}
```
