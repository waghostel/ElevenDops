
import asyncio
import base64
import streamlit as st
import logging
from datetime import datetime, time

from streamlit_app.services.backend_api import get_backend_client, BackendAPIClient
from streamlit_app.services.models import ConversationSummary, ConversationDetail

# Page Configuration
st.set_page_config(
    page_title="對話紀錄",
    page_icon="💬",
    layout="wide"
)

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
    """Render sidebar filters."""
    st.sidebar.header("篩選紀錄")
    
    patient_id = st.sidebar.text_input("病患 ID", placeholder="輸入 ID...")
    
    date_col1, date_col2 = st.sidebar.columns(2)
    start_date=None
    end_date=None
    
    with date_col1:
        start_d = st.date_input("開始日期", value=None)
        if start_d:
            start_date = datetime.combine(start_d, time.min)
            
    with date_col2:
        end_d = st.date_input("結束日期", value=None)
        if end_d:
            end_date = datetime.combine(end_d, time.max)
            
    requires_attention = st.sidebar.checkbox("僅顯示需關注", value=False)
    
    return patient_id, start_date, end_date, requires_attention

def render_stats_display(stats: dict):
    """Render aggregate statistics from backend."""
    
    cols = st.columns(4)
    with cols[0]:
        st.metric("總對話數", stats.get("total_conversations", 0))
    with cols[1]:
        avg_dur = stats.get("average_duration_formatted", "0m 0s")
        st.metric("平均時長", avg_dur)
    with cols[2]:
        att_pct = stats.get("attention_percentage", 0)
        st.metric("需關注比例", f"{att_pct:.1f}%")
    with cols[3]:
        # Placeholder or other stat
        pass

def render_conversation_list(conversations: list[ConversationSummary]):
    """Render list of conversations as selectable items."""
    st.subheader(f"對話列表 ({len(conversations)})")
    
    if not conversations:
        st.info("找不到符合條件的對話紀錄。")
        return None

    # Create a nice dataframe for display
    data = []
    for c in conversations:
        data.append({
            "ID": c.conversation_id,
            "日期": c.created_at.strftime("%Y-%m-%d %H:%M"),
            "病患": c.patient_id,
            "代理名稱": c.agent_name,
            "訊息數": c.total_messages,
            "時長": f"{c.duration_seconds}秒",
            "關注": "⚠️ 是" if c.requires_attention else "否"  # Use Is/No for Yes/No
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
        st.error(f"無法載入詳細資訊: {e}")
        return

    st.divider()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"與 {detail.patient_id} 的對話")
        if detail.requires_attention:
            st.warning("⚠️ 此對話需要關注")
    with col2:
        if st.button("關閉詳情", type="secondary"):
            st.session_state.selected_conversation_id = None
            st.rerun()

    # Metadata
    metadata_cols = st.columns(4)
    metadata_cols[0].write(f"**日期:** {detail.created_at.strftime('%Y-%m-%d %H:%M')}")
    metadata_cols[1].write(f"**代理:** {detail.agent_name}")
    metadata_cols[2].write(f"**時長:** {detail.duration_seconds}秒")
    metadata_cols[3].write(f"**訊息數:** {detail.total_messages}")

    # Two main columns: Chat Transcript & Analysis
    main_cols = st.columns([2, 1])
    
    with main_cols[0]:
        st.subheader("對話內容")
        with st.container(height=600):
            for msg in detail.messages:
                role = "病患" if msg.role == "patient" else "代理"
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
                        st.caption("音訊無法播放")

    with main_cols[1]:
        st.subheader("分析結果")
        
        with st.expander("主要關注點", expanded=True):
            if detail.main_concerns:
                for c in detail.main_concerns:
                    st.markdown(f"- {c}")
            else:
                st.info("無特定關注點。")
                
        with st.expander("未回答的問題", expanded=True):
            if detail.unanswered_questions:
                for q in detail.unanswered_questions:
                     st.error(f"❓ {q}")
            else:
                st.success("所有問題皆已回答！")

        with st.expander("已回答的問題", expanded=False):
            if detail.answered_questions:
                for q in detail.answered_questions:
                    st.markdown(f"✅ {q}")
            else:
                st.info("無已回答的問題。")

async def main():
    st.title("💬 對話紀錄")
    
    # Sidebar Filters
    patient_id, start_date, end_date, requires_attention = render_filters()
    
    # Load Data
    client = get_backend_client()
    try:
        with st.spinner("載入紀錄中..."):
            conversations = await client.get_conversation_logs(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                requires_attention_only=requires_attention
            )
            stats = await client.get_conversation_statistics()
    except Exception as e:
        st.error(f"無法取得紀錄: {e}")
        return

    # Render Stats
    render_stats_display(stats)
    
    # Handle Selection State
    if "selected_conversation_id" not in st.session_state:
        st.session_state.selected_conversation_id = None
        
    # Render List
    st.markdown("---")
    selected_id = render_conversation_list(conversations)
    
    # Update selection if changed
    if selected_id:
        st.session_state.selected_conversation_id = selected_id
        
    # Render Details if selected
    if st.session_state.selected_conversation_id:
        await render_detail_view(st.session_state.selected_conversation_id)

if __name__ == "__main__":
    asyncio.run(main())
