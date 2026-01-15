import google.generativeai as genai
from typing import List, Dict, Optional
from config import settings
from .prompts import SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
    
    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        company_knowledge_base: Optional[str] = None
    ) -> str:
        """
        Generate a response using Gemini AI.
        
        Args:
            message: The user's message
            conversation_history: List of previous messages in format [{"role": "user"/"model", "content": "..."}]
            company_knowledge_base: Company-specific knowledge base content to inject into context
        
        Returns:
            AI-generated response string
        """
        try:
            # Build conversation context
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] in ["user", "CLIENT"] else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [msg["content"]]
                    })
            
            # Start chat with history
            chat = self.model.start_chat(history=chat_history)
            
            # Build enhanced prompt with knowledge base
            if not conversation_history:
                prompt = SYSTEM_PROMPT
                
                # Add company knowledge base if provided
                if company_knowledge_base:
                    prompt += f"\n\n## Company Knowledge Base\n\nYou have access to the following company-specific information. Use this information to provide accurate, relevant answers about the company's products, services, and policies:\n\n{company_knowledge_base}\n\n---\n\nIMPORTANT: When answering questions, prioritize information from the knowledge base above. If the answer is in the knowledge base, use it. If not, provide general assistance and offer to connect with a human agent.\n"
                
                prompt += f"\n\nUser: {message}"
            else:
                # For subsequent messages, just send the message
                # The knowledge base context is already in the first message
                prompt = message
            
            # Generate response
            response = chat.send_message(prompt)
            
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Would you like to speak with a human agent?"
    
    def build_conversation_context(self, messages: List[Dict]) -> List[Dict[str, str]]:
        """
        Build conversation context from message history.
        
        Args:
            messages: List of message objects from database
        
        Returns:
            Formatted conversation history for Gemini
        """
        context = []
        for msg in messages:
            role = "user" if msg.get("sender_type") == "CLIENT" else "model"
            context.append({
                "role": role,
                "content": msg.get("content", "")
            })
        return context


# Global instance
gemini_client = GeminiClient()
