"""Education Audio Generation Page.

This page allows doctors to generate audio patient education materials
from knowledge documents using ElevenLabs TTS.
"""

import asyncio
import logging
import time
from typing import List, Optional

import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.models import (
    AudioResponse,
    KnowledgeDocument,
    VoiceOption,
)
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer

# Page configuration
st.set_page_config(page_title="Education Audio", page_icon="🎧", layout="wide")

render_sidebar()

# Initialize client
client = get_backend_client()

# Session state initialization
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None
if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""
if "selected_voice_id" not in st.session_state:
    st.session_state.selected_voice_id = None
if "voices" not in st.session_state:
    st.session_state.voices = []
if "selected_llm_model" not in st.session_state:
    st.session_state.selected_llm_model = "gemini-2.5-flash-lite"
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = None


# Cache settings
DOCUMENTS_CACHE_TTL = 30  # seconds
VOICES_CACHE_TTL = 300  # 5 minutes


def render_header():
    """Render page header."""
    st.title("🎧 Patient Education Audio")
    st.markdown(
        """
        Generate high-quality audio education materials for your patients using 
        ElevenLabs AI voices. Select a knowledge document, customize the script, 
        and choose a voice.
        """
    )


async def load_documents_cached() -> List[KnowledgeDocument]:
    """Load documents with session state caching (async-compatible)."""
    cache_key = "_documents_cache"
    cache_time_key = "_documents_cache_time"
    
    now = time.time()
    
    # Check if cache exists and is still valid
    if (
        cache_key in st.session_state
        and cache_time_key in st.session_state
        and (now - st.session_state[cache_time_key]) < DOCUMENTS_CACHE_TTL
    ):
        return st.session_state[cache_key]
    
    # Fetch fresh data
    try:
        documents = await client.get_knowledge_documents()
        st.session_state[cache_key] = documents
        st.session_state[cache_time_key] = now
        return documents
    except Exception as e:
        st.error(f"Unable to load documents. Please check your connection. (Error: {e})")
        return []


async def load_voices_cached() -> List[VoiceOption]:
    """Load voices with session state caching (async-compatible)."""
    cache_key = "_voices_cache"
    cache_time_key = "_voices_cache_time"
    
    now = time.time()
    
    # Check if cache exists and is still valid
    if (
        cache_key in st.session_state
        and cache_time_key in st.session_state
        and (now - st.session_state[cache_time_key]) < VOICES_CACHE_TTL
    ):
        return st.session_state[cache_key]
    
    # Fetch fresh data
    try:
        voices = await client.get_available_voices()
        st.session_state[cache_key] = voices
        st.session_state[cache_time_key] = now
        return voices
    except Exception as e:
        st.error(f"Unable to load voice options. (Error: {e})")
        return []


async def generate_script(knowledge_id: str):
    """Generate script from document using streaming for real-time feedback."""
    model = st.session_state.selected_llm_model
    prompt = st.session_state.custom_prompt
    
    # Create placeholders for streaming display
    progress_placeholder = st.empty()
    script_placeholder = st.empty()
    status_placeholder = st.empty()
    
    full_script = ""
    final_model_used = ""
    
    try:
        status_placeholder.info("🚀 Starting AI script generation...")
        
        async for event in client.generate_script_stream(
            knowledge_id=knowledge_id,
            model_name=model,
            custom_prompt=prompt
        ):
            event_type = event.get("type")
            
            if event_type == "token":
                # Append token and update display
                full_script += event.get("content", "")
                script_placeholder.text_area(
                    "📝 Generating script...",
                    value=full_script,
                    height=400,
                    disabled=True,
                    key=f"streaming_script_{len(full_script)}"
                )
                status_placeholder.caption(f"⏳ Generating... ({len(full_script):,} characters)")
                
            elif event_type == "complete":
                # Generation complete
                final_script = event.get("script", full_script)
                final_model_used = event.get("model_used", model)
                
                st.session_state.generated_script = final_script
                
                # Clear streaming placeholders
                progress_placeholder.empty()
                script_placeholder.empty()
                status_placeholder.empty()
                
                st.toast(f"✅ Script generated using {final_model_used}!", icon="📝")
                st.rerun()
                
            elif event_type == "error":
                # Error occurred during generation
                error_msg = event.get("message", "Unknown error")
                status_placeholder.empty()
                script_placeholder.empty()
                
                # If we have partial content, offer to use it
                if full_script:
                    st.warning(
                        f"⚠️ Generation interrupted: {error_msg}\n\n"
                        f"Partial content ({len(full_script):,} chars) has been preserved."
                    )
                    st.session_state.generated_script = full_script
                else:
                    st.error(f"Script generation failed: {error_msg}")
                return
                
    except Exception as e:
        # Clean up placeholders on error
        progress_placeholder.empty()
        script_placeholder.empty()
        status_placeholder.empty()
        
        error_msg = str(e) if str(e) else repr(e)
        st.error(f"Script generation failed: {error_msg}")


async def generate_audio(knowledge_id: str, script: str, voice_id: str):
    """Generate audio from script."""
    try:
        with st.spinner("Synthesizing audio with ElevenLabs..."):
            await client.generate_audio(knowledge_id, script, voice_id)
            st.toast("Audio generated successfully!", icon="✅")
            # Clear script to allow new generation or keep it? 
            # Requirements say: "After successful generation, the audio should appear in the 'Audio History' list"
            # We'll reload the history.
            st.rerun()
    except Exception as e:
        st.error(f"Audio generation failed. Please check your quota or try again. (Error: {e})")


async def render_document_selection(documents: List[KnowledgeDocument]):
    """Render document selection section."""
    st.subheader("1. Select Knowledge Document")
    
    if not documents:
        st.info("No knowledge documents found. Please upload documents in the Knowledge Base first.")
        return

    doc_options = {doc.disease_name: doc for doc in documents}
    selected_name = st.selectbox(
        "Choose a condition/procedure:",
        options=list(doc_options.keys()),
        index=None,
        placeholder="Select a document...",
    )

    if selected_name:
        selected_doc = doc_options[selected_name]
        
        # If selection changed, reset state
        if (
            st.session_state.selected_document
            and st.session_state.selected_document.knowledge_id != selected_doc.knowledge_id
        ):
            st.session_state.generated_script = ""
            st.session_state.selected_voice_id = None
            
        st.session_state.selected_document = selected_doc
        
        with st.expander("View Document Content", expanded=False):
            st.markdown(selected_doc.raw_content)


@st.dialog("Customize Prompt")
def render_prompt_editor_dialog():
    """Render dialog to customize script generation prompt."""
    st.markdown("Customize the instructions for the AI script writer.")
    
    # Default text to show if no custom prompt set yet
    default_text = (
        st.session_state.custom_prompt 
        if st.session_state.custom_prompt 
        else """# Role
You are a medical education script writer specializing in creating voice-optimized content.

# Goal
Generate a patient education script from the provided medical knowledge document.

# Guidelines
- Write in a conversational, warm tone
- Use short, clear sentences
- Include natural pauses using punctuation
- Avoid complex medical jargon"""
    )

    new_prompt = st.text_area(
        "Prompt Content", 
        value=default_text,
        height=300
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset to Default", use_container_width=True):
            st.session_state.custom_prompt = None
            st.rerun()
            
    with col2:
        if st.button("Save Changes", type="primary", use_container_width=True):
            st.session_state.custom_prompt = new_prompt
            # st.dialog automatically handles closing on rerun usually
            st.rerun()


async def render_script_editor():
    """Render script generation and editing section."""
    st.subheader("2. Script Editor")
    
    if not st.session_state.selected_document:
        st.info("Please select a document specifically to proceed.")
        return

    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.session_state.selected_llm_model = st.selectbox(
            "AI Model",
            options=["gemini-1.5-flash-8b", "gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-3-pro-preview"],
            index=1, # Default to gemini-2.5-flash-lite
            help="Select the AI model for script generation"
        )
        
        if st.button("⚙️ Customize Prompt", use_container_width=True):
            render_prompt_editor_dialog()
            
        st.divider()

        if st.button("✨ Generate Script", key="generate_script_btn", type="primary", use_container_width=True):
            await generate_script(st.session_state.selected_document.knowledge_id)

    if st.session_state.generated_script:
        st.markdown("**Review and Edit Script:**")
        edited_script = st.text_area(
            "Script Content",
            value=st.session_state.generated_script,
            height=600,
            label_visibility="collapsed",
            key="script_editor_area"
        )
        st.session_state.generated_script = edited_script
        st.caption(f"Character count: {len(edited_script)}")


async def render_audio_generation():
    """Render voice selection and audio generation."""
    st.subheader("3. Voice & Generation")

    if not st.session_state.generated_script:
        st.info("Generate or write a script to proceed.")
        return

    # Load voices if not loaded
    if not st.session_state.voices:
        st.session_state.voices = await load_voices_cached()

    if not st.session_state.voices:
        st.warning("No voices available. Check API connection.")
        return

    voice_options = {v.name: v for v in st.session_state.voices}
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_voice_name = st.selectbox(
            "Select Voice",
            options=list(voice_options.keys())
        )
        
    selected_voice = voice_options[selected_voice_name]
    st.session_state.selected_voice_id = selected_voice.voice_id
    
    with col2:
        if selected_voice.preview_url:
            st.audio(selected_voice.preview_url, format="audio/mpeg")
            st.caption("Voice Preview")

    st.divider()
    
    if st.button("Generate Audio 🎵", type="primary", use_container_width=True, key="generate_audio_btn"):
        await generate_audio(
            st.session_state.selected_document.knowledge_id,
            st.session_state.generated_script,
            st.session_state.selected_voice_id,
        )


async def render_audio_history():
    """Render audio history for the selected document."""
    if not st.session_state.selected_document:
        return

    st.subheader("Audio History")
    
    try:
        audio_files = await client.get_audio_files(st.session_state.selected_document.knowledge_id)
        
        if not audio_files:
            st.caption("No audio files generated yet for this document.")
            return

        for audio in audio_files:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Generated:** {audio.created_at.strftime('%Y-%m-%d %H:%M')}")
                    with st.expander("View Script"):
                        st.text(audio.script[:100] + "..." if len(audio.script) > 100 else audio.script)
                with col2:
                    st.audio(audio.audio_url, format="audio/mpeg")

    except Exception as e:
        st.error(f"Unable to load audio history. Please refer to conversion logs or try again later. (Error: {e})")


async def main():
    """Main page execution."""
    render_header()
    
    documents = await load_documents_cached()
    
    await render_document_selection(documents)
    await render_script_editor()
    await render_audio_generation()
    st.divider()
    await render_audio_history()
    render_footer()


if __name__ == "__main__":
    asyncio.run(main())
