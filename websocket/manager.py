from typing import Dict, Set, Optional
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for clients and admins."""
    
    def __init__(self):
        # Client connections: {session_id: WebSocket}
        self.client_connections: Dict[str, WebSocket] = {}
        
        # Admin connections: {admin_id: WebSocket}
        self.admin_connections: Dict[int, WebSocket] = {}
        
        # Session to admin mapping: {session_id: admin_id}
        self.session_admin_map: Dict[str, int] = {}
    
    async def connect_client(self, session_id: str, websocket: WebSocket):
        """Connect a client WebSocket."""
        await websocket.accept()
        self.client_connections[session_id] = websocket
        logger.info(f"Client connected: session_id={session_id}")
    
    def disconnect_client(self, session_id: str):
        """Disconnect a client WebSocket."""
        if session_id in self.client_connections:
            del self.client_connections[session_id]
            logger.info(f"Client disconnected: session_id={session_id}")
        
        # Remove session-admin mapping if exists
        if session_id in self.session_admin_map:
            del self.session_admin_map[session_id]
    
    async def connect_admin(self, admin_id: int, websocket: WebSocket):
        """Connect an admin WebSocket."""
        await websocket.accept()
        self.admin_connections[admin_id] = websocket
        logger.info(f"Admin connected: admin_id={admin_id}")
    
    def disconnect_admin(self, admin_id: int):
        """Disconnect an admin WebSocket."""
        if admin_id in self.admin_connections:
            del self.admin_connections[admin_id]
            logger.info(f"Admin disconnected: admin_id={admin_id}")
        
        # Remove all session mappings for this admin
        sessions_to_remove = [
            session_id for session_id, aid in self.session_admin_map.items()
            if aid == admin_id
        ]
        for session_id in sessions_to_remove:
            del self.session_admin_map[session_id]
    
    async def send_to_client(self, session_id: str, message: dict):
        """Send a message to a specific client."""
        if session_id in self.client_connections:
            try:
                await self.client_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {session_id}: {e}")
                self.disconnect_client(session_id)
    
    async def send_to_admin(self, admin_id: int, message: dict):
        """Send a message to a specific admin."""
        if admin_id in self.admin_connections:
            try:
                await self.admin_connections[admin_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to admin {admin_id}: {e}")
                self.disconnect_admin(admin_id)
    
    async def broadcast_to_admins(self, message: dict, exclude_admin_id: Optional[int] = None):
        """Broadcast a message to all connected admins."""
        for admin_id, websocket in self.admin_connections.items():
            if exclude_admin_id and admin_id == exclude_admin_id:
                continue
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to admin {admin_id}: {e}")
    
    def assign_session_to_admin(self, session_id: str, admin_id: int):
        """Assign a session to an admin."""
        self.session_admin_map[session_id] = admin_id
        logger.info(f"Session {session_id} assigned to admin {admin_id}")
    
    def get_admin_for_session(self, session_id: str) -> Optional[int]:
        """Get the admin ID assigned to a session."""
        return self.session_admin_map.get(session_id)
    
    def is_client_connected(self, session_id: str) -> bool:
        """Check if a client is connected."""
        return session_id in self.client_connections
    
    def is_admin_connected(self, admin_id: int) -> bool:
        """Check if an admin is connected."""
        return admin_id in self.admin_connections


# Global connection manager instance
manager = ConnectionManager()
