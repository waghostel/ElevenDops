# Agent Customization Features - TODO

**Created:** 2026-01-13  
**Status:** Research Complete, Implementation Pending

## Overview

This document outlines potential customization features for the Agent Setup page based on ElevenLabs Conversational AI API capabilities.

---

## High Priority Features

### 1. LLM Model Selection ⭐ (IN PROGRESS)

**Current State:** Uses ElevenLabs default LLM  
**Proposed:** Dropdown selector for LLM model

**Supported Models:**

- **Google Gemini:**
  - `gemini-2.5-flash` (recommended default - balanced performance)
  - `gemini-2.0-flash`
  - `gemini-1.5-flash`
  - `gemini-1.5-pro`
- **OpenAI GPT:**
  - `gpt-4o` (recommended for complex reasoning)
  - `gpt-4o-mini`
  - `gpt-4-turbo`
  - `gpt-3.5-turbo`
- **Anthropic Claude:**
  - `claude-sonnet-4` (highest accuracy)
  - `claude-sonnet-3.7`
  - `claude-sonnet-3.5`
  - `claude-haiku-4.5`

**Implementation Notes:**

- Add `llm` configuration to `conversation_config` in `elevenlabs_service.py`
- Use same model configuration pattern as Education Audio page (`ChatGoogleGenerativeAI`)
- Store model selection in agent database record

**API Structure:**

```python
conversation_config={
    "agent": {...},
    "tts": {...},
    "llm": {
        "model_id": "gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 500
    }
}
```

---

### 2. First Message Customization ⭐ (IN PROGRESS)

**Current State:** Hardcoded to "Hello! I'm your medical assistant. How can I help you today?"  
**Proposed:** Customizable text input field

**Use Cases:**

- Professional: "Good day. I'm here to answer your medical questions."
- Friendly: "Hi there! I'm your friendly health assistant. What can I help you with?"
- Educational: "Welcome! I'm here to help you learn about your health condition."

**Implementation:**

- Add `first_message` field to `AgentCreateRequest` schema
- Update `agent_config["first_message"]` in `create_agent()` method
- Add text input in Agent Setup UI (Identity tab)

---

## Medium Priority Features

### 3. Temperature Control

**Current State:** Not configurable (uses ElevenLabs default)  
**Proposed:** Slider (0.0 - 1.0)

**Impact:**

- Lower (0.0-0.3): Deterministic, consistent medical responses
- Medium (0.4-0.7): Balanced creativity and consistency
- Higher (0.8-1.0): More creative, varied responses

**Default:** 0.7 (matches Education Audio configuration)

---

### 4. Max Response Tokens

**Current State:** Not configurable  
**Proposed:** Number input (100-2000)

**Use Cases:**

- Short answers: 100-300 tokens
- Standard responses: 300-500 tokens
- Detailed explanations: 500-2000 tokens

**Default:** 500 tokens

---

### 5. Backup LLM Model

**Current State:** No fallback mechanism  
**Proposed:** Optional secondary model selection

**Use Cases:**

- Primary model unavailable
- Rate limit exceeded
- Cost optimization (fallback to cheaper model)

---

## Lower Priority Features

### 6. ASR (Speech Recognition) Settings

**Current State:** Uses ElevenLabs default ASR  
**Proposed:** Quality toggle (standard/high)

**API Structure:**

```python
conversation_config={
    "asr": {
        "quality": "high",  # or "standard"
        "provider": "elevenlabs",
        "user_input_audio_format": "pcm_16000"
    }
}
```

---

### 7. Conversation Timeout

**Current State:** Uses ElevenLabs default  
**Proposed:** Seconds input (30-300)

**Impact:** How long agent waits for user input before ending conversation

---

### 8. Client Tools Configuration

**Current State:** Not implemented  
**Proposed:** Advanced feature for future phases

**Use Cases:**

- Enable client-side operations (UI interactions)
- Custom function calling
- External API integrations

**Reference:** [ElevenLabs Client Tools Documentation](https://elevenlabs.io/docs/agents-platform/customization/tools/client-tools)

---

## Implementation Roadmap

### Phase 1 (Current)

- [x] Research ElevenLabs API capabilities
- [ ] Implement LLM Model Selection
- [ ] Implement First Message Customization
- [ ] Update database schema
- [ ] Update UI (Agent Setup page)

### Phase 2 (Future)

- [ ] Temperature Control
- [ ] Max Response Tokens
- [ ] Backup LLM Model

### Phase 3 (Advanced)

- [ ] ASR Settings
- [ ] Conversation Timeout
- [ ] Client Tools Configuration

---

## Technical References

- **ElevenLabs Agents API:** `docs/elevenlabs-api/api--agents.md`
- **Prompting Guide:** `docs/elevenlabs-api/guide--prompting.md`
- **Current Implementation:** `backend/services/elevenlabs_service.py`
- **Education Audio LLM Config:** `backend/services/langgraph_workflow.py` (lines 258-265)

---

## Notes

- All LLM configurations should follow the pattern used in Education Audio for consistency
- Consider adding "Advanced Options" collapsible section in UI to avoid overwhelming users
- Ensure backward compatibility - existing agents should continue working with defaults
