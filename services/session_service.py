from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.chat import ChatSession, Message, ClientInfo, SessionState, SenderType
from schemas.chat import ClientInfoCreate, MessageCreate
import uuid
from datetime import datetime


def create_session(db: Session, client_info_data: ClientInfoCreate) -> ChatSession:
    """
    Create a new chat session with client information.
    
    Args:
        db: Database session
        client_info_data: Client information (name, email, phone)
    
    Returns:
        Created ChatSession object
    """
    # Create client info
    client_info = ClientInfo(
        name=client_info_data.name,
        email=client_info_data.email,
        phone=client_info_data.phone,
    )
    db.add(client_info)
    db.flush()  # Get the client_info.id
    
    # Create chat session
    session = ChatSession(
        session_id=str(uuid.uuid4()),
        state=SessionState.AI,
        client_info_id=client_info.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


def get_session_by_id(db: Session, session_id: str) -> Optional[ChatSession]:
    """Get a chat session by session_id."""
    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()


def get_session_messages(db: Session, session_db_id: int) -> List[Message]:
    """Get all messages for a session."""
    return db.query(Message).filter(
        Message.session_id == session_db_id
    ).order_by(Message.created_at).all()


def update_session_state(db: Session, session_db_id: int, new_state: SessionState) -> ChatSession:
    """Update the state of a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_db_id).first()
    if session:
        session.state = new_state
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def assign_admin_to_session(db: Session, session_db_id: int, admin_id: int) -> ChatSession:
    """Assign an admin to a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_db_id).first()
    if session:
        session.assigned_admin_id = admin_id
        session.state = SessionState.HUMAN
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def close_session(db: Session, session_db_id: int) -> ChatSession:
    """Close a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_db_id).first()
    if session:
        session.state = SessionState.CLOSED
        session.closed_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def get_pending_sessions(db: Session) -> List[ChatSession]:
    """Get all sessions waiting for human agent (in HUMAN state but no admin assigned)."""
    return db.query(ChatSession).filter(
        ChatSession.state == SessionState.HUMAN,
        ChatSession.assigned_admin_id == None
    ).order_by(ChatSession.created_at).all()


def get_active_admin_sessions(db: Session, admin_id: int) -> List[ChatSession]:
    """Get all active sessions assigned to an admin."""
    return db.query(ChatSession).filter(
        ChatSession.assigned_admin_id == admin_id,
        ChatSession.state == SessionState.HUMAN
    ).order_by(desc(ChatSession.updated_at)).all()


def get_all_active_sessions(db: Session) -> List[ChatSession]:
    """Get all active sessions (AI or HUMAN, not closed)."""
    return db.query(ChatSession).filter(
        ChatSession.state.in_([SessionState.AI, SessionState.HUMAN])
    ).order_by(desc(ChatSession.updated_at)).all()
