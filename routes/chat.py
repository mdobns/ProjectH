from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.chat import ChatSession, Message
from schemas.chat import (
    SessionCreate,
    SessionResponse,
    MessageResponse,
    ClientInfoResponse,
)
from services import (
    create_session,
    get_session_by_id,
    get_messages_by_session,
)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new chat session with client information.
    
    Requires:
    - name: Client's full name
    - email: Client's email address
    - phone: Client's phone number
    
    Returns the created session with session_id to use for WebSocket connection.
    """
    session = create_session(db, session_data.client_info)
    return session


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a chat session.
    """
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all messages for a chat session.
    """
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = get_messages_by_session(db, session.id)
    return messages
