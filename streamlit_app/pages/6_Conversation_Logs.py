
import asyncio
import base64
import streamlit as st
import logging
from datetime import datetime, time

from streamlit_app.services.backend_api import get_backend_client, BackendAPIClient
from streamlit_app.services.models import ConversationSummary, ConversationDetail
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer

# Page Configuration
st.set_page_config(
    page_title="Conversation Logs",
    page_icon="💬",
    layout="wide"
)

render_sidebar()

# Custom CSS for chat styling
st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 2rem;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 10px;
        max-width: 80%;
    }
    .chat-patient {
        background-color: #f0f2f6;
        align_self: flex-start;
        border-left: 5px solid #ff4b4b;
    }
    .chat-agent {
        background-color: #e6f3ff;
        align_self: flex-end;
        border-right: 5px solid #0068c9;
    }
    .attention-badge {
        background-color: #ffcccc;
        color: #990000;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .stat-card {
        padding: 1rem;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def render_filters():
    """Render filters in a horizontal layout at the top of the page."""
    st.subheader("Filter Logs")
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1], vertical_alignment="bottom")
        start_date = None
        end_date = None
        
        with col1:
            patient_id = st.text_input("Patient ID", placeholder="Enter ID...")
        
        with col2:
            start_d = st.date_input("Start Date", value=None)
            if start_d:
                start_date = datetime.combine(start_d, time.min)
                
        with col3:
            end_d = st.date_input("End Date", value=None)
            if end_d:
                end_date = datetime.combine(end_d, time.max)
                
        with col4:
            requires_attention = st.checkbox("Attention Only", value=False)
    
    return patient_id, start_date, end_date, requires_attention

def render_stats_display(stats: dict):
    """Render aggregate statistics from backend."""
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Conversations", stats.get("total_conversations", 0))
    with cols[1]:
        avg_dur = stats.get("average_duration_formatted", "0m 0s")
        st.metric("Avg Duration", avg_dur)
    with cols[2]:
        att_pct = stats.get("attention_percentage", 0)
        st.metric("Attention Needed %", f"{att_pct:.1f}%")
    with cols[3]:
        # Placeholder or other stat
        pass

def render_conversation_list(conversations: list[ConversationSummary]):
    """Render list of conversations as selectable items."""
    st.subheader(f"Conversation List ({len(conversations)})")
    
    if not conversations:
        st.info("No logs found matching criteria.")
        return None

    # Create a nice dataframe for display
    data = []
    for c in conversations:
        data.append({
            "ID": c.conversation_id,
            "Date": c.created_at.strftime("%Y-%m-%d %H:%M"),
            "Patient": c.patient_id,
            "Agent Name": c.agent_name,
            "Msg Count": c.total_messages,
            "Duration": f"{c.duration_seconds}s",
            "Attention": "⚠️ Yes" if c.requires_attention else "No"  # Use Yes/No
        })
    
    # Use dataframe with selection
    import pandas as pd
    df = pd.DataFrame(data)
    
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )
    
    if len(event.selection.rows) > 0:
        selected_row_idx = event.selection.rows[0]
        # map back to conversation ID
        # Since df is same order as conversations list
        return conversations[selected_row_idx].conversation_id
    
    return None

async def render_detail_view(conversation_id: str):
    """Render detailed view of a single conversation."""
    client = get_backend_client()
    try:
        detail = await client.get_conversation_detail(conversation_id)
    except Exception as e:
        st.error(f"Failed to load details: {e}")
        return

    st.divider()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Conversation with {detail.patient_id}")
        if detail.requires_attention:
            st.warning("⚠️ This conversation requires attention")
    with col2:
        if st.button("Close Details", type="secondary"):
            st.session_state.selected_conversation_id = None
            st.rerun()

    # Metadata
    metadata_cols = st.columns(4)
    metadata_cols[0].write(f"**Date:** {detail.created_at.strftime('%Y-%m-%d %H:%M')}")
    metadata_cols[1].write(f"**Agent:** {detail.agent_name}")
    metadata_cols[2].write(f"**Duration:** {detail.duration_seconds}s")
    metadata_cols[3].write(f"**Msg Count:** {detail.total_messages}")

    # Two main columns: Chat Transcript & Analysis
    main_cols = st.columns([2, 1])
    
    with main_cols[0]:
        st.subheader("Transcript")
        with st.container(height=600):
            for msg in detail.messages:
                role = "Patient" if msg.role == "patient" else "Agent"
                icon = "👤" if msg.role == "patient" else "🤖"
                
                div = f"""
                <div style="width: 100%; display: flex; justify_content: {'flex-end' if msg.role=='agent' else 'flex-start'}; margin-bottom: 10px;">
                    <div style="background-color: {'#e6f3ff' if msg.role=='agent' else '#f0f2f6'}; padding: 10px 15px; border-radius: 12px; max-width: 80%;">
                        <div style="font-size: 0.8rem; color: #666; margin-bottom: 4px;">{icon} {role} • {msg.timestamp.strftime('%H:%M:%S')}</div>
                        <div>{msg.content}</div>
                    </div>
                </div>
                """
                st.markdown(div, unsafe_allow_html=True)
                
                # If audio available
                if msg.audio_data:
                    try:
                        audio_bytes = base64.b64decode(msg.audio_data)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception:
                        st.caption("Audio unavailable")

    with main_cols[1]:
        st.subheader("Analysis")
        
        with st.expander("Key Concerns", expanded=True):
            if detail.main_concerns:
                for c in detail.main_concerns:
                    st.markdown(f"- {c}")
            else:
                st.info("No specific concerns.")
                
        with st.expander("Unanswered Questions", expanded=True):
            if detail.unanswered_questions:
                for q in detail.unanswered_questions:
                     st.error(f"❓ {q}")
            else:
                st.success("All questions answered!")

        with st.expander("Answered Questions", expanded=False):
            if detail.answered_questions:
                for q in detail.answered_questions:
                    st.markdown(f"✅ {q}")
            else:
                st.info("No answered questions.")

async def main():
    st.title("💬 Conversation Logs")
    st.markdown("Review and analyze past conversations between patients and AI agents.")
    
    # --- Filters Section (Top) ---
    patient_id, start_date, end_date, requires_attention = render_filters()
    
    st.divider()
    
    # --- Load Data ---
    client = get_backend_client()
    try:
        with st.spinner("Loading logs..."):
            conversations = await client.get_conversation_logs(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                requires_attention_only=requires_attention
            )
            stats = await client.get_conversation_statistics()
    except Exception as e:
        st.error(f"Failed to fetch logs: {e}")
        render_footer()
        return

    # --- Stats Section ---
    render_stats_display(stats)
    
    # --- Handle Selection State ---
    if "selected_conversation_id" not in st.session_state:
        st.session_state.selected_conversation_id = None
        
    # --- Conversation List ---
    st.markdown("---")
    selected_id = render_conversation_list(conversations)
    
    # Update selection if changed
    if selected_id:
        st.session_state.selected_conversation_id = selected_id
        
    # --- Detail View ---
    if st.session_state.selected_conversation_id:
        await render_detail_view(st.session_state.selected_conversation_id)

    render_footer()

if __name__ == "__main__":
    asyncio.run(main())
