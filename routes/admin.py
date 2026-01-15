from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.chat import AdminUser, ChatSession
from schemas.chat import SessionResponse, AdminResponse
from auth.dependencies import get_current_admin
from services import (
    get_pending_sessions,
    get_active_admin_sessions,
    get_all_active_sessions,
    assign_admin_to_session,
    close_session,
    get_session_by_id,
)
from utils.queue import session_queue

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/queue", response_model=List[SessionResponse])
async def get_queue(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all sessions waiting in queue for human agent.
    
    Requires JWT authentication.
    """
    pending_sessions = get_pending_sessions(db)
    return pending_sessions


@router.get("/active", response_model=List[SessionResponse])
async def get_active_sessions(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions (assigned to current admin or all active).
    
    Requires JWT authentication.
    """
    # Get sessions assigned to this admin
    active_sessions = get_active_admin_sessions(db, current_admin.id)
    return active_sessions


@router.get("/all-sessions", response_model=List[SessionResponse])
async def get_all_sessions(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all active sessions (AI and HUMAN states).
    
    Requires JWT authentication.
    """
    all_sessions = get_all_active_sessions(db)
    return all_sessions


@router.post("/sessions/{session_id}/claim", response_model=SessionResponse)
async def claim_session(
    session_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Claim a session from the queue.
    
    Requires JWT authentication.
    """
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Assign to admin
    updated_session = assign_admin_to_session(db, session.id, current_admin.id)
    
    # Remove from queue
    session_queue.remove_session(session_id)
    
    return updated_session


@router.post("/sessions/{session_id}/close", response_model=SessionResponse)
async def close_session_endpoint(
    session_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Close a chat session.
    
    Requires JWT authentication.
    """
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify admin is assigned to this session
    if session.assigned_admin_id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this session"
        )
    
    closed_session = close_session(db, session.id)
    return closed_session


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get current authenticated admin information.
    
    Requires JWT authentication.
    """
    return current_admin
