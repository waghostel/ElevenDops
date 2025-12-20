"""Analysis service for conversation processing."""

from typing import List, Tuple, Optional
import math
from backend.models.schemas import ConversationMessageSchema

class AnalysisService:
    """Service for analyzing conversation content."""
    
    def categorize_questions(
        self, messages: List[ConversationMessageSchema]
    ) -> Tuple[List[str], List[str]]:
        """Categorize questions into answered and unanswered.
        
        Args:
            messages: List of conversation messages in chronological order.
            
        Returns:
            Tuple containing (answered_questions, unanswered_questions) lists.
        """
        answered = []
        unanswered = []
        
        for i, msg in enumerate(messages):
            if msg.role != "patient":
                continue
                
            # Check if message contains a question mark
            if "?" in msg.content or "？" in msg.content:
                # Get the actual question content (simple implementation for now)
                # In a real system, might use NLP to extract questions
                question_text = msg.content
                
                # Check if followed by agent response
                is_answered = False
                if i + 1 < len(messages):
                    next_msg = messages[i + 1]
                    if next_msg.role == "agent":
                        is_answered = True
                
                if is_answered:
                    answered.append(question_text)
                else:
                    unanswered.append(question_text)
                    
        return answered, unanswered

    def extract_main_concerns(
        self, messages: List[ConversationMessageSchema]
    ) -> List[str]:
        """Extract main concerns from patient messages.
        
        Args:
            messages: List of conversation messages.
            
        Returns:
            List of main concern strings.
        """
        # MVP Implementation: Return first few patient messages or simple keyword extraction
        # Real implementation would use LLM or NLP
        concerns = []
        patient_msgs = [m for m in messages if m.role == "patient"]
        
        # Take up to 3 longest patient messages as "concerns" for now
        # Or just take the first message if it's substantial
        sorted_msgs = sorted(patient_msgs, key=lambda m: len(m.content), reverse=True)
        
        for msg in sorted_msgs[:3]:
            # Simple truncation for display
            content = msg.content
            if len(content) > 50:
                content = content[:47] + "..."
            concerns.append(content)
            
        return concerns

    def calculate_requires_attention(self, unanswered_questions: List[str]) -> bool:
        """Determine if conversation requires attention.
        
        Args:
            unanswered_questions: List of unanswered questions.
            
        Returns:
            True if there are unanswered questions.
        """
        return len(unanswered_questions) > 0

    def format_duration(self, duration_seconds: int) -> str:
        """Format duration in seconds to "Xm Ys" format.
        
        Args:
            duration_seconds: Duration in seconds.
            
        Returns:
            Formatted string.
        """
        if duration_seconds < 0:
            return "0m 0s"
            
        minutes = math.floor(duration_seconds / 60)
        seconds = duration_seconds % 60
        
        return f"{minutes}m {seconds}s"
