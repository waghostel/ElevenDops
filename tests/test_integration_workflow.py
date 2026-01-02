import pytest
import asyncio
import uuid
from datetime import datetime
from backend.services.data_service import get_data_service
from backend.models.schemas import (
    KnowledgeDocumentCreate, SyncStatus,
    AgentResponse, AnswerStyle,
    PatientSessionResponse, ConversationDetailSchema, ConversationMessageSchema,
    AudioMetadata
)

# Mark as integration test
pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

async def test_complete_firestore_workflow():
    """
    14.1 Test complete workflow with Firestore
    - Create knowledge document
    - Verify persistence
    - Create agent linked to knowledge
    - Create patient session
    - Save conversation
    - Query conversation logs with filters
    - Verify dashboard stats
    """
    service = get_data_service()
    
    # 1. Create Knowledge Document
    print("Step 1: Create Knowledge Document")
    doc_create = KnowledgeDocumentCreate(
        doctor_id="doc_integration_test",
        disease_name="Integrationitis",
        tags=["post_care"],
        raw_content="# Treatment\nTake two integration tests and call me in the morning."
    )
    doc = await service.create_knowledge_document(doc_create)
    assert doc.knowledge_id is not None
    assert doc.sync_status == SyncStatus.PENDING
    print(f"Created document: {doc.knowledge_id}")

    # 2. Verify Persistence
    print("Step 2: Verify Persistence")
    fetched_doc = await service.get_knowledge_document(doc.knowledge_id)
    assert fetched_doc is not None
    assert fetched_doc.raw_content == doc_create.raw_content
    print("Document persisted correctly.")

    # 3. Create Agent Linked to Knowledge
    print("Step 3: Create Agent")
    agent_create = AgentResponse(
        agent_id=str(uuid.uuid4()),
        name="Integration Agent",
        knowledge_ids=[doc.knowledge_id], # Linking to knowledge
        voice_id="voice_123",
        answer_style=AnswerStyle.PROFESSIONAL,
        elevenlabs_agent_id="eleven_agent_123",
        doctor_id="doc_integration_test",
        created_at=datetime.now()
    )
    agent = await service.save_agent(agent_create)
    assert agent.agent_id == agent_create.agent_id
    print(f"Created agent: {agent.agent_id}")

    # 4. Create Patient Session
    print("Step 4: Create Patient Session")
    session_id = str(uuid.uuid4())
    session_create = PatientSessionResponse(
        session_id=session_id,
        patient_id="pat_integration_test",
        agent_id=agent.agent_id,
        signed_url="https://example.com/signed_url",
        created_at=datetime.now(),
        status="active"
    )
    session = await service.create_patient_session(session_create)
    assert session.session_id == session_id
    print(f"Created session: {session.session_id}")

    # 5. Save Conversation / Add Messages
    print("Step 5: Add Messages & Save Conversation")
    # Add messages to session
    msg1 = ConversationMessageSchema(role="patient", content="Hello, I have tests.", timestamp=datetime.now())
    msg2 = ConversationMessageSchema(role="agent", content="I see.", timestamp=datetime.now())
    
    await service.add_session_message(session_id, msg1)
    await service.add_session_message(session_id, msg2)
    
    msgs = await service.get_session_messages(session_id)
    assert len(msgs) == 2
    
    # Save completed conversation detail
    conv_detail = ConversationDetailSchema(
        conversation_id=session_id, # Using session_id as conv_id for simplicity 
        patient_id="pat_integration_test",
        agent_id=agent.agent_id,
        agent_name=agent.name,
        requires_attention=True,
        main_concerns=["Testing"],
        messages=msgs,
        answered_questions=[],
        unanswered_questions=["Why is docker down?"],
        duration_seconds=60,
        created_at=datetime.now()
    )
    saved_conv = await service.save_conversation(conv_detail)
    assert saved_conv.conversation_id == session_id
    print(f"Saved conversation: {saved_conv.conversation_id}")

    # 6. Query logs with filters
    print("Step 6: Query Logs")
    # Filter by patient
    logs = await service.get_conversation_logs(patient_id="pat_integration_test")
    assert len(logs) >= 1
    assert any(l.conversation_id == session_id for l in logs)
    
    # Filter by attention needed
    logs_attn = await service.get_conversation_logs(requires_attention_only=True)
    assert any(l.conversation_id == session_id for l in logs_attn)
    print("Logs queried successfully.")

    # 7. Verify Dashboard Stats
    print("Step 7: Dashboard Stats")
    stats = await service.get_dashboard_stats()
    assert stats.document_count >= 1 # At least our document
    assert stats.agent_count >= 1 # At least our agent
    print(f"Stats: {stats}")

    # Cleanup (Optional, but good for local dev repeated runs)
    await service.delete_knowledge_document(doc.knowledge_id)
    await service.delete_agent(agent.agent_id)
    # No delete for conversations/sessions in interface yet, but that's fine for MVP
    
    print("Workflow Test Completed Successfully.")

if __name__ == "__main__":
    # Allow running directly with python
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_complete_firestore_workflow())
