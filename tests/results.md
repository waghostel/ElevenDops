Traceback (most recent call last):
Starting Verification...

--- Testing: lang=en, model=eleven_turbo_v2_5, list=['en'] ---
  File "C:\Users\Cheney\Documents\Github\ElevenDops\tests\verify_agent_creation.py", line 37, in test_create_agent
    response = client.conversational_ai.agents.create(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Cheney\Documents\Github\ElevenDops\.venv\Lib\site-packages\elevenlabs\conversational_ai\agents\client.py", line 103, in create
    _response = self._raw_client.create(
                ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Cheney\Documents\Github\ElevenDops\.venv\Lib\site-packages\elevenlabs\conversational_ai\agents\raw_client.py", line 122, in create
    raise ApiError(status_code=_response.status_code, headers=dict(_response.headers), body=_response_json)
elevenlabs.core.api_error.ApiError: headers: {'date': 'Tue, 13 Jan 2026 07:03:03 GMT', 'server': 'uvicorn', 'content-length': '2478', 'content-type': 'application/json', 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST, PATCH, OPTIONS, DELETE, GET, PUT', 'access-control-max-age': '600', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'x-trace-id': 'a4b843807e8acc1a6ed071a41223752f', 'x-region': 'us-central1', 'via': '1.1 google, 1.1 google', 'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000'}, status_code: 400, body: {'detail': {'status': 'input_invalid', 'message': '[{"type":"value_error","loc":[],"msg":"Value error, English Agents must use turbo or flash v2.","input":{"asr":{"quality":"high","provider":"elevenlabs","user_input_audio_format":"pcm_16000","keywords":[]},"turn":{"turn_timeout":7.0,"initial_wait_time":null,"silence_end_call_timeout":-1,"soft_timeout_config":{"timeout_seconds":-1.0,"message":"Hhmmmm...yeah give me a second...","use_llm_generated_message":false},"mode":"turn","turn_eagerness":"normal"},"tts":{"model_id":"eleven_turbo_v2_5","voice_id":"UgBBYS2sOqTuMpoF3BR0","supported_voices":[],"suggested_audio_tags":[],"agent_output_audio_format":"pcm_16000","optimize_streaming_latency":3,"stability":0.5,"speed":1.0,"similarity_boost":0.8,"text_normalisation_type":"system_prompt","pronunciation_dictionary_locators":[]},"conversation":{"text_only":false,"max_duration_seconds":600,"client_events":["audio","interruption","agent_response","user_transcript","agent_response_correction","agent_tool_response"],"monitoring_enabled":false,"monitoring_events":["user_transcript","agent_response","agent_response_correction"]},"language_presets":{},"vad":{"background_voice_detection":false},"agent":{"first_message":"Hello.","language":"en","hinglish_mode":false,"dynamic_variables":{"dynamic_variable_placeholders":{}},"disable_first_message_interruptions":false,"prompt":{"prompt":"You are a test agent.","llm":"gemini-2.5-flash","reasoning_effort":null,"thinking_budget":null,"temperature":0.0,"max_tokens":-1,"tool_ids":[],"built_in_tools":{"end_call":null,"language_detection":null,"transfer_to_agent":null,"transfer_to_number":null,"skip_turn":null,"play_keypad_touch_tone":null,"voicemail_detection":null},"mcp_server_ids":[],"native_mcp_server_ids":[],"knowledge_base":[],"custom_llm":null,"ignore_default_personality":false,"rag":{"enabled":false,"embedding_model":"e5_mistral_7b_instruct","max_vector_distance":0.6,"max_documents_length":50000,"max_retrieved_rag_chunks_count":20,"query_rewrite_prompt_override":null},"timezone":null,"backup_llm_config":{"preference":"default"},"cascade_timeout_seconds":8.0,"tools":[]}}},"ctx":{"error":"English Agents must use turbo or flash v2."},"url":"https://errors.pydantic.dev/2.10/v/value_error"}]'}}

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\Cheney\Documents\Github\ElevenDops\tests\verify_agent_creation.py", line 61, in <module>
    test_create_agent("Fail_En_V25", "en", "eleven_turbo_v2_5", ["en"])
  File "C:\Users\Cheney\Documents\Github\ElevenDops\tests\verify_agent_creation.py", line 52, in test_create_agent
    print(f"\u274c FAILED: {type(e).__name__}: {e}")
UnicodeEncodeError: 'cp950' codec can't encode character '\u274c' in position 0: illegal multibyte sequence
