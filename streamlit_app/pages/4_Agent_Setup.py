import asyncio
import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.exceptions import APIError, APIConnectionError
from backend.models.schemas import AnswerStyle
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer
from streamlit_app.components.error_console import add_error_to_log, render_error_console

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

# Initialize client
client = get_backend_client()


# Cached data fetching functions
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


# Refresh Button
if st.button("🔄 Refresh Data"):
    get_cached_documents.clear()
    get_cached_agents.clear()
    # Voices usually don't need frequent refresh, but we can if needed
    st.rerun()

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

# --- Create New Agent Column ---

st.header("Create New Agent")
with st.form("create_agent_form"):
    name = st.text_input("Agent Name", placeholder="e.g., Diabetes Specialist")
    
    # Knowledge Selection
    st.subheader("Select Knowledge")
    if docs:
        doc_options = {doc.knowledge_id: f"{doc.disease_name} ({', '.join(doc.tags)})" for doc in docs}
        selected_doc_ids = st.multiselect(
            "Link Knowledge Documents",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x]
        )
    else:
        st.info("No knowledge documents available. Please upload some first.")
        selected_doc_ids = []

    # Voice Selection
    st.subheader("Voice Configuration")
    voice_map = {v.voice_id: v for v in voices}
    selected_voice_id = st.selectbox(
        "Select Voice",
        options=list(voice_map.keys()),
        format_func=lambda x: voice_map[x].name if x in voice_map else x
    )
    
    if selected_voice_id and selected_voice_id in voice_map:
        voice = voice_map[selected_voice_id]
        st.caption(voice.description or "No description")
        if voice.preview_url:
            st.audio(voice.preview_url)
    
    # Style Selection
    st.subheader("Answer Style")
    selected_style = st.selectbox(
        "Select Answer Style",
        options=list(STYLE_OPTIONS.keys()),
        format_func=lambda x: STYLE_OPTIONS[x]
    )
    
    # Language Selection
    st.subheader("Conversation Languages")
    LANGUAGE_OPTIONS = {
        "zh": "中文 (Traditional Chinese)",
        "en": "English",
        "es": "Español (Spanish)",
        "fr": "Français (French)",
        "de": "Deutsch (German)",
        "ja": "日本語 (Japanese)",
        "ko": "한국어 (Korean)",
    }
    selected_languages = st.multiselect(
        "Select Conversation Languages",
        options=list(LANGUAGE_OPTIONS.keys()),
        default=["zh"],
        format_func=lambda x: LANGUAGE_OPTIONS[x],
        help="First language is primary. Multiple languages enable auto-detection."
    )
    
    submitted = st.form_submit_button("Create Agent")
    
    if submitted:
        if not name.strip():
            add_error_to_log("Agent name is required.")
        elif not selected_voice_id:
            add_error_to_log("Voice selection is required.")
        elif not selected_languages:
            add_error_to_log("At least one language is required.")
        else:
            client = get_backend_client()
            try:
                with st.spinner("Creating agent in ElevenLabs..."):
                    run_async(client.create_agent(
                        name=name,
                        knowledge_ids=selected_doc_ids,
                        voice_id=selected_voice_id,
                        answer_style=selected_style,
                        languages=selected_languages
                    ))
                st.success(f"Agent '{name}' created successfully!")
                get_cached_agents.clear()
                st.rerun()
            except APIError as e:
                add_error_to_log(f"Creation failed: {e.message}")
            except Exception as e:
                add_error_to_log(f"Error: {str(e)}")


# --- Existing Agents Column ---

st.header("Existing Agents")

with st.container(border=True):
    if not agents:
        st.info("No agents created yet.")
    else:
        for agent in agents:
            # Language display mapping
            LANGUAGE_DISPLAY = {
                "zh": "中文 (Traditional Chinese)",
                "en": "English",
                "es": "Español (Spanish)",
                "fr": "Français (French)",
                "de": "Deutsch (German)",
                "ja": "日本語 (Japanese)",
                "ko": "한국어 (Korean)",
            }
            
            with st.expander(f"🤖 {agent.name}", expanded=False):
                st.write(f"**Description:** {agent.answer_style.title()} style")
                # Handle list of languages
                langs = agent.languages if hasattr(agent, "languages") and agent.languages else ["zh"]
                lang_names = [LANGUAGE_DISPLAY.get(lang, lang) for lang in langs]
                st.write(f"**Languages:** {', '.join(lang_names)}")
                st.caption(f"ID: {agent.agent_id}")
                st.caption(f"Created: {agent.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Knowledge
                linked_docs = [d for d in docs if d.knowledge_id in agent.knowledge_ids]
                if linked_docs:
                    st.markdown("**Linked Knowledge:**")
                    for d in linked_docs:
                        st.text(f"• {d.disease_name}")
                else:
                    st.text("No linked knowledge.")
                
                # Delete Button
                if st.button("Delete", key=f"del_{agent.agent_id}"):
                    client = get_backend_client()
                    try:
                        with st.spinner("Deleting agent..."):
                            run_async(client.delete_agent(agent.agent_id))
                        st.success("Agent deleted.")
                        get_cached_agents.clear()
                        st.rerun()
                    except Exception as e:
                        add_error_to_log(f"Delete failed: {str(e)}")

render_error_console()
render_footer()

