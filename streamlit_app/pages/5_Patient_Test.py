
import streamlit as st
import asyncio
import base64
from datetime import datetime
from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer
from streamlit_app.components.error_console import add_error_to_log, render_error_console
from streamlit_app.services.models import PatientSession, ConversationMessage

# Page Configuration
st.set_page_config(
    page_title="Patient Test",
    page_icon="🏥",
    layout="wide",
)

render_sidebar()

st.title("🧪 Patient Conversation Test")
st.markdown("Simulate patient interactions and test your AI agents in real-time.")

# Initialize client
client = get_backend_client()


# Cached data fetching functions
@st.cache_resource(ttl=30)
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


@st.cache_data(ttl=300)
def get_cached_audio_files(knowledge_ids):
    """Fetch audio files for all knowledge IDs with caching."""
    async def _fetch():
        client = get_backend_client()
        tasks = [client.get_audio_files(kid) for kid in knowledge_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_audio = []
        for res in results:
            if not isinstance(res, Exception):
                all_audio.extend(res)
        return all_audio
    
    return run_async(_fetch())


# Initialize session state
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""
if "selected_agent_id" not in st.session_state:
    st.session_state.selected_agent_id = None
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None  # Store full agent object
if "current_session" not in st.session_state:
    st.session_state.current_session: PatientSession | None = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history: list[ConversationMessage] = []

# --- Patient ID Section ---

st.subheader("1. Patient ID")


with st.container(border=True):
    if st.button("🎯 Demo Patient ID", help="Load Demo Patient ID"):
        st.session_state.patient_id = "A123456789"
        st.rerun()
    patient_id_input = st.text_input(
        "Enter Patient ID",
        value=st.session_state.patient_id,
        help="Alphanumeric only"
    )

if patient_id_input:
    if not patient_id_input.isalnum():
        add_error_to_log("Invalid format: Alphanumeric only")
    else:
        st.session_state.patient_id = patient_id_input
        st.success(f"✅ Patient ID Confirmed: {patient_id_input}")
        
        # Auto-select first agent if none selected yet
        if not st.session_state.selected_agent_id:
            try:
                agents = get_cached_agents()
                if agents:
                    first_agent = agents[0]
                    st.session_state.selected_agent_id = first_agent.agent_id
                    st.session_state.selected_agent = first_agent
            except Exception:
                pass  # Silent fail - user can still select manually
else:
    st.info("Please enter Patient ID to continue")



# --- Education Audio Section ---
# Show if patient ID is valid (agent is auto-selected)
if st.session_state.patient_id and st.session_state.patient_id.isalnum():
    st.divider()
    st.subheader("2. Education Audio")
    
    current_agent = st.session_state.selected_agent
    
    if not current_agent:
        st.info("ℹ️ No agents available. Please check the Agent Setup page.")
    elif not current_agent.knowledge_ids:
        st.info("ℹ️ This agent has no linked knowledge base")
    else:
        try:
            audio_files = get_cached_audio_files(tuple(current_agent.knowledge_ids))
            
            if not audio_files:
                st.info("ℹ️ No education audio available for this agent")
            else:
                # Display audio players
                for audio in audio_files:
                    with st.expander(f"🔊 {audio.script[:30]}... ({audio.voice_id})"):
                        st.audio(audio.audio_url)
                        st.caption(f"Script: {audio.script}")
                
        except Exception as e:
            add_error_to_log(f"Failed to load audio files: {str(e)}")

# --- Conversation Section ---
@st.fragment
def render_conversation_interface():
    # Only show if patient ID is valid
    if not (st.session_state.patient_id and st.session_state.patient_id.isalnum()):
        return
    
    st.divider()
    st.subheader("3. Conversation Test")

    # --- Agent Selection (moved from old Section 2) ---
    with st.container(border=True):
        try:
            agents = get_cached_agents()
            
            if not agents:
                st.warning("⚠️ No agents available")
                st.info("📢 The voice agent will be ready to serve you soon.")
                return  # Cannot proceed without agent
            else:
                agent_options = {a.name: a for a in agents}
                selected_agent_name = st.selectbox(
                    "Select Agent",
                    options=list(agent_options.keys()),
                    key="agent_selector_main"
                )
                
                if selected_agent_name:
                    selected_agent = agent_options[selected_agent_name]
                    st.session_state.selected_agent_id = selected_agent.agent_id
                    st.session_state.selected_agent = selected_agent
                    st.caption(f"Knowledge IDs: {', '.join(selected_agent.knowledge_ids)}")
                        
        except Exception as e:
            add_error_to_log(f"Failed to load agent list: {str(e)}")
            st.warning("⚠️ Failed to load agents")
            return  # Cannot proceed on error

    # Check if agent is selected before proceeding
    if not st.session_state.selected_agent_id:
        return

    # Helper async functions (use global client)
    async def start_new_session(p_id, a_id):
        return await client.create_patient_session(p_id, a_id)

    async def send_msg(s_id, msg, chat_mode):
        return await client.send_patient_message(s_id, msg, chat_mode=chat_mode)

    async def end_sess(s_id):
        return await client.end_patient_session(s_id)

    # 1. Start Conversation Button
    if st.session_state.current_session is None:
        if st.button("🚀 Start Conversation", type="primary"):
            with st.spinner("Connecting..."):
                try:
                    new_session = run_async(
                        start_new_session(st.session_state.patient_id, st.session_state.selected_agent_id)
                    )
                    st.session_state.current_session = new_session
                    st.session_state.conversation_history = []  # Reset history
                    st.rerun()
                except Exception as e:
                    add_error_to_log(f"Connection failed: {str(e)}")

    # 2. Active Conversation Interface
    else:
        # Init Chat Mode state (needed for logic before UI render)
        if "chat_mode_enabled" not in st.session_state:
            st.session_state.chat_mode_enabled = True
        chat_mode = st.session_state.chat_mode_enabled

        # Show status
        st.success(f"🟢 Connected - Session ID: {st.session_state.current_session.session_id}")
        st.info("ℹ️ **Note**: A full audio conversation mode will be implemented in the future React web interface.")
        
        # Display History
        for msg in st.session_state.conversation_history:
            with st.chat_message(msg.role):
                # Timestamp header
                timestamp_str = msg.timestamp.strftime("%H:%M:%S")
                st.caption(f"🕒 {timestamp_str}")
                
                st.write(msg.content)
                
                # Audio Playback - only show when Chat Mode is OFF (audio was generated)
                if msg.audio_data and not chat_mode:
                    try:
                        audio_bytes = base64.b64decode(msg.audio_data)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        add_error_to_log(f"Cannot play audio: {str(e)}") 

        # Input
        if prompt := st.chat_input("Type your message..."):
            # Add user message immediately
            user_msg = ConversationMessage(role="patient", content=prompt, timestamp=datetime.now())
            st.session_state.conversation_history.append(user_msg)
            
            # Send to backend
            with st.spinner("Agent is thinking..."):
                try:
                    response = run_async(
                        send_msg(st.session_state.current_session.session_id, prompt, chat_mode)
                    )
                    # Add agent response
                    agent_msg = ConversationMessage(
                        role="agent", 
                        content=response.response_text, 
                        timestamp=response.timestamp,
                        audio_data=response.audio_data
                    )
                    st.session_state.conversation_history.append(agent_msg)
                    st.rerun()
                except Exception as e:
                    add_error_to_log(f"Message send failed: {str(e)}")

        # End Conversation Section
        st.divider()
        
        # Toggle at bottom 
        st.toggle("💬 Chat Mode (Text Only)", key="chat_mode_enabled", help="Disable audio synthesis for faster response and cost saving")
        
        col_clear, col_end = st.columns([1, 1])
        
        with col_clear:
            if st.button("🧹 Clear History", use_container_width=True, help="Clear the chat history from the UI"):
                st.session_state.conversation_history = []
                st.rerun()
        
        with col_end:
            if st.button("🛑 End Conversation", type="secondary", use_container_width=True):
                with st.spinner("Ending session..."):
                    try:
                        run_async(end_sess(st.session_state.current_session.session_id))
                        st.session_state.current_session = None
                        st.info("Conversation ended")
                        st.rerun()
                    except Exception as e:
                        add_error_to_log(f"Failed to end conversation: {str(e)}")

render_conversation_interface()

render_error_console()
render_footer()

