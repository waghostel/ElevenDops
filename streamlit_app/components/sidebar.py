import streamlit as st

def render_sidebar() -> None:
    """Render the sidebar navigation."""
    with st.sidebar:
        # CSS to make sidebar use flexbox and push System Status to bottom
        st.markdown(
            """
            <style>
                /* Hide default MPA navigation */
                [data-testid="stSidebarNav"] {
                    display: none;
                }
                
                /* Make sidebar content container flex column with full height */
                [data-testid="stSidebarContent"] {
                    display: flex !important;
                    flex-direction: column !important;
                    height: 100vh !important;
                }
                
                /* Make user content container grow and use flex */
                [data-testid="stSidebarUserContent"] {
                    display: flex !important;
                    flex-direction: column !important;
                    flex-grow: 1 !important;
                }
                
                /* Make intermediate div grow */
                [data-testid="stSidebarUserContent"] > div:first-child {
                    display: flex !important;
                    flex-direction: column !important;
                    flex-grow: 1 !important;
                }
                
                /* Make vertical block grow */
                [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
                    display: flex !important;
                    flex-direction: column !important;
                    flex-grow: 1 !important;
                }
                
                /* Make the spacer container grow to push content down */
                [data-testid="stVerticalBlock"] > div:has(.sidebar-spacer) {
                    flex-grow: 1 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.subheader("Navigation")

        # Navigation links to available pages
        st.page_link("app.py", label="Quick Start", icon="🏥")
        st.page_link(
            "pages/1_Doctor_Dashboard.py",
            label="Doctor Dashboard",
            icon="👨‍⚕️",
        )
        st.page_link(
            "pages/2_Upload_Knowledge.py",
            label="Knowledge Base",
            icon="📚",
        )
        st.page_link(
            "pages/3_Education_Audio.py",
            label="Education Audio",
            icon="🎧",
        )
        st.page_link(
            "pages/4_Agent_Setup.py",
            label="Voice Agents",
            icon="🎙️",
        )
        st.page_link(
            "pages/5_Patient_Test.py",
            label="Patient Test",
            icon="🧪",
        )
        st.page_link(
            "pages/6_Conversation_Logs.py",
            label="Patient Insights",
            icon="💬",
        )

        # Spacer to push System Status to bottom
        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
        
        st.divider()
        
        # System status indicator
        st.subheader("System Status")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        # Settings at the bottom
        if st.button("⚙️ Settings", use_container_width=True):
            st.toast("Settings page coming soon!", icon="⚙️")
        st.success("Backend: Online", icon="✅")
    
