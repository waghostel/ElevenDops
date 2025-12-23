import streamlit as st

def render_sidebar() -> None:
    """Render the sidebar navigation."""
    st.logo("streamlit_app/images/elevenDops LOGO.PNG", size="large")
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
        try:
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
        except KeyError:
            # During testing, st.page_link may fail if pages aren't indexed
            # Fallback to simple text or nothing
            pass

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
        
        # Real Backend Health Check
        import httpx
        import os
        
        @st.cache_data(ttl=5, show_spinner=False)
        def check_backend_status() -> bool:
            """Check if the backend API is reachable."""
            # Allow tests to bypass checking
            if st.session_state.get("IS_TESTING_BACKEND"):
                return True

            try:
                # Use sync HTTP request - simpler and more reliable than async in cached function
                # Use 10s timeout because health check may take time when checking service connections
                backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
                response = httpx.get(f"{backend_url}/api/health", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    # Check if API is reachable (200) - consider it "online" even if services are unhealthy
                    # The sidebar shows if backend server is reachable, not if all services are healthy
                    return True
                return False
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPError):
                return False

        status = check_backend_status()
        
        if status:
            st.success("Backend: Online", icon="✅")
        else:
            st.error("Backend: Offline", icon="❌")
    
