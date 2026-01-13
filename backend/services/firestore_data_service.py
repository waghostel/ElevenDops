import logging
from datetime import datetime
from typing import List, Optional
import uuid
import re

import google.cloud.firestore as firestore
from google.cloud.firestore import SERVER_TIMESTAMP
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import GoogleAPICallError, RetryError

from backend.services.data_service import DataServiceInterface
from backend.services.firestore_service import get_firestore_service
from backend.models.schemas import (
    DashboardStatsResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    PatientSessionResponse,
    SyncStatus,
    ConversationSummarySchema,
    ConversationDetailSchema,
    ConversationMessageSchema,
    AudioMetadata,
    AgentResponse,
    AnswerStyle,
    CustomTemplateCreate,
    CustomTemplateUpdate,
    CustomTemplateResponse,
)

logger = logging.getLogger(__name__)

# Collection names as constants
KNOWLEDGE_DOCUMENTS = "knowledge_documents"
AUDIO_FILES = "audio_files"
AGENTS = "agents"
CONVERSATIONS = "conversations"
CONVERSATIONS = "conversations"
PATIENT_SESSIONS = "patient_sessions"
CUSTOM_TEMPLATES = "custom_templates"


class FirestoreDataService(DataServiceInterface):
    """Firestore implementation of the data service interface."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._firestore = get_firestore_service()
        self._db = self._firestore.db
        self._initialized = True
        logger.info("FirestoreDataService initialized")

    # ==================== Helper Methods ====================
    
    def _doc_to_knowledge_response(self, doc_dict: dict) -> KnowledgeDocumentResponse:
        """Convert Firestore document to KnowledgeDocumentResponse."""
        return KnowledgeDocumentResponse(
            knowledge_id=doc_dict["knowledge_id"],
            doctor_id=doc_dict["doctor_id"],
            disease_name=doc_dict["disease_name"],
            tags=doc_dict.get("tags", []),
            raw_content=doc_dict["raw_content"],
            sync_status=SyncStatus(doc_dict["sync_status"]),
            elevenlabs_document_id=doc_dict.get("elevenlabs_document_id"),
            structured_sections=doc_dict.get("structured_sections"),
            created_at=doc_dict["created_at"],
            sync_error_message=doc_dict.get("sync_error_message"),
            last_sync_attempt=doc_dict.get("last_sync_attempt"),
            sync_retry_count=doc_dict.get("sync_retry_count", 0),
            modified_at=doc_dict.get("modified_at"),
        )

    def _doc_to_audio_metadata(self, doc_dict: dict) -> AudioMetadata:
        """Convert Firestore document to AudioMetadata."""
        return AudioMetadata(
            audio_id=doc_dict["audio_id"],
            knowledge_id=doc_dict["knowledge_id"],
            voice_id=doc_dict["voice_id"],
            script=doc_dict["script"],
            audio_url=doc_dict["audio_url"],
            duration_seconds=doc_dict.get("duration_seconds"),
            created_at=doc_dict["created_at"],
            doctor_id=doc_dict.get("doctor_id", "default_doctor"),
            name=doc_dict.get("name", ""),
            description=doc_dict.get("description", ""),
        )

    def _doc_to_agent_response(self, doc_dict: dict) -> AgentResponse:
        """Convert Firestore document to AgentResponse."""
        return AgentResponse(
            agent_id=doc_dict["agent_id"],
            name=doc_dict["name"],
            knowledge_ids=doc_dict.get("knowledge_ids", []),
            voice_id=doc_dict["voice_id"],
            answer_style=AnswerStyle(doc_dict["answer_style"]),
            elevenlabs_agent_id=doc_dict["elevenlabs_agent_id"],
            doctor_id=doc_dict["doctor_id"],
            created_at=doc_dict["created_at"],
            languages=doc_dict.get("languages", ["zh"]),
        )
    
    def _doc_to_patient_session_response(self, doc_dict: dict) -> PatientSessionResponse:
        """Convert Firestore document to PatientSessionResponse."""
        return PatientSessionResponse(
            session_id=doc_dict["session_id"],
            patient_id=doc_dict["patient_id"],
            agent_id=doc_dict["agent_id"],
            signed_url=doc_dict["signed_url"],
            created_at=doc_dict["created_at"],
        )

    def _doc_to_conversation_detail(self, doc_dict: dict) -> ConversationDetailSchema:
        """Convert Firestore document to ConversationDetailSchema."""
        messages = [
            ConversationMessageSchema(
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"],
                is_answered=m.get("is_answered"),
                audio_data=m.get("audio_data"),
            )
            for m in doc_dict.get("messages", [])
        ]
        return ConversationDetailSchema(
            conversation_id=doc_dict["conversation_id"],
            patient_id=doc_dict["patient_id"],
            agent_id=doc_dict["agent_id"],
            agent_name=doc_dict["agent_name"],
            requires_attention=doc_dict.get("requires_attention", False),
            main_concerns=doc_dict.get("main_concerns", []),
            messages=messages,
            answered_questions=doc_dict.get("answered_questions", []),
            unanswered_questions=doc_dict.get("unanswered_questions", []),
            duration_seconds=doc_dict.get("duration_seconds", 0),
            created_at=doc_dict["created_at"],
        )
        
    def _parse_structured_sections(self, content: str) -> dict:
        """Parse markdown content into structured sections based on headers."""
        sections = {}
        matches = list(re.finditer(r'(^|\n)(?P<level>\s*#{1,6})\s(?P<title>.*)', content))
        if not matches:
             if content.strip():
                 sections["content"] = content
             return sections

        for i, match in enumerate(matches):
            current_start = match.start()
            if i == 0:
                intro = content[0:current_start].strip()
                if intro:
                    sections["Introduction"] = intro

            header_title = match.group("title").strip()
            match_end = match.end()
            
            if i + 1 < len(matches):
                next_start = matches[i+1].start()
                section_content = content[match_end:next_start].strip()
            else:
                section_content = content[match_end:].strip()
            
            if section_content:
                sections[header_title] = section_content
        return sections

    # ==================== Dashboard ====================
    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Get dashboard statistics using collection counts."""
        try:
            # Use aggregation queries for counts
            doc_count_query = self._db.collection(KNOWLEDGE_DOCUMENTS).count()
            agent_count_query = self._db.collection(AGENTS).count()
            audio_count_query = self._db.collection(AUDIO_FILES).count()
            
            # Execute queries
            # Note: In a real production scenario, we might want to run these concurrently
            # using asyncio.gather if the client library supports async aggregation execution well.
            # standard google-cloud-firestore uses sync methods for count().get() usually, 
            # but wrapping in executor or just calling sequentially is fine for MVP scale.
            # If using async client, await properly. 
            
            # Assuming sync client wrapped in async service or async client usage:
            # The current codebase seems to use standard sync calls in async defs without await on .get() 
            # for count aggregation in the existing snippet, which might be blocking.
            # However, `get()` on generation returns an object with `value`.
            
            doc_snapshot = doc_count_query.get()
            agent_snapshot = agent_count_query.get()
            audio_snapshot = audio_count_query.get()
            
            doc_count = doc_snapshot[0][0].value
            agent_count = agent_snapshot[0][0].value
            audio_count = audio_snapshot[0][0].value
            
            # Calculate last_activity across all collections
            last_activity = await self._get_last_activity_timestamp()
                
            return DashboardStatsResponse(
                document_count=doc_count,
                agent_count=agent_count,
                audio_count=audio_count,
                last_activity=last_activity,
            )
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            # Fallback
            return DashboardStatsResponse(
                document_count=0,
                agent_count=0,
                audio_count=0,
                last_activity=datetime.now(),
            )

    async def _get_last_activity_timestamp(self) -> datetime:
        """Get the most recent created_at timestamp across all collections."""
        collections = [KNOWLEDGE_DOCUMENTS, AGENTS, AUDIO_FILES, CONVERSATIONS]
        latest = None
        
        for collection_name in collections:
            try:
                # Get the most recent document from this collection
                docs = (
                    self._db.collection(collection_name)
                    .order_by("created_at", direction=firestore.Query.DESCENDING)
                    .limit(1)
                    .stream()
                )
                
                for doc in docs:
                    timestamp = doc.to_dict().get("created_at")
                    # Handle Firestore Timestamp objects or datetime strings
                    if timestamp:
                        # If it's a string, try to parse it (though models usually enforce datetime/Timestamp)
                        if isinstance(timestamp, str):
                            try:
                                timestamp = datetime.fromisoformat(timestamp)
                            except ValueError:
                                continue
                                
                        if latest is None or timestamp > latest:
                            latest = timestamp
            except Exception as e:
                logger.warning(f"Failed to check last activity for {collection_name}: {e}")
                continue
        
        return latest if latest else datetime.now()

    # ==================== Knowledge Documents ====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def create_knowledge_document(
        self, doc: KnowledgeDocumentCreate
    ) -> KnowledgeDocumentResponse:
        try:
            knowledge_id = str(uuid.uuid4())
            structured = self._parse_structured_sections(doc.raw_content)
            
            doc_data = {
                "knowledge_id": knowledge_id,
                "doctor_id": doc.doctor_id,
                "disease_name": doc.disease_name,
                "tags": doc.tags,
                "raw_content": doc.raw_content,
                "sync_status": SyncStatus.PENDING.value,
                "elevenlabs_document_id": None,
                "structured_sections": structured,
                "created_at": SERVER_TIMESTAMP,
            }
            
            self._db.collection(KNOWLEDGE_DOCUMENTS).document(knowledge_id).set(doc_data)
            
            # Approximate created_at for return
            doc_data["created_at"] = datetime.now()
            
            return self._doc_to_knowledge_response(doc_data)
        except Exception as e:
            logger.error(f"Failed to create knowledge document: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def update_knowledge_document(
        self, knowledge_id: str, update_data: KnowledgeDocumentUpdate
    ) -> Optional[KnowledgeDocumentResponse]:
        try:
            doc_ref = self._db.collection(KNOWLEDGE_DOCUMENTS).document(knowledge_id)
            doc_snap = doc_ref.get()
            if not doc_snap.exists:
                return None
            
            updates = update_data.model_dump(exclude_unset=True)
            if not updates:
                return self._doc_to_knowledge_response(doc_snap.to_dict())
            
            # Set modified_at
            now = datetime.now()
            updates["modified_at"] = now
            
            doc_ref.update(updates)
            
            # Get updated
            updated_snap = doc_ref.get()
            return self._doc_to_knowledge_response(updated_snap.to_dict())
        except Exception as e:
            logger.error(f"Failed to update knowledge document {knowledge_id}: {e}")
            raise

    async def get_knowledge_documents(
        self, doctor_id: Optional[str] = None
    ) -> List[KnowledgeDocumentResponse]:
        try:
            ref = self._db.collection(KNOWLEDGE_DOCUMENTS)
            if doctor_id:
                ref = ref.where(filter=firestore.FieldFilter("doctor_id", "==", doctor_id))
            
            docs = ref.stream()
            return [self._doc_to_knowledge_response(d.to_dict()) for d in docs]
        except Exception as e:
            logger.error(f"Failed to get knowledge documents: {e}")
            return []

    async def get_knowledge_document(
        self, knowledge_id: str
    ) -> Optional[KnowledgeDocumentResponse]:
        try:
            doc = self._db.collection(KNOWLEDGE_DOCUMENTS).document(knowledge_id).get()
            if not doc.exists:
                return None
            return self._doc_to_knowledge_response(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get knowledge document {knowledge_id}: {e}")
            return None

    async def update_knowledge_sync_status(
        self, 
        knowledge_id: str, 
        status: SyncStatus, 
        elevenlabs_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        try:
            ref = self._db.collection(KNOWLEDGE_DOCUMENTS).document(knowledge_id)
            updates = {
                "sync_status": status.value,
                "last_sync_attempt": firestore.SERVER_TIMESTAMP
            }
            if elevenlabs_id:
                updates["elevenlabs_document_id"] = elevenlabs_id
            
            if status == SyncStatus.SYNCING:
                updates["sync_retry_count"] = firestore.Increment(1)
            
            if error_message:
                updates["sync_error_message"] = error_message
            elif status == SyncStatus.COMPLETED or status == SyncStatus.PENDING:
                updates["sync_error_message"] = None
                if status == SyncStatus.PENDING:
                     updates["sync_retry_count"] = 0

            try:
                ref.update(updates)
                return True
            except Exception:
                return False
        except Exception as e:
            logger.error(f"Failed to update sync status {knowledge_id}: {e}")
            return False

    async def delete_knowledge_document(self, knowledge_id: str) -> bool:
        try:
            # Check if exists first to return correct boolean
            doc_ref = self._db.collection(KNOWLEDGE_DOCUMENTS).document(knowledge_id)
            if not doc_ref.get().exists:
                return False
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete knowledge document {knowledge_id}: {e}")
            return False

    # ==================== Audio Files ====================
    async def save_audio_metadata(self, audio: AudioMetadata) -> AudioMetadata:
        try:
            doc_data = audio.model_dump()
            self._db.collection(AUDIO_FILES).document(audio.audio_id).set(doc_data)
            return audio
        except Exception as e:
            logger.error(f"Failed to save audio metadata: {e}")
            raise

    async def get_audio_files(
        self, knowledge_id: Optional[str] = None, doctor_id: Optional[str] = None
    ) -> List[AudioMetadata]:
        try:
            ref = self._db.collection(AUDIO_FILES)
            if knowledge_id:
                ref = ref.where(filter=firestore.FieldFilter("knowledge_id", "==", knowledge_id))
            if doctor_id:
                ref = ref.where(filter=firestore.FieldFilter("doctor_id", "==", doctor_id))
            
            docs = ref.stream()
            return [self._doc_to_audio_metadata(d.to_dict()) for d in docs]
        except Exception as e:
            logger.error(f"Failed to get audio files: {e}")
            return []

    async def get_audio_file(self, audio_id: str) -> Optional[AudioMetadata]:
        try:
            doc = self._db.collection(AUDIO_FILES).document(audio_id).get()
            if not doc.exists:
                return None
            return self._doc_to_audio_metadata(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get audio file {audio_id}: {e}")
            return None

    async def delete_audio_file(self, audio_id: str) -> bool:
        try:
            doc_ref = self._db.collection(AUDIO_FILES).document(audio_id)
            if not doc_ref.get().exists:
                return False
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete audio file {audio_id}: {e}")
            return False

    # ==================== Agents ====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def save_agent(self, agent: AgentResponse) -> AgentResponse:
        try:
            doc_data = agent.model_dump()
            doc_data["answer_style"] = agent.answer_style.value
            
            self._db.collection(AGENTS).document(agent.agent_id).set(doc_data)
            return agent
        except Exception as e:
            logger.error(f"Failed to save agent: {e}")
            raise

    async def get_agents(
        self, doctor_id: Optional[str] = None
    ) -> List[AgentResponse]:
        try:
            ref = self._db.collection(AGENTS)
            if doctor_id:
                ref = ref.where(filter=firestore.FieldFilter("doctor_id", "==", doctor_id))
            
            docs = ref.stream()
            return [self._doc_to_agent_response(d.to_dict()) for d in docs]
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            return []

    async def get_agent(self, agent_id: str) -> Optional[AgentResponse]:
        try:
            doc = self._db.collection(AGENTS).document(agent_id).get()
            if not doc.exists:
                return None
            return self._doc_to_agent_response(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None

    async def delete_agent(self, agent_id: str) -> bool:
        try:
            doc_ref = self._db.collection(AGENTS).document(agent_id)
            if not doc_ref.get().exists:
                return False
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False

    # ==================== Patient Sessions ====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def create_patient_session(
        self, session: PatientSessionResponse
    ) -> PatientSessionResponse:
        try:
            doc_data = session.model_dump()
            doc_data["messages"] = [] 
            self._db.collection(PATIENT_SESSIONS).document(session.session_id).set(doc_data)
            return session
        except Exception as e:
            logger.error(f"Failed to create patient session: {e}")
            raise

    async def get_patient_session(
        self, session_id: str
    ) -> Optional[PatientSessionResponse]:
        try:
            doc = self._db.collection(PATIENT_SESSIONS).document(session_id).get()
            if not doc.exists:
                return None
            return self._doc_to_patient_session_response(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get patient session {session_id}: {e}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def add_session_message(
        self, session_id: str, message: ConversationMessageSchema
    ) -> None:
        try:
            ref = self._db.collection(PATIENT_SESSIONS).document(session_id)
            message_dict = message.model_dump()
            ref.update({
                "messages": firestore.ArrayUnion([message_dict])
            })
        except Exception as e:
            logger.error(f"Failed to add session message {session_id}: {e}")
            raise

    async def get_session_messages(
        self, session_id: str
    ) -> List[ConversationMessageSchema]:
        try:
            doc = self._db.collection(PATIENT_SESSIONS).document(session_id).get()
            if not doc.exists:
                return []
            
            messages = doc.to_dict().get("messages", [])
            return [ConversationMessageSchema(**m) for m in messages]
        except Exception as e:
            logger.error(f"Failed to get session messages {session_id}: {e}")
            return []

    # ==================== Conversations ====================
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((GoogleAPICallError, RetryError))
    )
    async def save_conversation(
        self, conversation: ConversationDetailSchema
    ) -> ConversationDetailSchema:
        try:
            doc_data = conversation.model_dump()
            self._db.collection(CONVERSATIONS).document(conversation.conversation_id).set(doc_data)
            return conversation
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            raise

    async def get_conversation_logs(
        self,
        patient_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        requires_attention_only: bool = False,
    ) -> List[ConversationSummarySchema]:
        try:
            ref = self._db.collection(CONVERSATIONS)
            
            if requires_attention_only:
                 ref = ref.where(filter=firestore.FieldFilter("requires_attention", "==", True))
            
            ref = ref.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            if start_date:
                ref = ref.where(filter=firestore.FieldFilter("created_at", ">=", start_date))
            if end_date:
                ref = ref.where(filter=firestore.FieldFilter("created_at", "<=", end_date))
                
            docs = ref.stream()
            
            results = []
            for d in docs:
                data = d.to_dict()
                
                if patient_id and patient_id.lower() not in data.get("patient_id", "").lower():
                    continue

                summary = ConversationSummarySchema(
                    conversation_id=data["conversation_id"],
                    patient_id=data["patient_id"],
                    agent_id=data["agent_id"],
                    agent_name=data["agent_name"],
                    requires_attention=data.get("requires_attention", False),
                    main_concerns=data.get("main_concerns", []),
                    total_messages=len(data.get("messages", [])),
                    answered_count=len(data.get("answered_questions", [])),
                    unanswered_count=len(data.get("unanswered_questions", [])),
                    duration_seconds=data.get("duration_seconds", 0),
                    created_at=data["created_at"],
                )
                results.append(summary)
            
            return results
        except Exception as e:
            logger.error(f"Failed to get conversation logs: {e}")
            return []

    async def get_conversation_detail(
        self, conversation_id: str
    ) -> Optional[ConversationDetailSchema]:
        try:
            doc = self._db.collection(CONVERSATIONS).document(conversation_id).get()
            if not doc.exists:
                return None
            return self._doc_to_conversation_detail(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get conversation detail {conversation_id}: {e}")
            return None

    async def get_conversation_count(self) -> int:
        """Get total number of conversations."""
        try:
            return self._db.collection(CONVERSATIONS).count().get()[0][0].value
        except Exception as e:
            logger.error(f"Failed to get conversation count: {e}")
            return 0

    async def get_average_duration(self) -> float:
        """Get average conversation duration in seconds."""
        try:
            # Note: Firestore aggregation for AVG might be available but fetching fields is safe MVP
            docs = self._db.collection(CONVERSATIONS).select(["duration_seconds"]).stream()
            durations = []
            for d in docs:
                val = d.to_dict().get("duration_seconds", 0)
                if val > 0:
                    durations.append(val)
            
            if not durations:
                return 0.0
            return sum(durations) / len(durations)
        except Exception as e:
            logger.error(f"Failed to get average duration: {e}")
            return 0.0

    async def get_attention_percentage(self) -> float:
        """Get percentage of conversations requiring attention."""
        try:
            total_req = self._db.collection(CONVERSATIONS).count()
            attn_req = self._db.collection(CONVERSATIONS).where(filter=firestore.FieldFilter("requires_attention", "==", True)).count()
            
            total_snap = total_req.get()
            attn_snap = attn_req.get()
            
            total = total_snap[0][0].value
            if total == 0:
                return 0.0
            
            attn = attn_snap[0][0].value
            return (attn / total) * 100.0
        except Exception as e:
            logger.error(f"Failed to get attention percentage: {e}")
            return 0.0

    # ==================== Custom Templates ====================
    def _doc_to_custom_template_response(self, doc_dict: dict) -> CustomTemplateResponse:
        """Convert Firestore document to CustomTemplateResponse."""
        return CustomTemplateResponse(
            template_id=doc_dict["template_id"],
            display_name=doc_dict["display_name"],
            description=doc_dict["description"],
            category=doc_dict["category"],
            preview=doc_dict.get("preview", doc_dict["content"][:200]),
            content=doc_dict["content"],
            created_by=doc_dict.get("created_by"),
            created_at=doc_dict["created_at"],
        )

    async def create_custom_template(
        self, template: CustomTemplateCreate, user_id: str = "default_user"
    ) -> CustomTemplateResponse:
        """Create a new custom template."""
        try:
            template_id = str(uuid.uuid4())
            now = datetime.now()
            
            doc_data = {
                "template_id": template_id,
                "display_name": template.display_name,
                "description": template.description,
                "content": template.content,
                "category": "custom",
                "preview": template.content[:200],
                "created_by": user_id,
                "created_at": now,  # We use local time for immediate return, Firestore will store Timestamp
            }
            
            # Using set with merge=True concept or specific ID
            self._db.collection(CUSTOM_TEMPLATES).document(template_id).set(doc_data)
            
            return self._doc_to_custom_template_response(doc_data)
        except Exception as e:
            logger.error(f"Failed to create custom template: {e}")
            raise

    async def get_custom_templates(self, user_id: Optional[str] = None) -> List[CustomTemplateResponse]:
        """Get all custom templates, optionally filtered by user."""
        try:
            ref = self._db.collection(CUSTOM_TEMPLATES)
            if user_id:
                ref = ref.where(filter=firestore.FieldFilter("created_by", "==", user_id))
            
            # Order by created_at desc
            ref = ref.order_by("created_at", direction=firestore.Query.DESCENDING)
            
            docs = ref.stream()
            return [self._doc_to_custom_template_response(d.to_dict()) for d in docs]
        except Exception as e:
            logger.error(f"Failed to get custom templates: {e}")
            return []

    async def get_custom_template(self, template_id: str) -> Optional[CustomTemplateResponse]:
        """Get a specific custom template."""
        try:
            doc = self._db.collection(CUSTOM_TEMPLATES).document(template_id).get()
            if not doc.exists:
                return None
            return self._doc_to_custom_template_response(doc.to_dict())
        except Exception as e:
            logger.error(f"Failed to get custom template {template_id}: {e}")
            return None

    async def update_custom_template(
        self, template_id: str, update_data: CustomTemplateUpdate
    ) -> Optional[CustomTemplateResponse]:
        """Update a custom template."""
        try:
            doc_ref = self._db.collection(CUSTOM_TEMPLATES).document(template_id)
            doc_snap = doc_ref.get()
            if not doc_snap.exists:
                return None
            
            updates = update_data.model_dump(exclude_unset=True)
            if not updates:
                return self._doc_to_custom_template_response(doc_snap.to_dict())
            
            # Update preview if content changed
            if "content" in updates:
                updates["preview"] = updates["content"][:200]
            
            doc_ref.update(updates)
            
            updated_snap = doc_ref.get()
            return self._doc_to_custom_template_response(updated_snap.to_dict())
        except Exception as e:
            logger.error(f"Failed to update custom template {template_id}: {e}")
            return None

    async def delete_custom_template(self, template_id: str) -> bool:
        """Delete a custom template."""
        try:
            doc_ref = self._db.collection(CUSTOM_TEMPLATES).document(template_id)
            if not doc_ref.get().exists:
                return False
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete custom template {template_id}: {e}")
            return False
