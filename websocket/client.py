from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.chat import SessionState, SenderType
from services import (
    get_session_by_id,
    create_message,
    get_conversation_history,
    update_session_state,
)
from websocket.manager import manager
from ai.client import gemini_client
from ai.prompts import detect_handoff_request
from utils.queue import session_queue
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/client/{session_id}")
async def client_websocket(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for client connections.
    
    Handles:
    - Client messages
    - AI responses
    - Handoff requests to human agents
    - Admin responses when connected to human
    """
    # Verify session exists
    session = get_session_by_id(db, session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    # Connect client
    await manager.connect_client(session_id, websocket)
    
    # Send welcome message
    await manager.send_to_client(session_id, {
        "type": "connected",
        "message": "Welcome! How can I help you today?",
        "session_id": session_id,
        "state": session.state.value
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_content = data.get("content", "").strip()
            
            if not message_content:
                continue
            
            # Save client message
            create_message(
                db=db,
                session_db_id=session.id,
                content=message_content,
                sender_type=SenderType.CLIENT
            )
            
            # Refresh session state
            db.refresh(session)
            
            # Check if client is requesting human agent
            if detect_handoff_request(message_content) and session.state == SessionState.AI:
                # Update session to request human
                update_session_state(db, session.id, SessionState.HUMAN)
                session_queue.add_session(session_id)
                
                # Notify client
                await manager.send_to_client(session_id, {
                    "type": "handoff_requested",
                    "message": "I'll connect you with a human agent. Please wait...",
                    "sender_type": "AI"
                })
                
                # Notify all admins of new session in queue
                await manager.broadcast_to_admins({
                    "type": "new_session_queued",
                    "session_id": session_id,
                    "client_name": session.client_info.name,
                    "queue_size": session_queue.get_queue_size()
                })
                
                continue
            
            # Route message based on session state
            if session.state == SessionState.AI:
                # AI handles the message
                conversation_history = get_conversation_history(db, session.id)
                ai_response = await gemini_client.generate_response(
                    message=message_content,
                    conversation_history=conversation_history
                )
                
                # Save AI response
                create_message(
                    db=db,
                    session_db_id=session.id,
                    content=ai_response,
                    sender_type=SenderType.AI
                )
                
                # Send to client
                await manager.send_to_client(session_id, {
                    "type": "message",
                    "content": ai_response,
                    "sender_type": "AI"
                })
            
            elif session.state == SessionState.HUMAN:
                # Forward to assigned admin
                admin_id = manager.get_admin_for_session(session_id)
                if admin_id and manager.is_admin_connected(admin_id):
                    await manager.send_to_admin(admin_id, {
                        "type": "message",
                        "session_id": session_id,
                        "content": message_content,
                        "sender_type": "CLIENT",
                        "client_name": session.client_info.name
                    })
                else:
                    # No admin connected, add to queue if not already there
                    if not session_queue.is_in_queue(session_id):
                        session_queue.add_session(session_id)
                        await manager.send_to_client(session_id, {
                            "type": "waiting",
                            "message": "Waiting for an agent to connect...",
                        })
    
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Error in client WebSocket: {e}")
    finally:
        manager.disconnect_client(session_id)
