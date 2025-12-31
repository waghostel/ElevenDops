"""Error Console Component.

Shared error console UI for capturing and displaying error messages
across all pages with stacking and timestamps.
"""

from datetime import datetime

import streamlit as st


def _init_error_log():
    """Initialize error log in session state if not exists."""
    if "error_log" not in st.session_state:
        st.session_state.error_log = []


def add_error_to_log(message: str):
    """Add an error message to the error log with timestamp.
    
    Args:
        message: The error message to add.
    """
    _init_error_log()
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.error_log.append(f"[{timestamp}] {message}")


def render_error_console():
    """Render the error console UI if there are errors.
    
    Should be called before render_footer() in each page.
    """
    _init_error_log()
    if st.session_state.error_log:
        with st.expander("⚠️ Error Console", expanded=True):
            # Display errors in reverse order (newest first)
            error_text = "\n".join(reversed(st.session_state.error_log))
            st.code(error_text, language="log")
            if st.button("🗑️ Clear Errors", key="clear_error_log"):
                st.session_state.error_log = []
                st.rerun()
