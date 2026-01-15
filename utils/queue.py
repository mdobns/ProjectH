from typing import Dict, List
from collections import deque
import asyncio
from datetime import datetime


class SessionQueue:
    """Queue for managing sessions waiting for human agents."""
    
    def __init__(self):
        self._queue: deque = deque()
        self._session_set: set = set()  # For O(1) lookup
    
    def add_session(self, session_id: str):
        """Add a session to the queue."""
        if session_id not in self._session_set:
            self._queue.append({
                "session_id": session_id,
                "queued_at": datetime.utcnow()
            })
            self._session_set.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove a session from the queue."""
        if session_id in self._session_set:
            self._queue = deque([
                item for item in self._queue 
                if item["session_id"] != session_id
            ])
            self._session_set.discard(session_id)
    
    def get_next_session(self) -> str:
        """Get the next session from the queue (FIFO)."""
        if self._queue:
            item = self._queue.popleft()
            self._session_set.discard(item["session_id"])
            return item["session_id"]
        return None
    
    def peek_next(self) -> str:
        """Peek at the next session without removing it."""
        if self._queue:
            return self._queue[0]["session_id"]
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions in the queue."""
        return list(self._queue)
    
    def get_queue_size(self) -> int:
        """Get the current size of the queue."""
        return len(self._queue)
    
    def is_in_queue(self, session_id: str) -> bool:
        """Check if a session is in the queue."""
        return session_id in self._session_set
    
    def clear(self):
        """Clear the entire queue."""
        self._queue.clear()
        self._session_set.clear()


# Global queue instance
session_queue = SessionQueue()
