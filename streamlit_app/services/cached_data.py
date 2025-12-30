import asyncio
from typing import List

import streamlit as st

from streamlit_app.services.backend_api import get_backend_client
from streamlit_app.services.models import KnowledgeDocument, VoiceOption

client = get_backend_client()

def run_async(coro):
    """Run async coroutine safely in sync Streamlit context.
    
    Uses existing event loop if available, otherwise creates new one.
    This prevents 'asyncio.run() cannot be called from a running event loop' errors.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # We're in an async context, need to run in a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        # No running loop, safe to use asyncio.run
        return asyncio.run(coro)


@st.cache_data(ttl=30)
def get_documents_cached() -> List[KnowledgeDocument]:
    """Fetch documents with caching (30s TTL).
    
    Uses @st.cache_data for clean, declarative caching instead of
    manual session state management.
    """
    try:
        return asyncio.run(client.get_knowledge_documents())
    except Exception as e:
        st.error(f"Unable to load documents. Please check your connection. (Error: {e})")
        return []


@st.cache_data(ttl=300)
def get_voices_cached() -> List[VoiceOption]:
    """Fetch voices with caching (5 min TTL).
    
    Uses @st.cache_data for clean, declarative caching instead of
    manual session state management.
    """
    try:
        return asyncio.run(client.get_available_voices())
    except Exception as e:
        st.error(f"Unable to load voice options. (Error: {e})")
        return []
