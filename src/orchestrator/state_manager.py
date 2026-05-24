"""
State Manager - Manages workflow state and memory
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from src.utils.logger import logger
import json


class StateManager:
    """
    Manages state for workflow execution
    
    Handles:
    - State persistence
    - State recovery
    - Caching
    - Session management
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
    def save_state(self, session_id: str, state: Dict[str, Any]) -> bool:
        """
        Save workflow state
        
        Args:
            session_id: Unique session identifier
            state: State data to save
            
        Returns:
            Success status
        """
        try:
            state["updated_at"] = datetime.now().isoformat()
            
            # Try Redis first, fallback to in-memory
            if self.redis_client:
                self.redis_client.setex(
                    f"state:{session_id}",
                    3600,  # 1 hour expiry
                    json.dumps(state)
                )
            else:
                self._memory_store[session_id] = state
                
            logger.debug(f"State saved for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")
            return False
    
    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow state
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            State data or None if not found
        """
        try:
            if self.redis_client:
                state_json = self.redis_client.get(f"state:{session_id}")
                if state_json:
                    return json.loads(state_json)
            else:
                return self._memory_store.get(session_id)
                
        except Exception as e:
            logger.error(f"Failed to load state: {str(e)}")
            return None
    
    def create_session(self, user_id: str) -> str:
        """
        Create a new session
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID
        """
        session_id = f"SESSION-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
        
        self._sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "is_active": True,
            "workflow_states": []
        }
        
        return session_id
    
    def update_session_activity(self, session_id: str) -> None:
        """Update session last activity timestamp"""
        if session_id in self._sessions:
            self._sessions[session_id]["last_activity"] = datetime.now().isoformat()
    
    def close_session(self, session_id: str) -> bool:
        """Close an active session"""
        if session_id in self._sessions:
            self._sessions[session_id]["is_active"] = False
            self._sessions[session_id]["closed_at"] = datetime.now().isoformat()
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_count = 0
        
        for session_id, session in list(self._sessions.items()):
            last_activity = datetime.fromisoformat(session["last_activity"])
            if last_activity < cutoff:
                del self._sessions[session_id]
                expired_count += 1
                
        return expired_count
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self._sessions.get(session_id)
    
    def clear_all(self) -> None:
        """Clear all stored state and sessions"""
        self._memory_store.clear()
        self._sessions.clear()
        if self.redis_client:
            self.redis_client.flushdb()