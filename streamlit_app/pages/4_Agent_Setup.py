import asyncio
import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.exceptions import APIError, APIConnectionError
from backend.models.schemas import AnswerStyle
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer
from streamlit_app.components.error_console import add_error_to_log, render_error_console
from backend.config import get_settings

# Page config
st.set_page_config(
    page_title="🤖",
    layout="wide",
)

render_sidebar()

st.title("🎙️ Voice Agents Setup")
st.markdown("Configure your AI assistants with medical knowledge bases and voice personalities.")

# Initialize session state for loading
if "loading" not in st.session_state:
    st.session_state.loading = False

# Initialize session state for custom system prompts
if "custom_agent_system_prompt" not in st.session_state:
    st.session_state.custom_agent_system_prompt = {}  # {style: custom_prompt}
if "cached_agent_system_prompts" not in st.session_state:
    st.session_state.cached_agent_system_prompts = None

# Initialize session state for form inputs (persist across tab switches)
if "agent_name" not in st.session_state:
    st.session_state.agent_name = ""
if "agent_selected_voice_id" not in st.session_state:
    st.session_state.agent_selected_voice_id = None
if "agent_selected_style" not in st.session_state:
    st.session_state.agent_selected_style = AnswerStyle.PROFESSIONAL.value
if "agent_selected_doc_ids" not in st.session_state:
    st.session_state.agent_selected_doc_ids = []
if "agent_selected_languages" not in st.session_state:
    st.session_state.agent_selected_languages = ["en"]

# Initialize client
client = get_backend_client()


# Cached data fetching functions
@st.cache_data(ttl=30)
def get_cached_documents():
    """Fetch documents with caching (30s TTL)."""
    return asyncio.run(client.get_knowledge_documents())


@st.cache_resource(ttl=300)
def get_cached_voices():
    """Fetch voices with caching (5 min TTL)."""
    return asyncio.run(client.get_available_voices())


@st.cache_data(ttl=30)
def get_cached_agents():
    """Fetch agents with caching (30s TTL)."""
    return asyncio.run(client.get_agents())


def run_async(coroutine):
    """Helper to run async coroutines."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()


# --- Fragment-wrapped Tab Functions ---


@st.fragment
def render_identity_tab(docs, STYLE_OPTIONS):
    """Render the Identity tab content with fragment isolation."""
    with st.container(height=500):
        st.markdown("**👤 Agent Information**")

        # Agent Name with callback
        def update_agent_name():
            st.session_state.agent_name = st.session_state._agent_name_input

        st.text_input(
            "Agent Name",
            value=st.session_state.agent_name,
            placeholder="e.g., Diabetes Specialist",
            key="_agent_name_input",
            on_change=update_agent_name,
        )

        # Document selection with callback
        if docs:
            doc_options = {
                doc.knowledge_id: f"{doc.disease_name} ({', '.join(doc.tags)})"
                for doc in docs
            }

            def update_selected_docs():
                st.session_state.agent_selected_doc_ids = (
                    st.session_state._agent_docs_select
                )

            st.multiselect(
                "Link Knowledge Documents",
                options=list(doc_options.keys()),
                default=[
                    d
                    for d in st.session_state.agent_selected_doc_ids
                    if d in doc_options
                ],
                format_func=lambda x: doc_options[x],
                key="_agent_docs_select",
                on_change=update_selected_docs,
            )

            if st.session_state.agent_selected_doc_ids:
                st.caption(
                    f"📚 {len(st.session_state.agent_selected_doc_ids)} document(s) selected"
                )
        else:
            st.info("No knowledge documents available. Please upload some first.")


@st.fragment
def render_voice_tab(voice_map, LANGUAGE_OPTIONS):
    """Render the Voice tab content with fragment isolation."""
    with st.container(height=500):
        st.markdown("**🎙️ Voice and Language**")

        if voice_map:

            def update_selected_voice():
                st.session_state.agent_selected_voice_id = (
                    st.session_state._agent_voice_select
                )

            st.selectbox(
                "Select Voice",
                options=list(voice_map.keys()),
                format_func=lambda x: voice_map[x].name if x in voice_map else x,
                index=(
                    list(voice_map.keys()).index(
                        st.session_state.agent_selected_voice_id
                    )
                    if st.session_state.agent_selected_voice_id in voice_map
                    else 0
                ),
                key="_agent_voice_select",
                on_change=update_selected_voice,
            )

            # Dynamic voice preview
            selected_voice_id = st.session_state.agent_selected_voice_id
            if selected_voice_id and selected_voice_id in voice_map:
                voice = voice_map[selected_voice_id]
                st.caption(voice.description or "Voice preview")
                if voice.preview_url:
                    st.audio(voice.preview_url, format="audio/mpeg")
        else:
            st.warning("No voices available. Please check your ElevenLabs connection.")

        # Language Selection
        def update_selected_languages():
            st.session_state.agent_selected_languages = (
                st.session_state._agent_languages_select
            )

        st.multiselect(
            "Select Conversation Languages",
            options=list(LANGUAGE_OPTIONS.keys()),
            default=st.session_state.agent_selected_languages,
            format_func=lambda x: LANGUAGE_OPTIONS[x],
            help="First language is primary. Multiple languages enable auto-detection.",
            key="_agent_languages_select",
            on_change=update_selected_languages,
        )


@st.fragment
def render_prompt_tab(client, STYLE_OPTIONS):
    """Render the Prompt tab content with fragment isolation."""
    with st.container(height=500):
        st.markdown("**🧠 Prompt Configuration**")

        # Answer Style selector - updates session state, dynamic key handles text area refresh
        def update_style_from_prompt():
            st.session_state.agent_selected_style = st.session_state._prompt_style_select

        st.selectbox(
            "Answer Style",
            options=list(STYLE_OPTIONS.keys()),
            format_func=lambda x: STYLE_OPTIONS[x],
            index=list(STYLE_OPTIONS.keys()).index(
                st.session_state.agent_selected_style
            ),
            key="_prompt_style_select",
            on_change=update_style_from_prompt,
        )

        # Fetch default prompts if not cached
        if st.session_state.cached_agent_system_prompts is None:
            try:
                st.session_state.cached_agent_system_prompts = run_async(
                    client.get_agent_system_prompts()
                )
            except Exception as e:
                add_error_to_log(f"Failed to load system prompts: {e}")
                st.session_state.cached_agent_system_prompts = {}

        current_style = st.session_state.agent_selected_style
        default_prompt = st.session_state.cached_agent_system_prompts.get(
            current_style, ""
        )
        current_prompt = st.session_state.custom_agent_system_prompt.get(
            current_style, default_prompt
        )

        # System prompt text area with callback
        def update_system_prompt():
            new_val = st.session_state._inline_system_prompt
            current = st.session_state.agent_selected_style
            default = st.session_state.cached_agent_system_prompts.get(current, "")
            if new_val != default:
                st.session_state.custom_agent_system_prompt[current] = new_val
            elif current in st.session_state.custom_agent_system_prompt:
                del st.session_state.custom_agent_system_prompt[current]

        st.text_area(
            "System Prompt",
            value=current_prompt,
            height=250,
            key=f"_inline_system_prompt_{current_style}",
            help="Edit the system prompt for this answer style",
            on_change=update_system_prompt,
        )

        # Reset to Default button
        if st.button(
            "🔄 Reset to Default", key="reset_prompt_btn", help="Reset to default prompt"
        ):
            if current_style in st.session_state.custom_agent_system_prompt:
                del st.session_state.custom_agent_system_prompt[current_style]
            st.rerun()


@st.dialog("✏️ Edit Agent")
def render_edit_agent_dialog(agent, docs, client, LANGUAGE_OPTIONS):
    """Render dialog to edit an existing agent."""
    st.caption(f"Editing Agent: {agent.name}")
    
    # helper for doc names
    doc_options = {
        d.knowledge_id: f"{d.disease_name} ({', '.join(d.tags)})"
        for d in docs
    } if docs else {}

    # Initialize state with current values if not set
    # Using form-specific keys to avoid conflicts
    name_key = f"edit_name_{agent.agent_id}"
    docs_key = f"edit_docs_{agent.agent_id}"

    # 1. Edit Name
    new_name = st.text_input("Agent Name", value=agent.name, key=name_key)
    
    # 2. Languages - Display Only (ElevenLabs API limitation)
    current_langs = agent.languages if hasattr(agent, "languages") else ["en"]
    valid_current_langs = [l for l in current_langs if l in LANGUAGE_OPTIONS]
    lang_display = ", ".join([LANGUAGE_OPTIONS.get(l, l) for l in valid_current_langs])
    
    st.text_input(
        "Conversation Languages",
        value=lang_display,
        disabled=True,
        help="Languages cannot be modified after agent creation due to ElevenLabs API limitations."
    )
    st.caption("⚠️ **Note:** To change languages, delete this agent and create a new one.")

    # 3. Edit Knowledge
    current_docs = [d for d in agent.knowledge_ids if d in doc_options]
    
    new_doc_ids = st.multiselect(
        "Linked Knowledge Documents",
        options=list(doc_options.keys()),
        default=current_docs,
        format_func=lambda x: doc_options[x],
        key=docs_key
    )

    st.warning("Note: Changing settings will update the agent in ElevenLabs, affecting any active sessions.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes", type="primary", use_container_width=True, key=f"save_{agent.agent_id}"):
            if not new_name.strip():
                st.error("Name cannot be empty.")
            else:
                try:
                    with st.spinner("Updating agent..."):
                        run_async(client.update_agent(
                            agent_id=agent.agent_id,
                            name=new_name,
                            knowledge_ids=new_doc_ids
                            # languages removed - not updateable via ElevenLabs API
                        ))
                    st.success("Agent updated successfully!")
                    get_cached_agents.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {str(e)}")
    
    with col2:
        if st.button("Cancel", use_container_width=True, key=f"cancel_{agent.agent_id}"):
            st.rerun()
@st.fragment
def render_existing_agents(agents, docs, client):
    """Render existing agents section with fragment isolation."""
    LANGUAGE_DISPLAY = {
        "en": "English",
        "zh": "中文 (Traditional Chinese)",
        "es": "Español (Spanish)",
        "fr": "Français (French)",
        "de": "Deutsch (German)",
        "ja": "日本語 (Japanese)",
        "ko": "한국어 (Korean)",
    }
    
    # We need access to LANGUAGE_OPTIONS for the dialog
    # It's defined globally in the script but passed to other functions
    # Let's recreate it here or pass it in. For simplicity, reusing the display map which matches keys.


    with st.container(border=True):
        if not agents:
            st.info("No agents created yet.")
        else:
            for agent in agents:
                with st.expander(f"🤖 {agent.name}", expanded=False):
                    st.write(f"**Description:** {agent.answer_style.title()} style")
                    langs = (
                        agent.languages
                        if hasattr(agent, "languages") and agent.languages
                        else ["en"]
                    )
                    lang_names = [LANGUAGE_DISPLAY.get(lang, lang) for lang in langs]
                    st.write(f"**Languages:** {', '.join(lang_names)}")
                    st.caption(f"ID: {agent.agent_id}")
                    st.caption(f"Created: {agent.created_at.strftime('%Y-%m-%d %H:%M')}")

                    linked_docs = [
                        d for d in docs if d.knowledge_id in agent.knowledge_ids
                    ]
                    if linked_docs:
                        st.markdown("**Linked Knowledge:**")
                        for d in linked_docs:
                            st.text(f"• {d.disease_name}")
                    else:
                        st.text("No linked knowledge.")



                    c1, c2, c3 = st.columns([1, 1, 3])
                    with c1:
                        if st.button("✏️ Edit", key=f"edit_btn_{agent.agent_id}"):
                            render_edit_agent_dialog(agent, docs, client, LANGUAGE_DISPLAY)
                    
                    with c2:
                         if st.button("🔄 Sync", key=f"sync_btn_{agent.agent_id}", help="Fetch configuration from ElevenLabs"):
                            try:
                                with st.spinner("Syncing from ElevenLabs..."):
                                    run_async(client.sync_agent(agent.agent_id))
                                st.success("Synced!")
                                get_cached_agents.clear()
                                st.rerun()
                            except Exception as e:
                                add_error_to_log(f"Sync failed: {str(e)}")
                    
                    with c3:
                        # Delete button (disabled in demo mode)
                        is_demo = get_settings().demo_mode
                        if st.button(
                            "🗑️ Delete",
                            key=f"del_{agent.agent_id}",
                            disabled=is_demo,
                            help="Delete is disabled in demo mode" if is_demo else None
                        ):
                            try:
                                with st.spinner("Deleting agent..."):
                                    run_async(client.delete_agent(agent.agent_id))
                                st.success("Agent deleted.")
                                get_cached_agents.clear()
                                st.rerun()
                            except Exception as e:
                                add_error_to_log(f"Delete failed: {str(e)}")


@st.dialog("Edit System Prompt")
def render_agent_system_prompt_editor(style: str):
    """Render dialog to edit system prompt for the selected answer style."""
    style_display = {
        "professional": "Professional",
        "friendly": "Friendly",
        "educational": "Educational"
    }
    st.markdown(f"Edit the system prompt for **{style_display.get(style, style)}** style.")
    
    # Fetch default prompts if not cached
    def get_default_prompts():
        try:
            return run_async(client.get_agent_system_prompts())
        except Exception as e:
            add_error_to_log(f"Failed to load system prompts: {e}")
            return {}
    
    if st.session_state.cached_agent_system_prompts is None:
        st.session_state.cached_agent_system_prompts = get_default_prompts()
    
    default_prompts = st.session_state.cached_agent_system_prompts
    default_prompt = default_prompts.get(style, "")
    
    # Use fragment for partial rerun without closing dialog
    @st.fragment
    def system_prompt_editor_fragment():
        # Check for pending reset
        reset_key = f"_reset_agent_system_prompt_{style}"
        if st.session_state.get(reset_key):
            st.session_state[reset_key] = False
            # Remove custom prompt for this style
            if style in st.session_state.custom_agent_system_prompt:
                del st.session_state.custom_agent_system_prompt[style]
            st.session_state[f"agent_system_prompt_textarea_{style}"] = default_prompt
            st.toast("Reset to default!", icon="🔄")
        
        # Get current prompt (custom if exists, else default)
        current_prompt = st.session_state.custom_agent_system_prompt.get(style, default_prompt)
        
        new_prompt = st.text_area(
            "System Prompt Content",
            value=current_prompt,
            height=400,
            key=f"agent_system_prompt_textarea_{style}"
        )
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            if st.button("Save", type="primary", use_container_width=True):
                st.session_state.custom_agent_system_prompt[style] = new_prompt
                st.toast("System prompt saved!", icon="✅")
                st.rerun()  # Full rerun to close dialog
        with fc2:
            if st.button("Reset to Default", use_container_width=True):
                st.session_state[reset_key] = True
                st.rerun(scope="fragment")  # Fragment rerun - stays in dialog
        with fc3:
            if st.button("Cancel", use_container_width=True):
                st.rerun()  # Full rerun to close dialog
    
    system_prompt_editor_fragment()


# Load data using cached functions
try:
    docs = get_cached_documents()
    voices = get_cached_voices()
    agents = get_cached_agents()
except Exception as e:
    add_error_to_log(f"Failed to load data: {str(e)}")
    docs, voices, agents = [], [], []

# Define style options
STYLE_OPTIONS = {
    AnswerStyle.PROFESSIONAL.value: "Professional (Formal & Objective)",
    AnswerStyle.FRIENDLY.value: "Friendly (Warm & Approachable)",
    AnswerStyle.EDUCATIONAL.value: "Educational (Teaching-focused)",
}

# Language options
LANGUAGE_OPTIONS = {
    "en": "English",
    "zh": "中文 (Traditional Chinese)",
    "es": "Español (Spanish)",
    "fr": "Français (French)",
    "de": "Deutsch (German)",
    "ja": "日本語 (Japanese)",
    "ko": "한국어 (Korean)",
}

# Prepare voice map
voice_map = {v.voice_id: v for v in voices}

# Initialize voice selection if not set
if st.session_state.agent_selected_voice_id is None and voice_map:
    st.session_state.agent_selected_voice_id = list(voice_map.keys())[0]

# --- Create New Agent Section ---
st.header("Create New Agent")

# Create tabs for organized input
identity_tab, voice_tab, prompt_tab = st.tabs([
    "👤 Identity", 
    "🎙️ Voice", 
    "🧠 Prompt"
])

with identity_tab:
    render_identity_tab(docs, STYLE_OPTIONS)

with voice_tab:
    render_voice_tab(voice_map, LANGUAGE_OPTIONS)

with prompt_tab:
    render_prompt_tab(client, STYLE_OPTIONS)


# Create Agent Button (outside tabs)
st.divider()

if st.button("🚀 Create Agent", type="primary", use_container_width=True, key="create_agent_btn"):
    # Validation
    name = st.session_state.agent_name
    selected_voice_id = st.session_state.agent_selected_voice_id
    selected_style = st.session_state.agent_selected_style
    selected_doc_ids = st.session_state.agent_selected_doc_ids
    selected_languages = st.session_state.agent_selected_languages
    
    if not name.strip():
        add_error_to_log("Agent name is required.")
    elif not selected_voice_id:
        add_error_to_log("Voice selection is required.")
    elif not selected_languages:
        add_error_to_log("At least one language is required.")
    else:
        try:
            # Get custom prompt if exists
            custom_prompt = st.session_state.custom_agent_system_prompt.get(selected_style)
            
            with st.spinner("Creating agent in ElevenLabs..."):
                run_async(client.create_agent(
                    name=name,
                    knowledge_ids=selected_doc_ids,
                    voice_id=selected_voice_id,
                    answer_style=selected_style,
                    languages=selected_languages,
                    system_prompt_override=custom_prompt
                ))
            st.success(f"Agent '{name}' created successfully!")
            
            # Clear form state
            st.session_state.agent_name = ""
            st.session_state.agent_selected_doc_ids = []
            
            get_cached_agents.clear()
            st.rerun()
        except APIError as e:
            add_error_to_log(f"Creation failed: {e.message}")
        except Exception as e:
            add_error_to_log(f"Error: {str(e)}")

# --- Existing Agents Section (Outside Tabs) ---
st.header("Existing Agents")
render_existing_agents(agents, docs, client)

render_error_console()
render_footer()
