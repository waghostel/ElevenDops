"""Education Audio Generation Page.

This page allows doctors to generate audio patient education materials
from knowledge documents using ElevenLabs TTS.
"""

import asyncio
import logging
from typing import List, Optional, Any

import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.models import (
    AudioResponse,
    KnowledgeDocument,
    VoiceOption,
    CustomTemplateCreate,
)
from streamlit_app.services.cached_data import (
    get_documents_cached,
    get_voices_cached,
    run_async,
)
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer
from streamlit_app.components.error_console import add_error_to_log, render_error_console

# Page configuration
st.set_page_config(page_title="Education Audio", page_icon="🎧", layout="wide")

render_sidebar()

# Initialize client
client = get_backend_client()

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
if "selected_templates" not in st.session_state:
    st.session_state.selected_templates = ["pre_surgery"]
if "quick_instructions" not in st.session_state:
    st.session_state.quick_instructions = ""
if "use_template_mode" not in st.session_state:
    st.session_state.use_template_mode = True
if "available_templates" not in st.session_state:
    st.session_state.available_templates = []
if "custom_system_prompt" not in st.session_state:
    st.session_state.custom_system_prompt = None
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "generation_id" not in st.session_state:
    st.session_state.generation_id = 0
if "multi_speaker_enabled" not in st.session_state:
    st.session_state.multi_speaker_enabled = False
if "speaker1_languages" not in st.session_state:
    st.session_state.speaker1_languages = []
if "speaker2_languages" not in st.session_state:
    st.session_state.speaker2_languages = []
if "speaker1_voice_id" not in st.session_state:
    st.session_state.speaker1_voice_id = None
if "speaker2_voice_id" not in st.session_state:
    st.session_state.speaker2_voice_id = None
if "target_duration_minutes" not in st.session_state:
    st.session_state.target_duration_minutes = 3
# Pending template operations (for async handling outside dialogs)
if "_pending_template_op" not in st.session_state:
    st.session_state._pending_template_op = None


# Process pending template operations (triggered by dialog form submissions)
if st.session_state._pending_template_op:
    op = st.session_state._pending_template_op
    st.session_state._pending_template_op = None
    
    try:
        if op["action"] == "create":
            run_async(client.create_custom_template(op["template"]))
            st.toast("Template created successfully!", icon="✅")
        elif op["action"] == "delete":
            run_async(client.delete_custom_template(op["template_id"]))
            st.toast("Template deleted!", icon="🗑️")
        elif op["action"] == "update":
            run_async(client.update_custom_template(
                op["template_id"],
                display_name=op["display_name"],
                description=op["description"],
                content=op["content"]
            ))
            st.toast("Template updated!", icon="✅")
        
        # Reload templates after any operation
        st.session_state.available_templates = run_async(client.get_templates())
    except Exception as e:
        add_error_to_log(f"Template operation failed: {e}")


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





async def generate_script(knowledge_id: str, script_placeholder: Optional[Any] = None):
    """Generate script from document using streaming for real-time feedback."""
    model = st.session_state.selected_llm_model
    st.session_state.is_generating = True
    
    # Increment generation_id to force new widget key on completion
    st.session_state.generation_id += 1
    current_gen_id = st.session_state.generation_id
    
    # Clear previous widget state to ensure fresh display on completion
    old_key = f"script_editor_area_{current_gen_id - 1}"
    if old_key in st.session_state:
        del st.session_state[old_key]
    
    # Determine whether to use templates or custom prompt
    use_templates = st.session_state.use_template_mode
    template_ids = st.session_state.selected_templates if use_templates else None
    quick_instructions = st.session_state.quick_instructions if use_templates else None
    custom_prompt = st.session_state.custom_prompt if not use_templates else None
    system_prompt_override = st.session_state.custom_system_prompt if use_templates else None
    # Determine multi-speaker mode
    multi_speaker = st.session_state.multi_speaker_enabled if use_templates else False
    
    # In single-speaker mode, use Speaker 1 languages as output language
    # In multi-speaker mode, use both speaker languages
    if multi_speaker:
        preferred_languages = None  # Multi-speaker handles languages differently
        speaker1_languages = st.session_state.speaker1_languages if use_templates else None
        speaker2_languages = st.session_state.speaker2_languages if use_templates else None
    else:
        # Single-speaker: use Speaker 1 languages as the output language
        preferred_languages = st.session_state.speaker1_languages if use_templates else None
        speaker1_languages = None
        speaker2_languages = None
    
    # Create placeholders for streaming display
    progress_placeholder = st.empty()
    # Use provided placeholder or create a temporary one
    disp_placeholder = script_placeholder if script_placeholder else st.empty()
    status_placeholder = st.empty()
    
    full_script = ""
    final_model_used = ""
    
    try:
        if use_templates:
            status_placeholder.info(f"🚀 Starting AI script generation with {len(template_ids)} template(s)...")
        else:
            status_placeholder.info("🚀 Starting AI script generation...")
        
        async for event in client.generate_script_stream(
            knowledge_id=knowledge_id,
            model_name=model,
            custom_prompt=custom_prompt,
            template_ids=template_ids,
            quick_instructions=quick_instructions,
            system_prompt_override=system_prompt_override,
            preferred_languages=preferred_languages,
            speaker1_languages=speaker1_languages,
            speaker2_languages=speaker2_languages,
            target_duration_minutes=st.session_state.target_duration_minutes if use_templates else None,
            is_multi_speaker=multi_speaker
        ):
            event_type = event.get("type")
            
            if event_type == "token":
                # Append token and update display
                full_script += event.get("content", "")
                
                # Use st.code for streaming - it doesn't require keys and works
                # perfectly with st.empty() placeholders for dynamic updates
                disp_placeholder.code(full_script, language=None, wrap_lines=True)
                status_placeholder.caption(f"⏳ Generating... ({len(full_script):,} characters)")
                
            elif event_type == "complete":
                # Generation complete
                final_script = event.get("script", full_script)
                final_model_used = event.get("model_used", model)
                
                st.session_state.generated_script = final_script
                st.session_state.is_generating = False
                
                # Clear streaming placeholders
                progress_placeholder.empty()
                if not script_placeholder:
                    # If we own the placeholder, clear it so the editor can take its place visually
                    disp_placeholder.empty()
                status_placeholder.empty()
                
                st.toast(f"✅ Script generated using {final_model_used}!", icon="📝")
                # Removed st.rerun() to prevent UI blink. The flow will continue in render_script_editor to show the editor.
                
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
                    add_error_to_log(f"Script generation failed: {error_msg}")
                st.session_state.is_generating = False
                st.rerun()
                return
                
    except Exception as e:
        # Clean up placeholders on error
        progress_placeholder.empty()
        if not script_placeholder:
            disp_placeholder.empty()
        status_placeholder.empty()
        st.session_state.is_generating = False
        
        error_msg = str(e) if str(e) else repr(e)
        add_error_to_log(f"Script generation failed: {error_msg}")
        st.rerun()


async def generate_audio(knowledge_id: str, script: str, voice_id: str):
    """Generate audio from script."""
    try:
        with st.spinner("Synthesizing audio with ElevenLabs..."):
            await client.generate_audio(knowledge_id, script, voice_id)
            st.toast("Audio generated successfully!", icon="✅")
            # Invalidate audio history cache so it refreshes on next render
            st.session_state["_audio_history_cache_id"] = None
    except Exception as e:
        add_error_to_log(f"Audio generation failed. Please check your quota or try again. (Error: {e})")


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


@st.dialog("Prompt Preview")
def render_preview_dialog(preview_text: str):
    """Render dialog to preview combined prompt."""
    st.markdown("This is the exact prompt that will be sent to the AI:")
    st.text_area("Full Prompt", value=preview_text, height=400, disabled=True)
    st.caption(f"Total characters: {len(preview_text)}")


@st.dialog("Edit System Prompt")
def render_system_prompt_editor():
    """Render dialog to edit the base system prompt."""
    st.markdown("Edit the foundational prompt that is inserted at the beginning of all script generation.")
    
    # helper for fetching system prompt synchronously
    def get_default_prompt():
        try:
            return run_async(client.get_base_system_prompt())
        except Exception as e:
            add_error_to_log(f"Failed to load base system prompt: {e}")
            return "Error loading system prompt."

    # Cache the default prompt in session state to avoid re-fetching on every rerun
    if "base_system_prompt_cached" not in st.session_state:
        st.session_state.base_system_prompt_cached = get_default_prompt()
    
    default_system_prompt = st.session_state.base_system_prompt_cached
    
    # Use fragment to allow partial rerun without closing dialog
    @st.fragment
    def system_prompt_editor_fragment():
        # Check for pending reset BEFORE widget renders
        if st.session_state.get("_reset_system_prompt_pending"):
            st.session_state["_reset_system_prompt_pending"] = False
            # Refresh default in case it changed on backend
            fresh_default = get_default_prompt()
            st.session_state.base_system_prompt_cached = fresh_default
            st.session_state["system_prompt_textarea"] = fresh_default
            st.session_state.custom_system_prompt = None
            default_system_prompt = fresh_default # Update local variable
        else:
            default_system_prompt = st.session_state.base_system_prompt_cached
        
        current_prompt = st.session_state.custom_system_prompt or default_system_prompt
        
        new_prompt = st.text_area(
            "System Prompt Content",
            value=current_prompt,
            height=350,
            key="system_prompt_textarea"
        )
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            if st.button("Save", type="primary", use_container_width=True):
                st.session_state.custom_system_prompt = new_prompt
                st.toast("System prompt saved!", icon="✅")
                st.rerun()  # Full rerun to close dialog
        with fc2:
            if st.button("Reset to Default", use_container_width=True):
                st.session_state["_reset_system_prompt_pending"] = True
                st.toast("Reset to default!", icon="🔄")
                st.rerun(scope="fragment")  # Fragment rerun - stays in dialog
        with fc3:
            if st.button("Cancel", use_container_width=True):
                st.rerun()  # Full rerun to close dialog
    
    system_prompt_editor_fragment()


@st.dialog("Manage Custom Templates")
def render_template_manager():
    """Render dialog for managing custom templates."""
    st.markdown("Create new templates or manage existing ones.")
    
    # Create new template form
    with st.expander("➕ Create New Template", expanded=False):
        with st.form("create_template_form"):
            display_name = st.text_input("Template Name", placeholder="e.g., Pediatric Intro")
            description = st.text_input("Description", placeholder="For explaining procedures to children")
            content = st.text_area("Template Content", placeholder="Write your prompt logic here...")
            
            if st.form_submit_button("Create Template", type="primary"):
                if not display_name or not content:
                    add_error_to_log("Name and Content are required.")
                else:
                    new_template = CustomTemplateCreate(
                        display_name=display_name,
                        description=description,
                        content=content
                    )
                    # Queue operation for async execution outside dialog
                    st.session_state._pending_template_op = {
                        "action": "create",
                        "template": new_template
                    }
                    st.rerun()

    st.divider()
    
    # List existing custom templates
    st.subheader("Your Custom Templates")
    
    # Ensure available templates are loaded
    templates = st.session_state.get("available_templates", [])
    custom_templates = [t for t in templates if t.category == "custom"]
    
    if not custom_templates:
        st.info("No custom templates found.")
    else:
        for tmpl in custom_templates:
            edit_key = f"editing_{tmpl.template_id}"
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{tmpl.display_name}**")
                    st.caption(tmpl.description)
                with c2:
                    if st.button("Edit", key=f"edit_{tmpl.template_id}", use_container_width=True):
                        # Toggle edit mode and load content
                        if not st.session_state.get(edit_key):
                            st.session_state[edit_key] = True
                            # Fetch content when entering edit mode (use run_async helper)
                            try:
                                content = run_async(client.get_template_content(tmpl.template_id))
                                st.session_state[f"content_{tmpl.template_id}"] = content
                            except Exception:
                                st.session_state[f"content_{tmpl.template_id}"] = tmpl.preview
                        else:
                            st.session_state[edit_key] = False
                with c3:
                    if st.button("Delete", key=f"del_{tmpl.template_id}", type="secondary", use_container_width=True):
                        # Queue delete operation for async execution
                        st.session_state._pending_template_op = {
                            "action": "delete",
                            "template_id": tmpl.template_id
                        }
                        st.rerun()
                
                # Show edit form when Edit is clicked
                if st.session_state.get(edit_key):
                    with st.form(f"edit_form_{tmpl.template_id}"):
                        edit_name = st.text_input("Template Name", value=tmpl.display_name)
                        edit_desc = st.text_input("Description", value=tmpl.description)
                        edit_content = st.text_area(
                            "Content", 
                            value=st.session_state.get(f"content_{tmpl.template_id}", tmpl.preview),
                            height=200
                        )
                        
                        fc1, fc2 = st.columns(2)
                        with fc1:
                            if st.form_submit_button("Save Changes", type="primary"):
                                # Queue update operation for async execution
                                st.session_state._pending_template_op = {
                                    "action": "update",
                                    "template_id": tmpl.template_id,
                                    "display_name": edit_name,
                                    "description": edit_desc,
                                    "content": edit_content
                                }
                                st.session_state[edit_key] = False
                                st.rerun()
                        with fc2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[edit_key] = False


@st.fragment
async def render_script_editor():
    """Render script generation and editing section (isolated fragment)."""
    st.subheader("2. Script Editor")
    
    if not st.session_state.selected_document:
        st.info("Please select a document specifically to proceed.")
        return

    # Load available templates if not loaded
    if not st.session_state.available_templates:
        try:
            st.session_state.available_templates = await client.get_templates()
        except Exception as e:
            st.warning(f"Could not load templates: {e}")
            st.session_state.available_templates = []

    col1, col2 = st.columns([1, 3])
    
    with col1:
        # AI Model selection
        st.session_state.selected_llm_model = st.selectbox(
            "AI Model",
            options=["gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-3-pro-preview"],
            index=0,
            help="Select the AI model for script generation"
        )
        
        # Speech duration selection (based on ~150 words per minute)
        DURATION_OPTIONS = {
            3: "3 min (~400–500 words)",
            5: "5 min (~650–850 words)",
            10: "10 min (~1,300–1,700 words)",
            15: "15 min (~2,000–2,500 words)",
        }
        st.session_state.target_duration_minutes = st.selectbox(
            "🕐 Speech Duration",
            options=list(DURATION_OPTIONS.keys()),
            format_func=lambda x: DURATION_OPTIONS[x],
            index=list(DURATION_OPTIONS.keys()).index(st.session_state.target_duration_minutes),
            help="Target length of the generated audio"
        )
        
        st.divider()
        
        # Multi-speaker toggle and language selection
        st.session_state.multi_speaker_enabled = st.toggle(
            "🎭 Multi-Speaker Dialogue",
            value=st.session_state.multi_speaker_enabled,
            help="Enable dialogue between Doctor/Educator and Patient/Learner"
        )
        
        st.caption("💡 Speaker 1 is the Doctor/Educator/Guider voice")
        
        # All ElevenLabs supported languages with native script + English
        # Chinese and Portuguese have regional variants for correct character/spelling output
        LANGUAGE_OPTIONS = [
            "ar", "bg", "cs", "da", "de", "el", "en", "es", "fi", "fil",
            "fr", "hi", "hr", "hu", "id", "it", "ja", "ko", "ms", "nl",
            "no", "pl", "pt-BR", "pt-PT", "ro", "ru", "sk", "sv", "ta", "tr", "uk", "zh-TW", "zh-CN"
        ]
        LANGUAGE_DISPLAY = {
            "ar": "العربية (Arabic)",
            "bg": "Български (Bulgarian)",
            "cs": "Čeština (Czech)",
            "da": "Dansk (Danish)",
            "de": "Deutsch (German)",
            "el": "Ελληνικά (Greek)",
            "en": "English",
            "es": "Español (Spanish)",
            "fi": "Suomi (Finnish)",
            "fil": "Filipino",
            "fr": "Français (French)",
            "hi": "हिन्दी (Hindi)",
            "hr": "Hrvatski (Croatian)",
            "hu": "Magyar (Hungarian)",
            "id": "Bahasa Indonesia (Indonesian)",
            "it": "Italiano (Italian)",
            "ja": "日本語 (Japanese)",
            "ko": "한국어 (Korean)",
            "ms": "Bahasa Melayu (Malay)",
            "nl": "Nederlands (Dutch)",
            "no": "Norsk (Norwegian)",
            "pl": "Polski (Polish)",
            "pt-BR": "Português Brasileiro (Brazilian Portuguese)",
            "pt-PT": "Português Europeu (European Portuguese)",
            "ro": "Română (Romanian)",
            "ru": "Русский (Russian)",
            "sk": "Slovenčina (Slovak)",
            "sv": "Svenska (Swedish)",
            "ta": "தமிழ் (Tamil)",
            "tr": "Türkçe (Turkish)",
            "uk": "Українська (Ukrainian)",
            "zh-TW": "繁體中文 (Traditional Chinese)",
            "zh-CN": "簡體中文 (Simplified Chinese)"
        }
        
        st.session_state.speaker1_languages = st.multiselect(
            "Speaker 1 Languages",
            options=LANGUAGE_OPTIONS,
            default=st.session_state.speaker1_languages,
            format_func=lambda x: LANGUAGE_DISPLAY.get(x, x),
            help="Languages for the Doctor/Educator speaker"
        )
        
        # Speaker 2 is grayed out when multi-speaker is disabled
        speaker2_disabled = not st.session_state.multi_speaker_enabled
        
        # Clear Speaker 2 languages when multi-speaker is disabled
        if speaker2_disabled:
            speaker2_default = []
        else:
            speaker2_default = st.session_state.speaker2_languages
        
        st.session_state.speaker2_languages = st.multiselect(
            "Speaker 2 Languages",
            options=LANGUAGE_OPTIONS,
            default=speaker2_default,
            format_func=lambda x: LANGUAGE_DISPLAY.get(x, x),
            help="Languages for the Patient/Learner speaker" if not speaker2_disabled else "Enable Multi-Speaker Dialogue to use Speaker 2",
            disabled=speaker2_disabled
        )
        
        st.divider()

        # Manage Templates Button
        if st.button("🛠️ Manage Templates", use_container_width=True):
            render_template_manager()
            
        st.divider()
        
        # Mode toggle: Template vs Custom
        st.session_state.use_template_mode = st.toggle(
            "Use Template Mode",
            value=st.session_state.use_template_mode,
            help="Enable template-based prompt building"
        )
        
        if st.session_state.use_template_mode:
            # Template selection
            if st.session_state.available_templates:
                template_options = {t.template_id: t for t in st.session_state.available_templates}
                
                selected = st.multiselect(
                    "📋 Content Modules",
                    options=list(template_options.keys()),
                    default=st.session_state.selected_templates,
                    format_func=lambda x: template_options[x].display_name if x in template_options else x,
                    help="Select content types to include in the prompt"
                )
                
                # Check for streamlit-sortables availability (it should be installed now)
                try:
                    from streamlit_sortables import sort_items
                    
                    if selected and len(selected) > 0:
                        st.caption("Drag to reorder content modules:")
                        selected_names = [template_options[t].display_name if t in template_options else t for t in selected]
                        
                        # Dynamic key ensures component re-initializes when selection changes
                        sorter_key = f"template_sorter_{len(selected)}_{hash(tuple(selected))}"
                        
                        ordered_names = sort_items(
                            selected_names,
                            direction="vertical",
                            key=sorter_key
                        )
                        
                        # Map back to IDs (careful with duplicate display names if any, but template names should be unique)
                        # We use a reverse lookup mapping
                        name_to_id = {template_options[t].display_name: t for t in selected if t in template_options}
                        
                        # Reconstruct selected_templates based on sorted order
                        # ordered_names comes from UI, map back to IDs
                        st.session_state.selected_templates = [name_to_id[n] for n in ordered_names if n in name_to_id]
                    else:
                        st.session_state.selected_templates = selected if selected else ["pre_surgery"]
                except ImportError:
                    st.warning("streamlit-sortables not installed. Reordering disabled.")
                    st.session_state.selected_templates = selected if selected else ["pre_surgery"]
                
                # Show template descriptions
                if selected:
                    with st.expander("📖 Template Details", expanded=False):
                        for tid in selected:
                            if tid in template_options:
                                t = template_options[tid]
                                st.markdown(f"**{t.display_name}**")
                                st.caption(t.description)
            
            st.divider()
            
            # Quick instructions
            st.session_state.quick_instructions = st.text_area(
                "💬 Additional Instructions",
                value=st.session_state.quick_instructions,
                placeholder="e.g., Focus on elderly patients, use simple language...",
                height=100,
                help="Add extra instructions without modifying templates"
            )
            
            if st.button("👁️ Preview Combined Prompt", use_container_width=True):
                try:
                    preview_text = await client.preview_combined_prompt(
                        st.session_state.selected_templates,
                        st.session_state.quick_instructions
                    )
                    render_preview_dialog(preview_text)
                except Exception as e:
                    add_error_to_log(f"Preview failed: {e}")
            
            # System prompt editor button
            if st.button("⚙️ Edit System Prompt", use_container_width=True):
                render_system_prompt_editor()
            if st.session_state.custom_system_prompt:
                st.caption("✓ Using custom system prompt")
        else:
            # Custom prompt mode (legacy)
            if st.button("⚙️ Customize Prompt", use_container_width=True):
                render_prompt_editor_dialog()
            
            if st.session_state.custom_prompt:
                st.caption("✓ Using custom prompt")
            
        st.divider()

        # Capture the second column container for streaming
        editor_placeholder = None

        if st.button("✨ Generate Script", key="generate_script_btn", type="primary", use_container_width=True):
            # The actual call will happen after we define the placeholder in col2
            st.session_state._trigger_generation = True

    with col2:
        # Streaming placeholder (only visible during generation)
        streaming_area = st.empty()
        
        if st.session_state.get("_trigger_generation"):
            st.session_state._trigger_generation = False
            await generate_script(
                st.session_state.selected_document.knowledge_id,
                script_placeholder=streaming_area
            )
        
        # Edit area (only visible when not generating)
        if st.session_state.is_generating:
            # Streaming is handled by generate_script via streaming_area
            pass
        else:
            streaming_area.empty()  # Clear any leftover streaming content
            st.markdown("**Review and Edit Script:**")
            # Use dynamic key based on generation_id to force widget refresh
            editor_key = f"script_editor_area_{st.session_state.generation_id}"
            edited_script = st.text_area(
                "Script Content",
                value=st.session_state.generated_script,
                height=600,
                label_visibility="collapsed",
                key=editor_key
            )
            st.session_state.generated_script = edited_script
            st.caption(f"Character count: {len(edited_script)}")


@st.fragment
async def render_audio_generation():
    """Render voice selection with dynamic language filtering (isolated fragment)."""
    st.subheader("3. Voice & Generation")

    if not st.session_state.generated_script:
        st.info("Generate or write a script to proceed.")
        return

    # Load voices if not loaded
    if not st.session_state.voices:
        st.session_state.voices = get_voices_cached()

    if not st.session_state.voices:
        st.warning("No voices available. Check API connection.")
        return

    # Helper function to filter voices by languages
    def filter_voices_by_languages(voices, lang_codes):
        if not lang_codes:
            return voices
        
        # Map UI language codes to voice language codes
        # Most codes match directly (en, ja, ko, fr, etc.)
        # Chinese variants (zh-TW, zh-CN) map to zh
        # Portuguese variants (pt-BR, pt-PT) map to pt
        lang_map = {"zh-TW": "zh", "zh-CN": "zh", "pt-BR": "pt", "pt-PT": "pt"}
        required_langs = {lang_map.get(lang, lang) for lang in lang_codes}
        
        filtered = [
            v for v in voices
            if hasattr(v, 'languages') and all(lang in getattr(v, 'languages', []) for lang in required_langs)
        ]
        
        return filtered if filtered else voices
    
    # Helper function to build voice options dict
    def build_voice_options(voices):
        options = {}
        for v in voices:
            lang_count = len(getattr(v, 'languages', [])) if hasattr(v, 'languages') else 0
            display_name = f"{v.name} ({lang_count} langs)" if lang_count > 0 else v.name
            options[display_name] = v
        return options

    # Check if multi-speaker mode is active
    speaker1_langs = st.session_state.get("speaker1_languages", [])
    speaker2_langs = st.session_state.get("speaker2_languages", [])
    is_multi_speaker = bool(speaker1_langs and speaker2_langs)
    
    if is_multi_speaker:
        st.caption("🎭 **Multi-Speaker Mode Active** - Select voices for each speaker")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Speaker 1** (Doctor/Educator)")
            speaker1_voices = filter_voices_by_languages(st.session_state.voices, speaker1_langs)
            speaker1_options = build_voice_options(speaker1_voices)
            
            if speaker1_options:
                speaker1_voice_name = st.selectbox(
                    "Speaker 1 Voice",
                    options=list(speaker1_options.keys()),
                    help=f"Showing {len(speaker1_voices)} voices supporting: {', '.join(speaker1_langs)}"
                )
                speaker1_voice = speaker1_options[speaker1_voice_name]
                st.session_state.speaker1_voice_id = speaker1_voice.voice_id
                
                if speaker1_voice.preview_url:
                    st.audio(speaker1_voice.preview_url, format="audio/mpeg")
            else:
                st.warning("No voices found for Speaker 1 languages")
        
        with col2:
            st.markdown("**Speaker 2** (Patient/Learner)")
            speaker2_voices = filter_voices_by_languages(st.session_state.voices, speaker2_langs)
            speaker2_options = build_voice_options(speaker2_voices)
            
            if speaker2_options:
                speaker2_voice_name = st.selectbox(
                    "Speaker 2 Voice",
                    options=list(speaker2_options.keys()),
                    help=f"Showing {len(speaker2_voices)} voices supporting: {', '.join(speaker2_langs)}"
                )
                speaker2_voice = speaker2_options[speaker2_voice_name]
                st.session_state.speaker2_voice_id = speaker2_voice.voice_id
                
                if speaker2_voice.preview_url:
                    st.audio(speaker2_voice.preview_url, format="audio/mpeg")
            else:
                st.warning("No voices found for Speaker 2 languages")
        
        # Use speaker1 voice for now (multi-speaker TTS would need separate API)
        st.session_state.selected_voice_id = st.session_state.speaker1_voice_id
        st.info("💡 Multi-speaker audio will be generated. ElevenLabs V3 uses voice assignments from your script formatting.")
    
    else:
        # Single speaker mode - use preferred_languages or show all
        selected_langs = st.session_state.get("preferred_languages", [])
        filtered_voices = filter_voices_by_languages(st.session_state.voices, selected_langs)
        voice_options = build_voice_options(filtered_voices)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            selected_voice_name = st.selectbox(
                "Select Voice",
                options=list(voice_options.keys()),
                help=f"Showing {len(filtered_voices)} voices" + (f" supporting: {', '.join(selected_langs)}" if selected_langs else "")
            )
            
        selected_voice = voice_options[selected_voice_name]
        st.session_state.selected_voice_id = selected_voice.voice_id
        
        with col2:
            if hasattr(selected_voice, 'languages') and selected_voice.languages:
                st.caption(f"Supports: {', '.join(selected_voice.languages[:10])}{'...' if len(selected_voice.languages) > 10 else ''}")
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


@st.fragment
async def render_audio_history():
    """Render audio history for the selected document (isolated fragment)."""
    if not st.session_state.selected_document:
        return

    st.subheader("Audio History")

    knowledge_id = st.session_state.selected_document.knowledge_id
    cache_key = "_audio_history_cache"
    cache_id_key = "_audio_history_cache_id"

    # Refresh button inside fragment
    if st.button("🔄 Refresh Audio List", key="refresh_audio_history"):
        st.session_state[cache_id_key] = None

    # Check cache validity
    if st.session_state.get(cache_id_key) != knowledge_id:
        # Cache miss or stale, fetch fresh data
        try:
            audio_files = await client.get_audio_files(knowledge_id)
            st.session_state[cache_key] = audio_files
            st.session_state[cache_id_key] = knowledge_id
        except Exception as e:
            add_error_to_log(f"Unable to load audio history. (Error: {e})")
            return
    else:
        audio_files = st.session_state.get(cache_key, [])

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


async def main():
    """Main page execution."""
    render_header()
    
    documents = get_documents_cached()
    
    await render_document_selection(documents)
    await render_script_editor()
    await render_audio_generation()
    st.divider()
    await render_audio_history()
    render_error_console()
    render_footer()


if __name__ == "__main__":
    asyncio.run(main())
