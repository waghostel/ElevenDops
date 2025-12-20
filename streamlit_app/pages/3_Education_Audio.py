"""Education Audio Generation Page.

This page allows doctors to generate audio patient education materials
from knowledge documents using ElevenLabs TTS.
"""

import asyncio
import logging
from typing import List, Optional

import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.models import (
    AudioResponse,
    KnowledgeDocument,
    VoiceOption,
)

# Page configuration
st.set_page_config(page_title="Education Audio", page_icon="🎧", layout="wide")

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


async def load_documents() -> List[KnowledgeDocument]:
    """Load available knowledge documents."""
    try:
        return await client.get_knowledge_documents()
    except Exception as e:
        st.error(f"Unable to load documents. Please check your connection. (Error: {e})")
        return []


async def load_voices() -> List[VoiceOption]:
    """Load available voices."""
    try:
        return await client.get_available_voices()
    except Exception as e:
        st.error(f"Unable to load voice options. (Error: {e})")
        return []


async def generate_script(knowledge_id: str):
    """Generate script from document."""
    try:
        with st.spinner("Generating script with AI..."):
            response = await client.generate_script(knowledge_id)
            st.session_state.generated_script = response.script
            st.toast("Script generated successfully!", icon="📝")
    except Exception as e:
        st.error(f"Script generation failed. Please try again. (Error: {e})")


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


async def render_script_editor():
    """Render script generation and editing section."""
    st.subheader("2. Script Editor")
    
    if not st.session_state.selected_document:
        st.info("Please select a document specifically to proceed.")
        return

    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("✨ Generate Script", key="generate_script_btn"):
            await generate_script(st.session_state.selected_document.knowledge_id)

    if st.session_state.generated_script:
        st.markdown("**Review and Edit Script:**")
        edited_script = st.text_area(
            "Script Content",
            value=st.session_state.generated_script,
            height=300,
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
        st.session_state.voices = await load_voices()

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
    
    documents = await load_documents()
    
    await render_document_selection(documents)
    await render_script_editor()
    await render_audio_generation()
    st.divider()
    await render_audio_history()


if __name__ == "__main__":
    asyncio.run(main())
