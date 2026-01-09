import streamlit as st
import asyncio
from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.exceptions import APIError
from streamlit_app.components.sidebar import render_sidebar
from streamlit_app.components.footer import render_footer
from streamlit_app.components.error_console import add_error_to_log, render_error_console
from backend.models.schemas import DEFAULT_DOCUMENT_TAGS

st.set_page_config(page_title="Upload Knowledge", page_icon="📚", layout="wide")

render_sidebar()

st.title("📚 Upload Knowledge Base")
st.markdown("Upload medical documents for the AI agent to reference during patient interactions.")

# Initialize client
client = get_backend_client()


@st.cache_data(ttl=30)
def get_cached_documents():
    """Fetch documents with caching (30s TTL)."""
    return asyncio.run(client.get_knowledge_documents())


@st.dialog("Edit Document")
def edit_document_dialog(doc):
    """Dialog for editing document metadata.
    
    Using @st.dialog isolates this form from the main page,
    preventing full page reruns when interacting with the edit form.
    
    Args:
        doc: The document object to edit.
    """
    st.text(f"Editing: {doc.disease_name}")
    
    new_name = st.text_input(
        "Disease Name", 
        value=doc.disease_name, 
        key=f"dialog_edit_name_{doc.knowledge_id}"
    )
    
    # Merge existing tags with defaults to handle custom tags
    combined_options = list(dict.fromkeys(DEFAULT_DOCUMENT_TAGS + doc.tags))
    new_tags = st.multiselect(
        "Document Tags",
        options=combined_options,
        default=doc.tags,
        format_func=lambda x: x.replace("_", " ").title(),
        key=f"dialog_edit_tags_{doc.knowledge_id}"
    )

    custom_tags_edit_input = st.text_input(
        "Custom Tags (comma-separated)",
        placeholder="e.g., urgent, specialist_review",
        help="Add your own tags beyond the predefined list",
        key=f"dialog_edit_custom_tags_{doc.knowledge_id}"
    )
    
    new_content = st.text_area(
        "Document Content",
        value=doc.raw_content,
        height=300,
        key=f"dialog_edit_content_{doc.knowledge_id}"
    )
    
    # Status placeholder for full-width spinner display
    status_placeholder = st.empty()
    
    btn_c1, btn_c2, _ = st.columns([1.2, 1.2, 4])
    with btn_c1:
        save_clicked = st.button("Save", key=f"dialog_save_{doc.knowledge_id}", type="primary")
    with btn_c2:
        if st.button("Cancel", key=f"dialog_cancel_{doc.knowledge_id}"):
            st.rerun()
    
    if save_clicked:
        # Parse custom tags from edit input
        parsed_custom_tags = []
        if custom_tags_edit_input and custom_tags_edit_input.strip():
            parsed_custom_tags = [
                tag.strip().lower().replace(" ", "_") 
                for tag in custom_tags_edit_input.split(",") 
                if tag.strip()
            ]
        
        # Combine multiselect tags with custom tags
        all_tags = list(dict.fromkeys(new_tags + parsed_custom_tags))

        if not new_name.strip():
            add_error_to_log("Disease name required")
        elif not all_tags:
            add_error_to_log("At least one tag required")
        elif not new_content.strip():
            add_error_to_log("Content cannot be empty")
        else:
            with status_placeholder:
                with st.spinner("Saving changes..."):
                    try:
                        asyncio.run(client.update_knowledge_document(
                            doc.knowledge_id, 
                            disease_name=new_name.strip(),
                            tags=all_tags,
                            raw_content=new_content.strip()
                        ))
                        get_cached_documents.clear()
                        st.success("Updated!")
                        st.rerun()
                    except APIError as e:
                        add_error_to_log(f"Update failed: {e.message}")


@st.dialog("Confirm Delete")
def confirm_delete_dialog(doc):
    """Dialog for confirming document deletion.
    
    Using @st.dialog isolates this confirmation from the main page,
    providing a clear, focused UX for destructive actions.
    
    Args:
        doc: The document object to delete.
    """
    st.warning(f"Are you sure you want to delete **{doc.disease_name}**?")
    st.text("This will permanently remove the document from storage and ElevenLabs.")
    
    # Status placeholder for full-width spinner display
    status_placeholder = st.empty()
    
    btn_c1, btn_c2, _ = st.columns([1.5, 1.5, 4])
    with btn_c1:
        delete_clicked = st.button("Delete", key=f"confirm_del_{doc.knowledge_id}", type="primary")
    with btn_c2:
        if st.button("Cancel", key=f"cancel_del_{doc.knowledge_id}"):
            st.rerun()
    
    if delete_clicked:
        with status_placeholder:
            with st.spinner("Deleting document..."):
                try:
                    asyncio.run(client.delete_knowledge_document(doc.knowledge_id))
                    get_cached_documents.clear()
                    st.toast("Document deleted!")
                    st.rerun()
                except APIError as e:
                    add_error_to_log(f"Delete failed: {e.message}")


# --- File Upload Section ---
# Initialize form ID for dynamic widget keys to allow clearing
if "upload_form_id" not in st.session_state:
    st.session_state["upload_form_id"] = 0

st.subheader("Submit New Document")

# Using st.form to batch all widget interactions - page only re-renders on submit
with st.form(f"upload_document_form_{st.session_state.upload_form_id}", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        disease_name = st.text_input(
            "Disease/Condition Name", 
            placeholder="e.g., Hypertension"
        )
    
    with col2:
        selected_tags = st.multiselect(
            "Document Tags",
            options=DEFAULT_DOCUMENT_TAGS,
            default=["faq"],
            format_func=lambda x: x.replace("_", " ").title()
        )
    
    # Custom tag entry
    custom_tags_input = st.text_input(
        "Custom Tags (comma-separated)",
        placeholder="e.g., urgent, specialist_review",
        help="Add your own tags beyond the predefined list"
    )
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["txt", "md"]
    )
    
    submitted = st.form_submit_button("Save & Sync", type="primary")

if submitted:
    # Parse custom tags from text input
    custom_tags = []
    if custom_tags_input and custom_tags_input.strip():
        custom_tags = [
            tag.strip().lower().replace(" ", "_") 
            for tag in custom_tags_input.split(",") 
            if tag.strip()
        ]
    
    # Combine selected tags with custom tags (deduplicated)
    all_tags = list(dict.fromkeys(selected_tags + custom_tags))
    
    if not disease_name or not disease_name.strip():
        add_error_to_log("Please enter a disease name.")
    elif not all_tags:
        add_error_to_log("Please select or enter at least one tag.")
    elif not uploaded_file:
        add_error_to_log("Please upload a file.")
    else:
        # File size check (300KB = 300 * 1024 bytes)
        if uploaded_file.size > 300 * 1024:
            add_error_to_log("File size exceeds 300KB limit.")
        else:
            content = uploaded_file.read().decode("utf-8")
            
            with st.spinner("Uploading and syncing..."):
                try:
                    # Run async function in sync context
                    doc = asyncio.run(client.upload_knowledge(
                        content=content,
                        disease_name=disease_name.strip(),
                        tags=all_tags
                    ))
                    st.success(f"Document '{disease_name}' uploaded successfully! Sync status: {doc.sync_status}")

                    
                    # Clear cache and form inputs
                    get_cached_documents.clear()
                    st.session_state["upload_form_id"] += 1
                    
                    # Rerun to update list
                    st.rerun()
                except APIError as e:
                    add_error_to_log(f"Upload failed: {e.message}")
                except Exception as e:
                    add_error_to_log(f"An unexpected error occurred: {e}")

# --- Document List Section ---
# Using @st.fragment to isolate document list interactions from upload form
@st.fragment
def render_document_list():
    """Render document list in an isolated fragment.
    
    Actions like Refresh, Edit, Delete only re-render this section,
    keeping the upload form state stable.
    """
    with st.container(border=True):
        # Refresh button - only triggers fragment re-render
        if st.button("Refresh List"):
            get_cached_documents.clear()

        try:
            documents = get_cached_documents()
            
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
                        "Tags": ", ".join(doc.tags),
                        "Created At": doc.created_at.strftime("%Y-%m-%d %H:%M"),
                        "Modified At": doc.modified_at.strftime("%Y-%m-%d %H:%M") if doc.modified_at else "-",
                        "Sync Status": doc.sync_status
                    })
                    
                st.dataframe(data, use_container_width=True, hide_index=True)
                
                # Actions for each document (Delete / Retry)
                st.markdown("### Document Actions")
                
                for doc in documents:
                    # Normal Display Row - edit form now opens in a dialog
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                    with col1:
                        st.text(f"{doc.disease_name} ({', '.join(doc.tags)})")
                    
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
                        # Edit button now opens a dialog for isolated editing
                        if st.button("Edit", key=f"edit_btn_{doc.knowledge_id}"):
                            edit_document_dialog(doc)

                    with col4:
                        # Delete button opens confirmation dialog
                        if st.button("Delete", key=f"del_{doc.knowledge_id}"):
                            confirm_delete_dialog(doc)

                    with col5:
                        # Retry button - only for failed documents
                        if doc.sync_status == "failed":
                            if st.button("Retry", key=f"retry_{doc.knowledge_id}", disabled=(doc.sync_status == "syncing")):
                                try:
                                    asyncio.run(client.retry_knowledge_sync(doc.knowledge_id))
                                    get_cached_documents.clear()
                                    st.success("Retry initiated.")
                                except APIError as e:
                                    add_error_to_log(f"Retry failed: {e.message}")

        except APIError as e:
            add_error_to_log(f"Failed to load documents: {e.message}")
        except Exception as e:
            add_error_to_log(f"An unexpected error occurred loading documents: {e}")


st.divider()
st.subheader("Existing Documents")
render_document_list()

render_error_console()
render_footer()

