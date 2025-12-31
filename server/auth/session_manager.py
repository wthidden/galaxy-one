"""
Session management for authenticated players.
"""
import logging
from typing import Optional, Dict
from .models import Session
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages player sessions and authentication tokens."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}  # token -> Session
        self._player_sessions: Dict[str, str] = {}  # player_id -> token

    def create_session(self, player_id: str) -> Session:
        """
        Create a new session for a player.
        If player already has a session, invalidate the old one.

        Args:
            player_id: Player ID

        Returns:
            New Session object
        """
        # Invalidate old session if exists
        if player_id in self._player_sessions:
            old_token = self._player_sessions[player_id]
            if old_token in self._sessions:
                del self._sessions[old_token]
                logger.info(f"Invalidated old session for player {player_id}")

        # Create new session
        session = Session(player_id)
        self._sessions[session.token] = session
        self._player_sessions[player_id] = session.token

        logger.info(f"Created session for player {player_id}, token: {session.token[:8]}...")
        return session

    def get_session(self, token: str) -> Optional[Session]:
        """
        Get session by token.

        Args:
            token: Session token

        Returns:
            Session if valid and not expired, None otherwise
        """
        session = self._sessions.get(token)
        if session and session.is_expired():
            # Clean up expired session
            self.invalidate_session(token)
            return None
        return session

    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate a session token and return player_id.

        Args:
            token: Session token

        Returns:
            player_id if valid, None otherwise
        """
        session = self.get_session(token)
        return session.player_id if session else None

    def invalidate_session(self, token: str):
        """
        Invalidate a session (logout).

        Args:
            token: Session token to invalidate
        """
        session = self._sessions.get(token)
        if session:
            player_id = session.player_id
            del self._sessions[token]
            if player_id in self._player_sessions:
                del self._player_sessions[player_id]
            logger.info(f"Invalidated session for player {player_id}")

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired_tokens = [
            token for token, session in self._sessions.items()
            if session.is_expired()
        ]

        for token in expired_tokens:
            session = self._sessions[token]
            player_id = session.player_id
            del self._sessions[token]
            if player_id in self._player_sessions:
                del self._player_sessions[player_id]

        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")

    def get_all_sessions(self) -> Dict[str, Session]:
        """
        Get all active sessions.

        Returns:
            Dictionary of token -> Session
        """
        return dict(self._sessions)

    def load_sessions(self, sessions_data: list):
        """
        Load sessions from persistence.

        Args:
            sessions_data: List of session dictionaries
        """
        for data in sessions_data:
            session = Session.from_dict(data)
            if not session.is_expired():
                self._sessions[session.token] = session
                self._player_sessions[session.player_id] = session.token

        logger.info(f"Loaded {len(self._sessions)} active sessions")


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
