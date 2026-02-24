"""Auth domain entities for QA-FRAMEWORK SaaS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from .value_objects import AuthProvider, TokenStatus


@dataclass
class User:
    """Base user entity for multi-tenant system."""
    
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    email_verified: bool = False
    password_hash: Optional[str] = None
    tenant_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    is_active: bool = True
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()


@dataclass
class OAuthUser:
    """OAuth user entity for social authentication."""
    
    id: UUID = field(default_factory=uuid4)
    provider: AuthProvider = AuthProvider.GOOGLE
    provider_id: str = ""
    email: str = ""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None  # Link to main User entity
    raw_data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def link_to_user(self, user_id: UUID) -> None:
        """Link OAuth user to main user account."""
        self.user_id = user_id
        self.updated_at = datetime.utcnow()
    
    def update_from_provider(self, name: Optional[str], avatar_url: Optional[str], raw_data: dict) -> None:
        """Update user info from provider."""
        if name:
            self.name = name
        if avatar_url:
            self.avatar_url = avatar_url
        self.raw_data = raw_data
        self.updated_at = datetime.utcnow()


@dataclass
class Token:
    """Authentication token entity."""
    
    id: UUID = field(default_factory=uuid4)
    access_token: str = ""
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    scope: str = ""
    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    status: TokenStatus = TokenStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if token has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired, not revoked)."""
        return self.status == TokenStatus.ACTIVE and not self.is_expired()
    
    def revoke(self) -> None:
        """Revoke token."""
        self.status = TokenStatus.REVOKED
    
    def mark_used(self) -> None:
        """Mark token as used (for one-time tokens)."""
        self.status = TokenStatus.USED
    
    @property
    def expires_in_seconds(self) -> Optional[int]:
        """Get seconds until expiration."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))
    
    def to_dict(self) -> dict:
        """Convert to API response dictionary."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in_seconds,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
        }


@dataclass
class Session:
    """User session entity for session management."""
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    token: str = ""
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow())
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.is_active and not self.is_expired()
    
    def refresh_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()
    
    def terminate(self) -> None:
        """Terminate session."""
        self.is_active = False
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        token: str,
        expires_in_seconds: int = 86400 * 7,  # 7 days default
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None,
    ) -> "Session":
        """Create a new session."""
        now = datetime.utcnow()
        from datetime import timedelta
        expires_at = now + timedelta(seconds=expires_in_seconds)
        
        return cls(
            user_id=user_id,
            token=token,
            user_agent=user_agent,
            ip_address=ip_address,
            device_info=device_info,
            expires_at=expires_at,
            created_at=now,
            last_activity_at=now,
            is_active=True,
        )


@dataclass
class APIKey:
    """API key entity for programmatic access."""
    
    id: UUID = field(default_factory=uuid4)
    key_hash: str = ""  # Hashed key (never store plaintext)
    name: str = ""
    user_id: UUID = field(default_factory=uuid4)
    tenant_id: Optional[UUID] = None
    scopes: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if API key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if API key is valid."""
        return self.is_active and not self.is_expired()
    
    def has_scope(self, scope: str) -> bool:
        """Check if key has a specific scope."""
        return scope in self.scopes or "*" in self.scopes
    
    def record_usage(self) -> None:
        """Record API key usage."""
        self.last_used_at = datetime.utcnow()
    
    def revoke(self) -> None:
        """Revoke API key."""
        self.is_active = False
    
    @classmethod
    def create(
        cls,
        name: str,
        user_id: UUID,
        scopes: List[str],
        tenant_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None,
    ) -> tuple["APIKey", str]:
        """
        Create a new API key.
        
        Returns:
            Tuple of (APIKey entity, plaintext key for one-time display)
        """
        import secrets
        import hashlib
        
        # Generate plaintext key (shown once)
        plaintext_key = f"qa_{secrets.token_hex(32)}"
        
        # Hash for storage
        key_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()
        
        api_key = cls(
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            tenant_id=tenant_id,
            scopes=scopes,
            expires_at=expires_at,
            is_active=True,
        )
        
        return api_key, plaintext_key
    
    def verify_key(self, plaintext_key: str) -> bool:
        """Verify a plaintext key against the stored hash."""
        import hashlib
        provided_hash = hashlib.sha256(plaintext_key.encode()).hexdigest()
        return provided_hash == self.key_hash
