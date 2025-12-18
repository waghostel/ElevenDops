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
    BackendAPIClient,
    DashboardStats,
)

# Page configuration
st.set_page_config(
    page_title="Doctor Dashboard - ElevenDops",
    page_icon="📊",
    layout="wide",
)


def get_dashboard_stats() -> DashboardStats | None:
    """Fetch dashboard stats from backend API.

    Returns:
        DashboardStats if successful, None if error occurred.
    """
    try:
        client = BackendAPIClient()
        # Run async function in sync context
        return asyncio.run(client.get_dashboard_stats())
    except APIConnectionError as e:
        st.error(f"⚠️ Cannot connect to backend: {e.message}", icon="🔌")
        return None
    except APITimeoutError as e:
        st.error(f"⏱️ Request timed out: {e.message}", icon="⏱️")
        return None
    except APIError as e:
        st.error(f"❌ API Error: {e.message}", icon="❌")
        return None


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
        time_diff = datetime.now() - stats.last_activity
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
    st.title("📊 Doctor Dashboard")
    st.markdown("Monitor your system status and recent activities at a glance.")
    st.divider()

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.toast("Settings page coming soon!", icon="⚙️")

    st.divider()

    # Fetch and display stats
    with st.spinner("Loading dashboard data..."):
        stats = get_dashboard_stats()

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
            st.button("🎙️ Start Session", use_container_width=True, disabled=True)

        st.caption("*Quick actions will be available in future updates.*")
    else:
        # Error state with retry
        st.warning(
            "Could not load dashboard data. Please check if the backend is running.",
            icon="⚠️",
        )
        if st.button("🔄 Retry Connection"):
            st.rerun()


def main() -> None:
    """Main page entry point."""
    render_dashboard()


if __name__ == "__main__":
    main()
