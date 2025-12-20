
import streamlit as st
import asyncio
import base64
from datetime import datetime
from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.services.models import PatientSession, ConversationMessage

# Page Configuration
st.set_page_config(
    page_title="病患測試",
    page_icon="🏥",
    layout="wide",
)

render_sidebar()

st.title("🏥 病患測試 (Patient Test)")

# Initialize session state
if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""
if "selected_agent_id" not in st.session_state:
    st.session_state.selected_agent_id = None
if "current_session" not in st.session_state:
    st.session_state.current_session: PatientSession | None = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history: list[ConversationMessage] = []

# --- Patient ID Section ---
st.subheader("1. 此病患ID (Patient ID)")
patient_id_input = st.text_input(
    "請輸入病患ID (Enter Patient ID)",
    value=st.session_state.patient_id,
    help="只允許字母和數字 (Alphanumeric only)"
)

if patient_id_input:
    if not patient_id_input.isalnum():
        st.error("❌ 病患ID 格式錯誤：只允許字母和數字 (Invalid format: Alphanumeric only)")
    else:
        st.session_state.patient_id = patient_id_input
        st.success(f"✅ 病患ID 已確認: {patient_id_input}")
else:
    st.info("請輸入病患ID以繼續 (Please enter Patient ID to continue)")

# Only proceed if patient ID is valid
if st.session_state.patient_id and st.session_state.patient_id.isalnum():
    st.subheader("2. 選擇 Agent (Select Agent)")
    
    # Needs async handling or wrapper?
    # Streamlit runs synchronously, so we need a sync wrapper or run async via asyncio.run/loop
    # For MVP, we usually assume the client has sync wrappers or we use a helper.
    # Looking at backend_api.py, it's async def. 
    # We should use st.connection or run_until_complete pattern if not handled.
    # For now, I'll assume I need to handle async call.
    import asyncio
    
    async def fetch_agents():
        client = get_backend_client()
        return await client.get_agents()
        
    try:
        # Simple async runner
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agents = loop.run_until_complete(fetch_agents())
        loop.close()
        
        if not agents:
            st.warning("⚠️ 目前沒有可用的 Agent (No agents available)")
        else:
            agent_options = {a.name: a.agent_id for a in agents}
            selected_agent_name = st.selectbox(
                "選擇要測試的 Agent",
                options=list(agent_options.keys())
            )
            
            if selected_agent_name:
                st.session_state.selected_agent_id = agent_options[selected_agent_name]
                # Display agent details if needed (Requirements 2.2)
                # knowledge area etc not in basic list, but AgentConfig has knowledge_ids. 
                # Ideally we show description, but schema has knowledge_ids.
                selected_agent_obj = next((a for a in agents if a.agent_id == st.session_state.selected_agent_id), None)
                if selected_agent_obj:
                    st.caption(f"Knowledge IDs: {', '.join(selected_agent_obj.knowledge_ids)}")
                    
    except Exception as e:
        st.error(f"❌ 無法讀取 Agent 列表: {str(e)}")

# --- Education Audio Section ---
# Only show if agent is selected
if st.session_state.selected_agent_id:
    st.divider()
    st.subheader("3. 衛教語音 (Education Audio)")
    
    async def fetch_audio_files(knowledge_ids):
        # We need knowledge ID to fetch audio. 
        # But wait, backend API get_audio_files takes knowledge_id (singular).
        # An agent has multiple knowledge_ids. We should fetch for all of them.
        client = get_backend_client()
        tasks = [client.get_audio_files(kid) for kid in knowledge_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Flatten and handle errors
        all_audio = []
        for res in results:
            if not isinstance(res, Exception):
                all_audio.extend(res)
        return all_audio

    # Retrieve current agent object again or persist properly
    # (In a real app, we'd optimize this double lookup)
    # Using the same loop execution for simplicity
    try:
         # We need the knowledge IDs from the selected agent
         # This requires us to have stored the full agent object or fetch it again.
         # The earlier block only stored ID. 
         # Let's assume we re-fetch effectively or stored it (I'll improve storage next step).
         # For now, hacky re-fetch via cache data if possible, or just re-execute fetch_agents which is fast mock.
         
         # Better: let's fetch specific agent details if needed, but get_agents returns all.
         
         # Re-running fetch for MVP simplicity to get knowledge_ids
         loop = asyncio.new_event_loop()
         asyncio.set_event_loop(loop)
         agents = loop.run_until_complete(fetch_agents())
         
         current_agent = next((a for a in agents if a.agent_id == st.session_state.selected_agent_id), None)
         
         if current_agent and current_agent.knowledge_ids:
             audio_files = loop.run_until_complete(fetch_audio_files(current_agent.knowledge_ids))
             loop.close()
             
             if not audio_files:
                 st.info("ℹ️ 此 Agent 尚未生成衛教語音 (No education audio available)")
             else:
                 # Display audio players
                 for audio in audio_files:
                     with st.expander(f"🔊 {audio.script[:30]}... ({audio.voice_id})"):
                         st.audio(audio.audio_url)
                         st.caption(f"Script: {audio.script}")
         else:
             st.info("ℹ️ 此 Agent 沒有關聯的知識庫 (No linked knowledge base)")
             if loop.is_running(): loop.close()
             
    except Exception as e:
        st.error(f"❌ 無法讀取語音檔案: {str(e)}")
        # Ensure loop closed
        try: loop.close() 
        except: pass

# --- Conversation Section ---
if st.session_state.selected_agent_id:
    st.divider()
    st.subheader("4. 對話測試 (Conversation Test)")

    # Helper async functions
    async def start_new_session(p_id, a_id):
        client = get_backend_client()
        return await client.create_patient_session(p_id, a_id)

    async def send_msg(s_id, msg):
        client = get_backend_client()
        return await client.send_patient_message(s_id, msg)

    async def end_sess(s_id):
        client = get_backend_client()
        return await client.end_patient_session(s_id)

    # 1. Start Conversation Button
    if st.session_state.current_session is None:
        if st.button("🚀 開始對話 (Start Conversation)", type="primary"):
            with st.spinner("正在建立連線... (Connecting...)"):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    new_session = loop.run_until_complete(
                        start_new_session(st.session_state.patient_id, st.session_state.selected_agent_id)
                    )
                    loop.close()
                    
                    st.session_state.current_session = new_session
                    st.session_state.conversation_history = [] # Reset history
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 無法建立連線: {str(e)}")
                    try: loop.close()
                    except: pass

    # 2. Active Conversation Interface
    else:
        # Show status
        st.success(f"🟢 連線中 (Connected) - Session ID: {st.session_state.current_session.session_id}")
        
        # Display History
        for msg in st.session_state.conversation_history:
            with st.chat_message(msg.role):
                # Timestamp header
                timestamp_str = msg.timestamp.strftime("%H:%M:%S")
                st.caption(f"🕒 {timestamp_str}")
                
                st.write(msg.content)
                
                # Audio Playback
                if msg.audio_data:
                    try:
                        audio_bytes = base64.b64decode(msg.audio_data)
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.error(f"⚠️ 無法播放音檔 (Cannot play audio): {str(e)}") 

        # Input
        if prompt := st.chat_input("請輸入您的問題 (Type your message)..."):
            # Add user message immediately
            user_msg = ConversationMessage(role="patient", content=prompt, timestamp=datetime.now())
            st.session_state.conversation_history.append(user_msg)
            
            # Send to backend
            with st.spinner("Agent 正在思考... (Agent is thinking...)"):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        send_msg(st.session_state.current_session.session_id, prompt)
                    )
                    loop.close()
                    
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
                    st.error(f"❌ 訊息發送失敗: {str(e)}")
                    try: loop.close()
                    except: pass

        # End Conversation Button
        st.divider()
        if st.button("🛑 結束對話 (End Conversation)", type="secondary"):
             with st.spinner("正在結束對話... (Ending session...)"):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        end_sess(st.session_state.current_session.session_id)
                    )
                    loop.close()
                    
                    st.session_state.current_session = None
                    st.info("對話已結束 (Conversation ended)")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 無法結束對話: {str(e)}")
                    try: loop.close()
                    except: pass

