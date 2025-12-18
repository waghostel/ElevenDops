# Create speech

```python
from elevenlabs import ElevenLabs
client = ElevenLabs(
  base_url="https://api.elevenlabs.io"
)
client.text_to_speech.convert(
 voice_id="JBFqnCBsd6RMkjVDRZzb",
 output_format="mp3_44100_128",
 text="The first move is what sets everything in motion.",
 model_id="eleven_multilingual_v2"
)
```

## Path parameters

**voice_id**: ID of the voice to be used. Use the [Get voices](https://elevenlabs.io/docs/api-reference/voices/search) endpoint list all the available voices.

## Query parameters

**enable_logging**:
When enable_logging is set to false zero retention mode will be used for the request. This will mean history features are unavailable for this request, including request stitching. Zero retention mode may only be used by enterprise customers.

**output_format**:
Output format of the generated audio. Formatted as codec_sample_rate_bitrate. So an mp3 with 22.05kHz sample rate at 32kbs is represented as mp3_22050_32. MP3 with 192kbps bitrate requires you to be subscribed to Creator tier or above. PCM with 44.1kHz sample rate requires you to be subscribed to Pro tier or above. Note that the μ-law format (sometimes written mu-law, often approximated as u-law) is commonly used for Twilio audio inputs.

## Request

**model_id**:
Identifier of the model that will be used, you can query them using GET /v1/models. The model needs to have support for text to speech, you can check this using the can_do_text_to_speech property.

**language_code**:
Language code (ISO 639-1) used to enforce a language for the model and text normalization. If the model does not support provided language code, an error will be returned.

**pronunciation_dictionary_locators**:
A list of pronunciation dictionary locators (id, version_id) to be applied to the text. They will be applied in order. You may have up to 3 locators per request

**previous_request_ids**:
A list of request_id of the samples that were generated before this generation. Can be used to improve the speech’s continuity when splitting up a large task into multiple requests. The results will be best when the same model is used across the generations. In case both previous_text and previous_request_ids is send, previous_text will be ignored. A maximum of 3 request_ids can be send.

**next_request_ids**:
A list of request_id of the samples that come after this generation. next_request_ids is especially useful for maintaining the speech’s continuity when regenerating a sample that has had some audio quality issues.

**text_normalization**:
This parameter controls text normalization with three modes: ‘auto’, ‘on’, and ‘off’. When set to ‘auto’, the system will automatically decide whether to apply text normalization (e.g., spelling out numbers). With ‘on’, text normalization will always be applied, while with ‘off’, it will be skipped.
