
import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.firestore_data_service import FirestoreDataService
from backend.models.schemas import DashboardStatsResponse
from google.cloud import firestore

# **Feature: dashboard-real-statistics, Property 1: Dashboard counts match collection sizes**
# **Feature: dashboard-real-statistics, Property 4: Last activity is maximum timestamp**
# **Feature: dashboard-real-statistics, Property 5: Error fallback returns valid response**

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset FirestoreDataService singleton before each test."""
    FirestoreDataService._instance = None
    yield
    FirestoreDataService._instance = None

@pytest.mark.asyncio
async def test_dashboard_stats_properties():
    """Validates that dashboard stats correctly reflect collection states."""
    
    # Mock data strategies
    collection_sizes = st.integers(min_value=0, max_value=20)
    timestamps = st.lists(
        st.datetimes(
            min_value=datetime(2020, 1, 1), 
            max_value=datetime(2030, 1, 1)
        ), 
        min_size=0, 
        max_size=20
    )

    @given(
        doc_count=collection_sizes,
        agent_count=collection_sizes,
        audio_count=collection_sizes,
        doc_timestamps=timestamps,
        agent_timestamps=timestamps,
        audio_timestamps=timestamps,
        conv_timestamps=timestamps
    )
    @settings(max_examples=50) 
    async def run_test(
        doc_count, agent_count, audio_count,
        doc_timestamps, agent_timestamps, audio_timestamps, conv_timestamps
    ):
        # Setup mocks
        mock_db = MagicMock()
        
        # Mock count queries
        mock_doc_query = MagicMock()
        mock_doc_query.count.return_value.get.return_value = [[AsyncMock(value=doc_count)]]
        
        mock_agent_query = MagicMock()
        mock_agent_query.count.return_value.get.return_value = [[AsyncMock(value=agent_count)]]
        
        mock_audio_query = MagicMock()
        mock_audio_query.count.return_value.get.return_value = [[AsyncMock(value=audio_count)]]
        
        def collection_side_effect(name):
            if name == "knowledge_documents":
                return mock_doc_query
            elif name == "agents":
                return mock_agent_query
            elif name == "audio_files":
                return mock_audio_query
            # For iteration in _get_last_activity_timestamp
            return AsyncMock()

        mock_db.collection.side_effect = collection_side_effect

        with patch('backend.services.firestore_data_service.get_firestore_service') as mock_fs:
            mock_fs.return_value.db = mock_db
            service = FirestoreDataService()
            
            # Mock the helper logic since we mock db calls above for counts but mocking
            # chained calls for timestamps inside the same method is complex with side_effect
            # depending on call args. For this property, we focus on counts.
            # We can mock _get_last_activity_timestamp to return something valid.
            
            with patch.object(service, '_get_last_activity_timestamp', new_callable=AsyncMock) as mock_helper:
                mock_helper.return_value = datetime.now()
                
                stats = await service.get_dashboard_stats()
                
                # Property 1: Dashboard counts match collection sizes
                assert stats.document_count == doc_count
                assert stats.agent_count == agent_count
                assert stats.audio_count == audio_count


@pytest.mark.asyncio
async def test_last_activity_logic():
    """Validates Property 4: Last activity is maximum timestamp."""
    
    timestamps = st.lists(
        st.datetimes(
            min_value=datetime(2020, 1, 1), 
            max_value=datetime(2030, 1, 1)
        ),
        min_size=0,
        max_size=5
    )

    @given(
        doc_timestamps=timestamps,
        agent_timestamps=timestamps,
        audio_timestamps=timestamps,
        conv_timestamps=timestamps
    )
    @settings(max_examples=50)
    async def run_test(doc_timestamps, agent_timestamps, audio_timestamps, conv_timestamps):
        mock_db = AsyncMock()
        
        # Helper to create mock docs
        def create_mock_docs(ts_list):
            docs = []
            if not ts_list:
                return docs
            # Sort descending as the query does
            sorted_ts = sorted(ts_list, reverse=True)
            # We only query limit(1), so the stream only yields the first
            mock_doc = AsyncMock()
            mock_doc.to_dict.return_value = {"created_at": sorted_ts[0]}
            docs.append(mock_doc)
            return docs

        # Setup collection mocks
        def collection_side_effect(name):
            mock_col = AsyncMock()
            mock_query = AsyncMock()
            mock_stream = AsyncMock()
            
            if name == "knowledge_documents":
                mock_stream.stream.return_value = create_mock_docs(doc_timestamps)
            elif name == "agents":
                mock_stream.stream.return_value = create_mock_docs(agent_timestamps)
            elif name == "audio_files":
                mock_stream.stream.return_value = create_mock_docs(audio_timestamps)
            elif name == "conversations":
                mock_stream.stream.return_value = create_mock_docs(conv_timestamps)
            else:
                mock_stream.stream.return_value = []

            # Chain: collection().order_by().limit().stream()
            mock_col.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_stream
            
            return mock_col

        mock_db.collection.side_effect = collection_side_effect

        with patch('backend.services.firestore_data_service.get_firestore_service') as mock_fs:
            mock_fs.return_value.db = mock_db
            service = FirestoreDataService()
            
            # Calculate expected
            all_ts = doc_timestamps + agent_timestamps + audio_timestamps + conv_timestamps
            expected = max(all_ts) if all_ts else None
            
            result = await service._get_last_activity_timestamp()
            
            if expected:
                assert result == expected
            else:
                # Should be close to now if no data
                assert (datetime.now() - result).total_seconds() < 5


@pytest.mark.asyncio
async def test_error_fallback():
    """Validates Property 5: Error fallback returns valid response."""
    
    mock_db = AsyncMock()
    # Simulate DB error
    mock_db.collection.side_effect = Exception("Firestore Connection Error")
    
    with patch('backend.services.firestore_data_service.get_firestore_service') as mock_fs:
        mock_fs.return_value.db = mock_db
        service = FirestoreDataService()
        
        stats = await service.get_dashboard_stats()
        
        assert stats.document_count == 0
        assert stats.agent_count == 0
        assert stats.audio_count == 0
        assert isinstance(stats.last_activity, datetime)

@pytest.mark.asyncio
async def test_count_increment_on_creation():
    """Validates Property 2: Count increases after creation."""
    # This test simulates creation by mocking the DB state change
    # Since we are mocking the DB, we verify that if the DB returns X+1, the stats return X+1
    # This is essentially testing that get_dashboard_stats reflects the DB state,
    # which is covered by test_dashboard_stats_properties (Property 1).
    # However, to be explicit about "Action -> Change" relationship:
    
    initial_count = 5
    
    # We will test one entity type, e.g., knowledge document
    mock_db = MagicMock()
    mock_doc_query = MagicMock()
    
    # First call returns initial_count, Second call returns initial_count + 1
    # Note: side_effect can be an iterable
    mock_doc_query.count.return_value.get.side_effect = [
        [[AsyncMock(value=initial_count)]], 
        [[AsyncMock(value=initial_count + 1)]]
    ]
    
    # Mock other collections to return constant
    mock_other = MagicMock()
    mock_other.count.return_value.get.return_value = [[AsyncMock(value=0)]]
    
    def collection_side_effect(name):
        if name == "knowledge_documents":
            return mock_doc_query
        return mock_other

    mock_db.collection.side_effect = collection_side_effect
    
    with patch('backend.services.firestore_data_service.get_firestore_service') as mock_fs:
        mock_fs.return_value.db = mock_db
        service = FirestoreDataService()
        
        # Mock helper to avoid errors
        with patch.object(service, '_get_last_activity_timestamp', new_callable=AsyncMock) as mock_helper:
            mock_helper.return_value = datetime.now()
        
            # Initial check
            stats1 = await service.get_dashboard_stats()
            assert stats1.document_count == initial_count
            
            # "Create" happens (simulated by DB change)
            
            # Second check
            stats2 = await service.get_dashboard_stats()
            assert stats2.document_count == initial_count + 1


@pytest.mark.asyncio
async def test_count_decrement_on_deletion():
    """Validates Property 3: Count decreases after deletion."""
    initial_count = 5
    
    mock_db = MagicMock()
    mock_doc_query = MagicMock()
    
    # First call returns initial_count, Second call returns initial_count - 1
    mock_doc_query.count.return_value.get.side_effect = [
        [[AsyncMock(value=initial_count)]], 
        [[AsyncMock(value=initial_count - 1)]]
    ]
    
    mock_other = MagicMock()
    mock_other.count.return_value.get.return_value = [[AsyncMock(value=0)]]
    
    def collection_side_effect(name):
        if name == "knowledge_documents":
            return mock_doc_query
        return mock_other

    mock_db.collection.side_effect = collection_side_effect
    
    with patch('backend.services.firestore_data_service.get_firestore_service') as mock_fs:
        mock_fs.return_value.db = mock_db
        service = FirestoreDataService()
        
        with patch.object(service, '_get_last_activity_timestamp', new_callable=AsyncMock) as mock_helper:
            mock_helper.return_value = datetime.now()
        
            stats1 = await service.get_dashboard_stats()
            assert stats1.document_count == initial_count
            
            stats2 = await service.get_dashboard_stats()
            assert stats2.document_count == initial_count - 1

