# Stream Speech: Real-time Voice Conversations

Converts text into speech using a voice of your choice and returns audio as an audio stream.

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)

client.text_to_speech.stream(
 voice_id="JBFqnCBsd6RMkjVDRZzb",
 output_format="mp3_44100_128",
 text="The first move is what sets everything in motion.",
 model_id="eleven_multilingual_v2"
)
```

## Parameters

**voice_id** (Path): ID of the voice to be used.
**output_format** (Query): Output format (e.g., `mp3_44100_128`, `ulaw_8000`).
**model_id** (Request): Identifier of the model (e.g., `eleven_multilingual_v2`).
**optimize_streaming_latency**:

- 0: Default mode (no latency optimizations)
- 1: Normal latency optimizations (about 50% improvement)
- 2: Strong latency optimizations (about 75% improvement)
- 3: Max latency optimizations
- 4: Max latency optimizations with text normalizer turned off (best latency, but potential mispronunciations)

**stream** (Internal): The SDK handles the chunked transfer encoding.
