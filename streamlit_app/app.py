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


from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer

def render_main_content() -> None:
    """Render the main page content."""
    # Header with branding
    # Header with branding
    st.title("🏥 ElevenDops: Your Voice Patient Education Platform")
    st.markdown("*AI-Powered Patient Education Platform*")

    st.divider()

    # Welcome message
    st.header("👋 Welcome to ElevenDops")
    with st.container(border=True):
        st.markdown(
            """
            **ElevenDops** is an AI-powered patient education platform that helps physicians 
            create personalized health education materials and intelligent voice assistants 
            to answer patient questions.
            
            Our platform empowers medical professionals by providing:
            - 📤 **Knowledge Upload** — Create and manage disease-specific educational documents
            - 🔊 **Education Audio** — Generate professional voice recordings using AI
            - 🤖 **AI Medical Assistants** — Build custom voice agents to answer patient questions 24/7
            - 📋 **Patient Insights** — Review conversation logs to understand patient concerns
            """
        )
        # Getting started section
        st.info(
            """
            **New to ElevenDops?** Start by visiting the **Doctor Dashboard** to see 
            an overview of your system status, including uploaded documents, active agents, 
            and recent activities.
            
            Use the sidebar navigation to explore different sections of the application.
            """,
            icon="💡",
        )
    
    st.divider()

    # Key features section
    st.header("✨ Key Features")

    # CSS for equal height cards
    st.markdown(
        """
        <style>
            /* Make feature cards equal height - target the row containing bordered containers */
            [data-testid="stHorizontalBlock"]:has([data-testid="stVerticalBlockBorderWrapper"]) {
                align-items: stretch !important;
            }
            
            /* Make columns flex containers */
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
                display: flex !important;
                flex-direction: column !important;
                flex-grow: 1 !important;
            }
            
            /* Make column's first child (stVerticalBlock wrapper) stretch */
            [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
                display: flex !important;
                flex-direction: column !important;
                flex-grow: 1 !important;
            }
            
            /* Make ALL intermediate divs in the column stretch */
            [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > div {
                display: flex !important;
                flex-direction: column !important;
                flex-grow: 1 !important;
            }
            
            /* Make the inner stVerticalBlock stretch */
            [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"] {
                display: flex !important;
                flex-direction: column !important;
                flex-grow: 1 !important;
            }
            
            /* Make the border wrapper stretch to fill remaining space */
            [data-testid="stVerticalBlockBorderWrapper"] {
                flex-grow: 1 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown(
                """
                ### 📤 Upload Knowledge
                
                **Create your medical education library**
                
                Upload and organize disease-specific documents (Markdown/TXT) to build your personalized knowledge base.
                
                ---
                
                **How it works:**
                1. Upload educational documents (e.g., post-surgery care, FAQs)
                2. Tag with disease name and document type
                3. System syncs content to ElevenLabs Knowledge Base
                
                ---
                
                **🩺 For Physicians:**
                - Eliminate repetitive explanations
                - Standardize patient education materials
                - Build a reusable medical knowledge library
                
                **👤 For Patients:**
                - Access accurate, physician-approved information
                - Get consistent answers anytime
                """
            )

    with col2:
        with st.container(border=True):
            st.markdown(
                """
                ### 🎧 Generate Audio
                
                **Transform text into professional voice recordings**
                
                Convert your medical documents into high-quality audio that patients can listen to anytime.
                
                ---
                
                **How it works:**
                1. Select an uploaded knowledge document
                2. AI generates a patient-friendly script
                3. Review and approve the script
                4. Generate professional audio with ElevenLabs TTS
                
                ---
                
                **🩺 For Physicians:**
                - Create audio once, use indefinitely
                - Maintain quality control with script approval
                - Offer accessible education for all literacy levels
                
                **👤 For Patients:**
                - Listen on-the-go or at home
                - Replay important instructions as needed
                - Better understand complex medical information
                """
            )

    with col3:
        with st.container(border=True):
            st.markdown(
                """
                ### 🤖 Create Agents
                
                **Build intelligent voice assistants for patients**
                
                Configure AI-powered agents that answer patient questions using your knowledge base.
                
                ---
                
                **How it works:**
                1. Create a new agent with a custom name
                2. Link it to your knowledge documents
                3. Choose voice personality & response style
                4. Deploy for patient interactions
                
                ---
                
                **🩺 For Physicians:**
                - Extend your reach with 24/7 AI assistants
                - Ensure responses are based on your approved content
                - Handle routine questions automatically
                
                **👤 For Patients:**
                - Get immediate answers without waiting
                - Ask questions in natural conversation
                - Receive consistent, reliable medical guidance
                """
            )

    with col4:
        with st.container(border=True):
            st.markdown(
                """
                ### 📋 Review Conversations
                
                **Understand patient concerns before appointments**
                
                Monitor and analyze patient-agent conversations to identify key concerns and improve care.
                
                ---
                
                **How it works:**
                1. View complete conversation logs by patient
                2. See answered vs. unanswered questions
                3. Identify cases flagged for doctor attention
                4. Prepare for appointments with patient insights
                
                ---
                
                **🩺 For Physicians:**
                - Know patient concerns before they arrive
                - Identify knowledge gaps to address
                - Improve efficiency during consultations
                
                **👤 For Patients:**
                - Confidence that complex questions reach the doctor
                - Better-prepared physicians for appointments
                - More focused and effective consultations
                """
            )

def main() -> None:
    """Main application entry point."""
    render_sidebar()
    render_main_content()
    render_footer(APP_VERSION)


if __name__ == "__main__":
    main()
