
import streamlit as st

def render_footer(app_version: str = "0.1.0") -> None:
    """Render the footer with version info and copyright."""
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; color: #888; font-size: 0.85em;">
                <p>ElevenDops v{app_version}</p>
                <p>© 2024 ElevenDops Team. All rights reserved.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
