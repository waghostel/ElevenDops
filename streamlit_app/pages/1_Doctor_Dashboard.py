"""
Doctor Dashboard Page.

Displays system statistics and quick monitoring capabilities for doctors.
"""

import asyncio
from datetime import datetime

import streamlit as st

from streamlit_app.services import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    get_backend_client,
    DashboardStats,
)
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer

# Page configuration
st.set_page_config(
    page_title="Doctor Dashboard - ElevenDops",
    page_icon="📊",
    layout="wide",
)

render_sidebar()


@st.cache_data(ttl=10)
def get_dashboard_stats() -> tuple[DashboardStats | None, str | None]:
    """Fetch dashboard stats from backend API.

    Returns:
        Tuple of (DashboardStats, None) if successful, or (None, error_message) if error occurred.
    """
    try:
        client = get_backend_client()
        # Run async function in sync context
        return (asyncio.run(client.get_dashboard_stats()), None)
    except APIConnectionError as e:
        return (None, f" Cannot connect to backend: {e.message}")
    except APITimeoutError as e:
        return (None, f"⏱️ Request timed out: {e.message}")
    except APIError as e:
        return (None, f"❌ API Error: {e.message}")


def render_metric_cards(stats: DashboardStats) -> None:
    """Render the four metric cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📄 Documents",
            value=stats.document_count,
            help="Total number of uploaded medical documents",
        )

    with col2:
        st.metric(
            label="🤖 Active Agents",
            value=stats.agent_count,
            help="Number of configured AI agents",
        )

    with col3:
        st.metric(
            label="🎵 Audio Files",
            value=stats.audio_count,
            help="Total generated audio files",
        )

    with col4:
        # Format last activity time
        now = datetime.now(stats.last_activity.tzinfo) if stats.last_activity.tzinfo else datetime.now()
        time_diff = now - stats.last_activity
        if time_diff.seconds < 60:
            last_activity_str = "Just now"
        elif time_diff.seconds < 3600:
            last_activity_str = f"{time_diff.seconds // 60}m ago"
        else:
            last_activity_str = stats.last_activity.strftime("%H:%M")

        st.metric(
            label="🕐 Last Activity",
            value=last_activity_str,
            help=f"Last activity: {stats.last_activity.strftime('%Y-%m-%d %H:%M:%S')}",
        )


def render_empty_states(stats: DashboardStats) -> None:
    """Render guidance messages for zero-count metrics."""
    if stats.document_count == 0:
        st.info(
            "📚 **No documents uploaded yet.** "
            "Start by uploading medical guidelines, textbooks, or educational materials.",
            icon="📚",
        )

    if stats.agent_count == 0:
        st.info(
            "🤖 **No agents configured.** "
            "Create your first AI agent to start patient simulations.",
            icon="🤖",
        )

    if stats.audio_count == 0:
        st.info(
            "🎙️ **No audio generated yet.** "
            "Audio files will appear here after voice interactions.",
            icon="🎙️",
        )


def render_dashboard() -> None:
    """Render the main dashboard content."""
    # Header
    st.title("👨‍⚕️ Doctor Dashboard")
    st.markdown("Monitor your system status and recent activities at a glance.")
    st.divider()

    # Fetch and display stats
    with st.spinner("Loading dashboard data..."):
        stats, error_message = get_dashboard_stats()

    if stats:
        # Display metric cards
        render_metric_cards(stats)

        st.divider()

        # Check for empty states and show guidance
        render_empty_states(stats)

        # Quick actions section
        st.subheader("🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("📤 Upload Document", use_container_width=True, disabled=True)
        with col2:
            st.button("➕ Create Agent", use_container_width=True, disabled=True)
        with col3:
            st.button("� Start Session", use_container_width=True, disabled=True)

        st.caption("*Quick actions will be available in future updates.*")
    else:
        # Error state - retry button first, then error messages

        if st.button("🔄 Retry Connection"):
            st.rerun()
        
        if error_message:
            st.error(error_message, icon="🔌")
        
        st.warning(
            "Could not load dashboard data. Please check if the backend is running.",
            icon="⚠️",
        )


def main() -> None:
    """Main page entry point."""
    render_dashboard()
    render_footer()


if __name__ == "__main__":
    main()
