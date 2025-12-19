import streamlit as st

def render_sidebar() -> None:
    """Render the sidebar navigation."""
    with st.sidebar:
        st.image(
            "https://via.placeholder.com/200x80?text=ElevenDops",
            use_container_width=True,
        )
        st.divider()

        st.subheader("📍 Navigation")

        # Navigation links to available pages
        st.page_link("app.py", label="🏠 Home", icon="🏠")
        st.page_link(
            "pages/1_Doctor_Dashboard.py",
            label="📊 Doctor Dashboard",
            icon="📊",
        )

        st.divider()

        # System status indicator
        st.subheader("⚡ System Status")
        st.success("Backend: Online", icon="✅")

        st.divider()

        # Quick actions
        st.subheader("🚀 Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
