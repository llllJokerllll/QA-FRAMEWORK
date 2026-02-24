"""Session storage backends for session management."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from uuid import UUID, uuid4
import json

from src.domain.auth.entities import Session


class SessionStore(ABC):
    """Abstract interface for session storage."""

    @abstractmethod
    async def create_session(
        self,
        user_id: UUID,
        token: str,
        expires_in_seconds: int = 86400 * 7,  # 7 days default
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> Session:
        """Create a new session.

        Args:
            user_id: User identifier
            token: Session token
            expires_in_seconds: Session lifetime
            user_agent: Client user agent string
            ip_address: Client IP address
            device_info: Device information

        Returns:
            Created Session entity
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session entity or None
        """
        pass

    @abstractmethod
    async def get_session_by_token(self, token: str) -> Optional[Session]:
        """Get session by token.

        Args:
            token: Session token

        Returns:
            Session entity or None
        """
        pass

    @abstractmethod
    async def update_session_activity(self, session_id: UUID) -> bool:
        """Update last activity timestamp.

        Args:
            session_id: Session identifier

        Returns:
            True if updated successfully
        """
        pass

    @abstractmethod
    async def revoke_session(self, session_id: UUID) -> bool:
        """Revoke a specific session.

        Args:
            session_id: Session identifier

        Returns:
            True if revoked successfully
        """
        pass

    @abstractmethod
    async def revoke_all_sessions(
        self,
        user_id: UUID,
        except_session_id: Optional[UUID] = None
    ) -> int:
        """Revoke all sessions for a user.

        Args:
            user_id: User identifier
            except_session_id: Optional session ID to keep

        Returns:
            Number of sessions revoked
        """
        pass

    @abstractmethod
    async def list_user_sessions(
        self,
        user_id: UUID,
        active_only: bool = True
    ) -> List[Session]:
        """List all sessions for a user.

        Args:
            user_id: User identifier
            active_only: Only return non-expired sessions

        Returns:
            List of session entities
        """
        pass

    @abstractmethod
    async def clean_expired_sessions(self) -> int:
        """Remove all expired sessions.

        Returns:
            Number of sessions cleaned
        """
        pass

    @abstractmethod
    async def terminate_inactive_sessions(
        self,
        user_id: UUID,
        inactive_days: int
    ) -> int:
        """Terminate sessions inactive for specified days.

        Args:
            user_id: User identifier
            inactive_days: Days of inactivity

        Returns:
            Number of sessions terminated
        """
        pass


class InMemorySessionStore(SessionStore):
    """In-memory session store for development and testing.

    NOT FOR PRODUCTION USE - Sessions are lost on restart.
    """

    def __init__(self):
        """Initialize in-memory session store."""
        self._sessions: Dict[UUID, Session] = {}

    async def create_session(
        self,
        user_id: UUID,
        token: str,
        expires_in_seconds: int = 604800,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> Session:
        """Create a new session in memory."""
        session = Session.create(
            user_id=user_id,
            token=token,
            expires_in_seconds=expires_in_seconds,
            user_agent=user_agent,
            ip_address=ip_address,
            device_info=device_info
        )
        self._sessions[session.id] = session
        return session

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session from memory."""
        session = self._sessions.get(session_id)
        if session and session.is_valid():
            return session
        return None

    async def get_session_by_token(self, token: str) -> Optional[Session]:
        """Get session by token."""
        for session in self._sessions.values():
            if session.token == token and session.is_valid():
                return session
        return None

    async def update_session_activity(self, session_id: UUID) -> bool:
        """Update session activity."""
        session = self._sessions.get(session_id)
        if session:
            session.refresh_activity()
            return True
        return False

    async def revoke_session(self, session_id: UUID) -> bool:
        """Revoke a session."""
        session = self._sessions.get(session_id)
        if session:
            session.terminate()
            return True
        return False

    async def revoke_all_sessions(
        self,
        user_id: UUID,
        except_session_id: Optional[UUID] = None
    ) -> int:
        """Revoke all sessions for user."""
        revoked_count = 0
        for session in self._sessions.values():
            if session.user_id == user_id:
                if except_session_id and session.id == except_session_id:
                    continue
                session.terminate()
                revoked_count += 1
        return revoked_count

    async def list_user_sessions(
        self,
        user_id: UUID,
        active_only: bool = True
    ) -> List[Session]:
        """List user sessions."""
        sessions = [
            s for s in self._sessions.values()
            if s.user_id == user_id and (not active_only or s.is_valid())
        ]
        # Sort by last activity (most recent first)
        return sorted(sessions, key=lambda s: s.last_activity_at, reverse=True)

    async def clean_expired_sessions(self) -> int:
        """Clean expired sessions."""
        expired_ids = [
            sid for sid, s in self._sessions.items()
            if s.is_expired()
        ]
        for sid in expired_ids:
            del self._sessions[sid]
        return len(expired_ids)

    async def terminate_inactive_sessions(
        self,
        user_id: UUID,
        inactive_days: int
    ) -> int:
        """Terminate inactive sessions."""
        cutoff = datetime.utcnow() - timedelta(days=inactive_days)
        terminated = 0
        for session in self._sessions.values():
            if session.user_id == user_id and session.last_activity_at < cutoff:
                session.terminate()
                terminated += 1
        return terminated


class RedisSessionStore(SessionStore):
    """Redis-backed session store for production.

    Requires redis-py package: pip install redis redis[hiredis]
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        key_prefix: str = "session:"
    ):
        """Initialize Redis session store.

