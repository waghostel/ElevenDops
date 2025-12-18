---
inclusion: fileMatch
fileMatchPattern: "streamlit_app/**/*.py"
---

# Streamlit Page Development Guidelines

## User Requirements Reference
See complete requirements: #[[file:user-need/user-need-phase1.md]]

## Page Structure
Each page in `streamlit_app/pages/` follows this pattern:
1. Page config and title
2. Session state initialization
3. UI components
4. Backend API calls (via `services/backend_api.py`)
5. Result display

## Pages Overview

### 1_Doctor_Dashboard.py
- Display system statistics from Firestore
- Show: uploaded docs count, agents count, audio files count, recent activity
- No direct API calls to ElevenLabs

### 2_Upload_Knowledge.py
- File upload (Markdown/TXT)
- Form: disease name, document type
- Call backend to save to Firestore + sync to ElevenLabs KB

### 3_Education_Audio.py
- Select knowledge document
- Generate script preview (LLM)
- Doctor review/edit
- Generate TTS audio
- Display audio player and URL

### 4_Agent_Setup.py
- Agent name input
- Multi-select knowledge documents
- Voice model selection
- Answer style: professional/friendly/educational

### 5_Patient_Test.py
- Patient ID input
- Agent/disease selection
- Audio playback
- Voice conversation interface

### 6_Conversation_Logs.py
- Patient ID filter
- Display: questions (answered/unanswered), agent responses
- Flag items requiring doctor attention

## UI Patterns
```python
import streamlit as st
from services.backend_api import BackendAPI

api = BackendAPI()

st.title("頁面標題")

# Form handling
with st.form("form_key"):
    input_value = st.text_input("標籤")
    if st.form_submit_button("提交"):
        result = api.some_endpoint(input_value)
        st.success("完成")
```

## Error Handling
- Use `st.error()` for user-facing errors
- Log technical errors for debugging
- Provide clear Chinese error messages
