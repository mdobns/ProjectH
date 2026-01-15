from typing import List
from sqlalchemy.orm import Session
from models.chat import Message, SenderType
from datetime import datetime


def create_message(
    db: Session,
    session_db_id: int,
    content: str,
    sender_type: SenderType
) -> Message:
    """
    Create and save a new message.
    
    Args:
        db: Database session
        session_db_id: Database ID of the chat session
        content: Message content
        sender_type: Type of sender (CLIENT, AI, ADMIN)
    
    Returns:
        Created Message object
    """
    message = Message(
        session_id=session_db_id,
        content=content,
        sender_type=sender_type,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_by_session(db: Session, session_db_id: int) -> List[Message]:
    """Get all messages for a session, ordered by creation time."""
    return db.query(Message).filter(
        Message.session_id == session_db_id
    ).order_by(Message.created_at).all()


def get_conversation_history(db: Session, session_db_id: int, limit: int = 10) -> List[dict]:
    """
    Get recent conversation history formatted for AI context.
    
    Args:
        db: Database session
        session_db_id: Database ID of the chat session
        limit: Maximum number of messages to retrieve
    
    Returns:
        List of messages in format [{"sender_type": "...", "content": "..."}]
    """
    messages = db.query(Message).filter(
        Message.session_id == session_db_id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    # Reverse to get chronological order
    messages = list(reversed(messages))
    
    return [
        {
            "sender_type": msg.sender_type.value,
            "content": msg.content,
        }
        for msg in messages
    ]
