from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from models.database import get_db
from models.chat import SenderType
from services import (
    get_session_by_id,
    create_message,
    assign_admin_to_session,
    close_session,
)
from websocket.manager import manager
from utils.queue import session_queue
from auth.jwt import verify_token
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/admin")
async def admin_websocket(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for admin connections.
    
    Required:
        token: JWT access token as query parameter
    
    Handles:
    - Admin authentication via JWT
    - Claiming sessions from queue
    - Bi-directional messaging with clients
    - Session management
    """
    # Verify JWT token
    payload = verify_token(token, token_type="access")
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    
    admin_username = payload.get("sub")
    admin_id = payload.get("admin_id")
    
    if not admin_username or not admin_id:
        await websocket.close(code=4001, reason="Invalid token payload")
        return
    
    # Connect admin
    await manager.connect_admin(admin_id, websocket)
    
    # Send welcome and queue info
    queue_sessions = session_queue.get_all_sessions()
    await manager.send_to_admin(admin_id, {
        "type": "connected",
        "message": f"Welcome, {admin_username}!",
        "queue_size": len(queue_sessions),
        "queued_sessions": queue_sessions
    })
    
    try:
        while True:
            # Receive message from admin
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "claim_session":
                # Admin wants to claim a session
                session_id = data.get("session_id")
                
                # Verify session exists and is available
                session = get_session_by_id(db, session_id)
                if not session:
                    await manager.send_to_admin(admin_id, {
                        "type": "error",
                        "message": "Session not found"
                    })
                    continue
                
                # Assign admin to session
                assign_admin_to_session(db, session.id, admin_id)
                manager.assign_session_to_admin(session_id, admin_id)
                
                # Remove from queue
                session_queue.remove_session(session_id)
                
                # Notify admin
                await manager.send_to_admin(admin_id, {
                    "type": "session_claimed",
                    "session_id": session_id,
                    "client_info": {
                        "name": session.client_info.name,
                        "email": session.client_info.email,
                        "phone": session.client_info.phone,
                    }
                })
                
                # Notify client
                if manager.is_client_connected(session_id):
                    await manager.send_to_client(session_id, {
                        "type": "agent_connected",
                        "message": f"You're now connected with {admin_username}",
                    })
                
                # Notify other admins
                await manager.broadcast_to_admins({
                    "type": "session_claimed_by_other",
                    "session_id": session_id,
                    "queue_size": session_queue.get_queue_size()
                }, exclude_admin_id=admin_id)
            
            elif message_type == "message":
                # Admin sending message to client
                session_id = data.get("session_id")
                content = data.get("content", "").strip()
                
                if not content:
                    continue
                
                session = get_session_by_id(db, session_id)
                if not session:
                    continue
                
                # Save admin message
                create_message(
                    db=db,
                    session_db_id=session.id,
                    content=content,
                    sender_type=SenderType.ADMIN
                )
                
                # Send to client
                if manager.is_client_connected(session_id):
                    await manager.send_to_client(session_id, {
                        "type": "message",
                        "content": content,
                        "sender_type": "ADMIN"
                    })
            
            elif message_type == "close_session":
                # Admin closing a session
                session_id = data.get("session_id")
                session = get_session_by_id(db, session_id)
                
                if session:
                    close_session(db, session.id)
                    
                    # Notify client
                    if manager.is_client_connected(session_id):
                        await manager.send_to_client(session_id, {
                            "type": "session_closed",
                            "message": "This conversation has been closed. Thank you!"
                        })
                        manager.disconnect_client(session_id)
                    
                    # Confirm to admin
                    await manager.send_to_admin(admin_id, {
                        "type": "session_closed",
                        "session_id": session_id
                    })
            
            elif message_type == "get_queue":
                # Admin requesting current queue
                queue_sessions = session_queue.get_all_sessions()
                await manager.send_to_admin(admin_id, {
                    "type": "queue_update",
                    "queue_size": len(queue_sessions),
                    "queued_sessions": queue_sessions
                })
    
    except WebSocketDisconnect:
        logger.info(f"Admin disconnected: {admin_id}")
    except Exception as e:
        logger.error(f"Error in admin WebSocket: {e}")
    finally:
        manager.disconnect_admin(admin_id)
