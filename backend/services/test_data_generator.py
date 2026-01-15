"""
Test Data Generator Component for Postman Testing

Generates realistic test data for API requests.
Supports knowledge documents, audio requests, agent configs, patient sessions, and templates.

Requirements: 15.3
"""

import uuid
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TestDataGenerator:
    """
    Generates realistic test data for API requests.
    
    Supports:
    - Knowledge document generation
    - Audio request generation
    - Agent configuration generation
    - Patient session generation
    - Template generation
    """
    
    # Disease names for realistic data
    DISEASE_NAMES = [
        "Diabetes", "Hypertension", "Asthma", "COPD", "Heart Disease",
        "Arthritis", "Osteoporosis", "Thyroid Disease", "Kidney Disease",
        "Liver Disease", "Cancer", "Stroke", "Dementia", "Depression",
    ]
    
    # Tags for categorization
    TAGS = [
        "chronic", "acute", "preventive", "treatment", "medication",
        "surgery", "therapy", "diagnosis", "management", "education",
    ]
    
    # Voice IDs
    VOICE_IDS = [
        "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "EXAVITQu4vr4xnSDxMaL",  # Bella
        "TxGEqnHWrfWFTfGW9XjX",  # Antoni
        "VR6AewLBTwakI2AVs33w",  # Arnold
        "pFZP5JQG7iQjIQuC4Iy4",  # Adam
    ]
    
    # System prompts
    SYSTEM_PROMPTS = [
        "professional", "friendly", "clinical", "educational", "supportive",
    ]
    
    @staticmethod
    def generate_knowledge_document(
        doctor_id: str = "test_doctor_001",
        include_structured_sections: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate test knowledge document.
        
        Args:
            doctor_id: Doctor ID for the document
            include_structured_sections: Whether to include structured sections
            
        Returns:
            Knowledge document data
        """
        disease_name = random.choice(TestDataGenerator.DISEASE_NAMES)
        tags = random.sample(TestDataGenerator.TAGS, k=random.randint(2, 4))
        
        raw_content = f"""# {disease_name} Patient Education

## Overview
{disease_name} is a common medical condition that affects many patients. This guide provides comprehensive information about the disease, its symptoms, and treatment options.

## Symptoms
- Symptom 1: Description of symptom 1
- Symptom 2: Description of symptom 2
- Symptom 3: Description of symptom 3

## Causes
The main causes of {disease_name} include:
1. Genetic factors
2. Environmental factors
3. Lifestyle factors

## Treatment Options
### Medication
- Medication 1: Description and dosage
- Medication 2: Description and dosage

### Lifestyle Changes
- Change 1: Description
- Change 2: Description

## Prevention
To prevent {disease_name}:
- Prevention tip 1
- Prevention tip 2
- Prevention tip 3

## When to Seek Help
Contact your doctor if you experience:
- Severe symptoms
- Persistent symptoms
- New symptoms
"""
        
        document = {
            "disease_name": disease_name,
            "tags": tags,
            "raw_content": raw_content,
            "doctor_id": doctor_id,
            "name": f"Test_{disease_name}_{uuid.uuid4().hex[:8]}",
            "description": f"Test knowledge document for {disease_name}",
        }
        
        if include_structured_sections:
            document["structured_sections"] = [
                {"title": "Overview", "content": "Overview content"},
                {"title": "Symptoms", "content": "Symptoms content"},
                {"title": "Treatment Options", "content": "Treatment content"},
            ]
        
        logger.debug(f"Generated knowledge document: {disease_name}")
        return document
    
    @staticmethod
    def generate_audio_request(
        knowledge_id: str,
        doctor_id: str = "test_doctor_001",
    ) -> Dict[str, Any]:
        """
        Generate audio generation request.
        
        Args:
            knowledge_id: Knowledge document ID
            doctor_id: Doctor ID
            
        Returns:
            Audio request data
        """
        script = """Welcome to today's health education session. 
        Today we'll discuss important information about managing your health condition.
        Please listen carefully and feel free to ask questions."""
        
        request = {
            "script": script,
            "voice_id": random.choice(TestDataGenerator.VOICE_IDS),
            "knowledge_id": knowledge_id,
            "doctor_id": doctor_id,
            "name": f"Test_Audio_{uuid.uuid4().hex[:8]}",
            "description": "Test audio generation",
            "language": "en-US",
            "model_id": "eleven_monolingual_v1",
        }
        
        logger.debug(f"Generated audio request for knowledge: {knowledge_id}")
        return request
    
    @staticmethod
    def generate_agent_config(
        knowledge_ids: Optional[List[str]] = None,
        doctor_id: str = "test_doctor_001",
    ) -> Dict[str, Any]:
        """
        Generate agent configuration.
        
        Args:
            knowledge_ids: List of knowledge document IDs
            doctor_id: Doctor ID
            
        Returns:
            Agent configuration data
        """
        if knowledge_ids is None:
            knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in range(random.randint(1, 3))]
        
        config = {
            "name": f"Test_Agent_{uuid.uuid4().hex[:8]}",
            "description": "Test AI agent for patient education",
            "knowledge_ids": knowledge_ids,
            "doctor_id": doctor_id,
            "system_prompt_style": random.choice(TestDataGenerator.SYSTEM_PROMPTS),
            "model": "eleven_turbo_v2",
            "voice_id": random.choice(TestDataGenerator.VOICE_IDS),
            "language": "en-US",
            "temperature": round(random.uniform(0.5, 1.0), 2),
            "max_tokens": random.choice([256, 512, 1024]),
            "enabled": True,
        }
        
        logger.debug(f"Generated agent config with {len(knowledge_ids)} knowledge documents")
        return config
    
    @staticmethod
    def generate_patient_session(
        agent_id: str,
        patient_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate patient session data.
        
        Args:
            agent_id: Agent ID for the session
            patient_id: Patient ID (generated if not provided)
            
        Returns:
            Patient session data
        """
        if patient_id is None:
            patient_id = f"patient_{uuid.uuid4().hex[:16]}"
        
        session = {
            "agent_id": agent_id,
            "patient_id": patient_id,
            "chat_mode": random.choice(["streaming", "non-streaming"]),
            "language": "en-US",
            "metadata": {
                "session_type": "test",
                "created_by": "test_automation",
            },
        }
        
        logger.debug(f"Generated patient session for agent: {agent_id}")
        return session
    
    @staticmethod
    def generate_patient_message(
        session_id: str,
        message_type: str = "text",
    ) -> Dict[str, Any]:
        """
        Generate patient message.
        
        Args:
            session_id: Session ID
            message_type: Message type (text, audio)
            
        Returns:
            Patient message data
        """
        sample_messages = [
            "What are the symptoms of this condition?",
            "How should I take my medication?",
            "What lifestyle changes should I make?",
            "When should I see a doctor?",
            "Are there any side effects?",
            "Can this condition be cured?",
            "What is the prognosis?",
            "How can I prevent complications?",
        ]
        
        message = {
            "session_id": session_id,
            "message": random.choice(sample_messages),
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        logger.debug(f"Generated patient message for session: {session_id}")
        return message
    
    @staticmethod
    def generate_template(
        doctor_id: str = "test_doctor_001",
        is_system: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate prompt template.
        
        Args:
            doctor_id: Doctor ID
            is_system: Whether this is a system template
            
        Returns:
            Template data
        """
        template_content = """You are a helpful medical education assistant. 
Your role is to provide accurate, evidence-based health information to patients.
Always encourage patients to consult with their healthcare provider for personalized advice.

Context: {context}
Patient Question: {question}

Provide a clear, compassionate response that:
1. Addresses the patient's question directly
2. Provides evidence-based information
3. Encourages professional medical consultation when appropriate
4. Uses simple, understandable language"""
        
        template = {
            "name": f"Test_Template_{uuid.uuid4().hex[:8]}",
            "description": "Test prompt template",
            "content": template_content,
            "doctor_id": doctor_id if not is_system else None,
            "is_system": is_system,
            "variables": ["context", "question"],
            "style": random.choice(TestDataGenerator.SYSTEM_PROMPTS),
        }
        
        logger.debug(f"Generated template: {template['name']}")
        return template
    
    @staticmethod
    def generate_conversation(
        session_id: str,
        message_count: int = 3,
    ) -> Dict[str, Any]:
        """
        Generate conversation data.
        
        Args:
            session_id: Session ID
            message_count: Number of messages in conversation
            
        Returns:
            Conversation data
        """
        messages = []
        for i in range(message_count):
            messages.append({
                "role": "patient" if i % 2 == 0 else "assistant",
                "content": f"Message {i+1} content",
                "timestamp": (datetime.utcnow() - timedelta(minutes=message_count-i)).isoformat(),
            })
        
        conversation = {
            "session_id": session_id,
            "messages": messages,
            "started_at": (datetime.utcnow() - timedelta(minutes=message_count)).isoformat(),
            "ended_at": datetime.utcnow().isoformat(),
            "duration_seconds": message_count * 60,
            "message_count": message_count,
            "analysis": {
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "topics": ["health", "medication", "symptoms"],
                "requires_attention": random.choice([True, False]),
            },
        }
        
        logger.debug(f"Generated conversation with {message_count} messages")
        return conversation
    
    @staticmethod
    def generate_batch_knowledge_documents(
        count: int = 5,
        doctor_id: str = "test_doctor_001",
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple knowledge documents.
        
        Args:
            count: Number of documents to generate
            doctor_id: Doctor ID
            
        Returns:
            List of knowledge documents
        """
        documents = [
            TestDataGenerator.generate_knowledge_document(doctor_id)
            for _ in range(count)
        ]
        
        logger.debug(f"Generated batch of {count} knowledge documents")
        return documents
    
    @staticmethod
    def generate_batch_agents(
        count: int = 3,
        knowledge_ids: Optional[List[str]] = None,
        doctor_id: str = "test_doctor_001",
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple agent configurations.
        
        Args:
            count: Number of agents to generate
            knowledge_ids: List of knowledge IDs to use
            doctor_id: Doctor ID
            
        Returns:
            List of agent configurations
        """
        agents = [
            TestDataGenerator.generate_agent_config(knowledge_ids, doctor_id)
            for _ in range(count)
        ]
        
        logger.debug(f"Generated batch of {count} agent configurations")
        return agents
    
    @staticmethod
    def generate_batch_templates(
        count: int = 3,
        doctor_id: str = "test_doctor_001",
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple templates.
        
        Args:
            count: Number of templates to generate
            doctor_id: Doctor ID
            
        Returns:
            List of templates
        """
        templates = [
            TestDataGenerator.generate_template(doctor_id)
            for _ in range(count)
        ]
        
        logger.debug(f"Generated batch of {count} templates")
        return templates
    
    @staticmethod
    def generate_unique_id(prefix: str = "test") -> str:
        """
        Generate unique ID for test data.
        
        Args:
            prefix: ID prefix
            
        Returns:
            Unique ID
        """
        return f"{prefix}_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_test_data_set() -> Dict[str, Any]:
        """
        Generate complete test data set.
        
        Returns:
            Dictionary with all test data
        """
        doctor_id = TestDataGenerator.generate_unique_id("doctor")
        
        # Generate knowledge documents
        knowledge_docs = TestDataGenerator.generate_batch_knowledge_documents(3, doctor_id)
        knowledge_ids = [f"knowledge_{uuid.uuid4().hex[:16]}" for _ in knowledge_docs]
        
        # Generate agents
        agents = TestDataGenerator.generate_batch_agents(2, knowledge_ids, doctor_id)
        agent_ids = [f"agent_{uuid.uuid4().hex[:16]}" for _ in agents]
        
        # Generate sessions
        sessions = [
            TestDataGenerator.generate_patient_session(agent_ids[0])
            for _ in range(2)
        ]
        session_ids = [f"session_{uuid.uuid4().hex[:16]}" for _ in sessions]
        
        # Generate audio requests
        audio_requests = [
            TestDataGenerator.generate_audio_request(knowledge_ids[0], doctor_id)
            for _ in range(2)
        ]
        
        # Generate templates
        templates = TestDataGenerator.generate_batch_templates(2, doctor_id)
        
        test_data = {
            "doctor_id": doctor_id,
            "knowledge_documents": knowledge_docs,
            "knowledge_ids": knowledge_ids,
            "agents": agents,
            "agent_ids": agent_ids,
            "sessions": sessions,
            "session_ids": session_ids,
            "audio_requests": audio_requests,
            "templates": templates,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        logger.info("Generated complete test data set")
        return test_data


__all__ = ["TestDataGenerator"]
