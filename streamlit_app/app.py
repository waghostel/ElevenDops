"""
ElevenDops Streamlit Application Entry Point.

This is the main entry point for the Streamlit MVP frontend.
Run with: streamlit run streamlit_app/app.py
"""

import streamlit as st

# Application constants
APP_VERSION = "0.1.0"
APP_TITLE = "ElevenDops"
APP_ICON = "🏥"

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


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


def render_main_content() -> None:
    """Render the main page content."""
    # Header with branding
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(
            """
            <div style="font-size: 80px; text-align: center;">🏥</div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.title("ElevenDops")
        st.markdown("*Intelligent Medical Assistant System*")

    st.divider()

    # Welcome message
    st.header("👋 Welcome to ElevenDops")
    st.markdown(
        """
        **ElevenDops** is an intelligent medical assistant system designed to enhance 
        medical education through advanced voice technology powered by ElevenLabs.
        
        Our platform helps medical educators and students by providing:
        - 🎯 **Realistic patient simulations** for clinical training
        - 🗣️ **Natural voice interactions** using state-of-the-art AI
        - 📚 **Comprehensive knowledge management** for medical content
        - 📈 **Detailed analytics** to track learning progress
        """
    )

    st.divider()

    # Key features section
    st.header("✨ Key Features")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            ### 📚 Knowledge Base
            Upload and manage medical documents, guidelines, and educational materials.
            """
        )

    with col2:
        st.markdown(
            """
            ### 🤖 AI Agents
            Configure intelligent assistant agents tailored for specific medical scenarios.
            """
        )

    with col3:
        st.markdown(
            """
            ### 🎙️ Voice Interaction
            Engage in real-time voice-based patient interactions for immersive training.
            """
        )

    with col4:
        st.markdown(
            """
            ### 📊 Analytics
            Monitor system usage, track progress, and analyze performance metrics.
            """
        )

    st.divider()

    # Getting started section
    st.header("🚀 Getting Started")
    st.info(
        """
        **New to ElevenDops?** Start by visiting the **Doctor Dashboard** to see 
        an overview of your system status, including uploaded documents, active agents, 
        and recent activities.
        
        Use the sidebar navigation to explore different sections of the application.
        """,
        icon="💡",
    )


def render_footer() -> None:
    """Render the footer with version info and copyright."""
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; color: #888; font-size: 0.85em;">
                <p>ElevenDops v{APP_VERSION}</p>
                <p>© 2024 ElevenDops Team. All rights reserved.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Main application entry point."""
    render_sidebar()
    render_main_content()
    render_footer()


if __name__ == "__main__":
    main()
