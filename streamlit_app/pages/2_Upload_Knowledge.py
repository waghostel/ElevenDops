import streamlit as st
import asyncio
from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.exceptions import APIError
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer

st.set_page_config(page_title="Upload Knowledge", page_icon="📚", layout="wide")

render_sidebar()

st.title("📚 Upload Knowledge Base")
st.markdown("Upload medical documents for the AI agent to reference during patient interactions.")

# Initialize client
client = get_backend_client()

# --- File Upload Section ---
# Header and Submit button on the same line
col_header, col_btn = st.columns([10, 1], vertical_alignment="center")
with col_header:
    st.subheader("Submits New Document")

with st.form("upload_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        disease_name = st.text_input("Disease/Condition Name", placeholder="e.g., Hypertension")
    
    with col2:
        document_type = st.selectbox(
            "Document Type",
            options=["faq", "post_care", "precautions"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "md"])  
    # Button aligned right using columns
    submitted = st.form_submit_button("Save & Sync")

if submitted:
    if not disease_name or not disease_name.strip():
        st.error("Please enter a disease name.")
    elif not uploaded_file:
        st.error("Please upload a file.")
    else:
        # File size check (300KB = 300 * 1024 bytes)
        if uploaded_file.size > 300 * 1024:
            st.error("File size exceeds 300KB limit.")
        else:
            content = uploaded_file.read().decode("utf-8")
            
            with st.spinner("Uploading and syncing..."):
                try:
                    # Run async function in sync context
                    doc = asyncio.run(client.upload_knowledge(
                        content=content,
                        disease_name=disease_name.strip(),
                        document_type=document_type
                    ))
                    st.success(f"Document '{disease_name}' uploaded successfully! Sync status: {doc.sync_status}")
                    # Rerun to update list
                    st.rerun()
                except APIError as e:
                    st.error(f"Upload failed: {e.message}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

# --- Document List Section ---
# --- Document List Section ---
st.divider()
st.subheader("Existing Documents")
with st.container(border=True):
    # Header and Refresh button on the same line
    if st.button("Refresh List"):
        st.rerun()

    try:
        documents = asyncio.run(client.get_knowledge_documents())
        
        if not documents:
            st.info("No documents uploaded yet.")
        else:
            # Convert to list of dicts for dataframe, or custom display
            # Let's use a dataframe for clean display
            data = []
            for doc in documents:
                data.append({
                    "ID": doc.knowledge_id,
                    "Disease": doc.disease_name,
                    "Type": doc.document_type,
                    "Created At": doc.created_at.strftime("%Y-%m-%d %H:%M"),
                    "Sync Status": doc.sync_status
                })
                
            st.dataframe(data, use_container_width=True, hide_index=True)
            
            # Actions for each document (Delete / Retry)
            st.markdown("### Document Actions")
            
            for doc in documents:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                with col1:
                    st.text(f"{doc.disease_name} ({doc.document_type})")
                
                with col2:
                    # Status display with color and retry count
                    status_color = "green"
                    if doc.sync_status == "failed":
                        status_color = "red"
                    elif doc.sync_status == "syncing":
                        status_color = "blue"
                    elif doc.sync_status == "pending":
                        status_color = "orange"
                    
                    status_label = doc.sync_status
                    if doc.sync_retry_count > 0:
                        status_label += f" (Retry {doc.sync_retry_count})"

                    st.markdown(f":{status_color}[{status_label}]")
                    
                    # Show error details for failed syncs
                    if doc.sync_status == "failed" and doc.sync_error_message:
                        with st.expander("Error Details"):
                            st.error(doc.sync_error_message)
                    
                with col3:
                    if st.button("Delete", key=f"del_{doc.knowledge_id}"):
                        if st.button("Confirm Delete?", key=f"conf_del_{doc.knowledge_id}"):
                            try:
                                asyncio.run(client.delete_knowledge_document(doc.knowledge_id))
                                st.success("Deleted!")
                                st.rerun()
                            except APIError as e:
                                st.error(f"Delete failed: {e.message}")

                with col4:
                    # Retry button - only for failed documents
                    if doc.sync_status == "failed":
                        if st.button("Retry Sync", key=f"retry_{doc.knowledge_id}", disabled=(doc.sync_status == "syncing")):
                            try:
                                asyncio.run(client.retry_knowledge_sync(doc.knowledge_id))
                                st.success("Retry initiated.")
                                st.rerun()
                            except APIError as e:
                                st.error(f"Retry failed: {e.message}")

    except APIError as e:
        st.error(f"Failed to load documents: {e.message}")
    except Exception as e:
        st.error(f"An unexpected error occurred loading documents: {e}")

render_footer()
