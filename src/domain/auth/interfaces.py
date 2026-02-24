"""Auth domain interfaces for QA-FRAMEWORK SaaS."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from .entities import User, OAuthUser, Token, Session, APIKey
from .value_objects import AuthProvider


class OAuthProvider(ABC):
    """Abstract interface for OAuth providers."""
    
    @property
    @abstractmethod
    def provider_name(self) -> AuthProvider:
        """Get the provider name."""
        pass
    
    @abstractmethod
    async def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        scope: Optional[str] = None,
    ) -> str:
        """
        Generate authorization URL for OAuth flow.
        
        Args:
            state: CSRF protection state parameter
            redirect_uri: Where to redirect after auth
            scope: Optional space-separated scopes
            
        Returns:
            Authorization URL to redirect user to
        """
        pass
    
    @abstractmethod
    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> Token:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Token entity with access and refresh tokens
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, token: Token) -> OAuthUser:
        """
        Get user information from OAuth provider.
        
        Args:
            token: Valid access token
            
        Returns:
            OAuthUser entity with user information
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New Token entity
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        pass


class AuthService(ABC):
    """Abstract interface for authentication service."""
    
    @abstractmethod
    async def register_user(
        self,
        email: str,
        password: str,
        tenant_id: Optional[UUID] = None,
    ) -> User:
        """
        Register a new user with email and password.
        
        Args:
            email: User email
            password: Plain text password (will be hashed)
            tenant_id: Optional tenant ID
            
        Returns:
            Created User entity
        """
        pass
    
    @abstractmethod
    async def authenticate_email(
        self,
        email: str,
        password: str,
    ) -> Token:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Token entity for authenticated session
            
        Raises:
            AuthenticationError: If credentials invalid
        """
        pass
    
    @abstractmethod
    async def authenticate_oauth(
        self,
        provider: AuthProvider,
        code: str,
        redirect_uri: str,
    ) -> tuple[Token, User]:
        """
        Authenticate user with OAuth provider.
        
        Args:
            provider: OAuth provider (google, github, etc.)
            code: Authorization code from callback
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Tuple of (Token, User) entities
        """
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[User]:
        """
        Validate an access token.
        
        Args:
            token: Access token to validate
            
        Returns:
            User entity if valid, None otherwise
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        pass


class SessionRepository(ABC):
    """Abstract interface for session storage."""
    
    @abstractmethod
    async def create(self, session: Session) -> Session:
        """Create a new session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Session]:
        """Get session by token."""
        pass
    
    @abstractmethod
    async def get_active_by_user(self, user_id: UUID) -> list[Session]:
        """Get all active sessions for a user."""
        pass
    
    @abstractmethod
    async def update(self, session: Session) -> Session:
        """Update session."""
        pass
    
    @abstractmethod
    async def delete(self, session_id: UUID) -> bool:
        """Delete session."""
        pass
    
    @abstractmethod
    async def delete_by_user(self, user_id: UUID) -> int:
        """Delete all sessions for a user. Returns count deleted."""
        pass


class APIKeyRepository(ABC):
    """Abstract interface for API key storage."""
    
    @abstractmethod
    async def create(self, api_key: APIKey) -> APIKey:
        """Create a new API key."""
        pass
    
    @abstractmethod
    async def get_by_id(self, key_id: UUID) -> Optional[APIKey]:
        """Get API key by ID."""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[APIKey]:
        """Get all API keys for a user."""
        pass
    
    @abstractmethod
    async def get_by_key_hash(self, key_hash: str) -> Optional[APIKey]:
        """Get API key by hash."""
        pass
    
    @abstractmethod
    async def update(self, api_key: APIKey) -> APIKey:
        """Update API key."""
        pass
    
    @abstractmethod
    async def delete(self, key_id: UUID) -> bool:
        """Delete API key."""
        pass


class PasswordHasher(ABC):
    """Abstract interface for password hashing."""
    
    @abstractmethod
    def hash(self, password: str) -> str:
        """Hash a password."""
        pass
    
    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash."""
        pass


class TokenGenerator(ABC):
    """Abstract interface for token generation."""
    
    @abstractmethod
    def generate_access_token(self, user_id: UUID, tenant_id: Optional[UUID] = None) -> str:
        """Generate an access token."""
        pass
    
    @abstractmethod
    def generate_refresh_token(self) -> str:
        """Generate a refresh token."""
        pass
    
    @abstractmethod
    def generate_state_token(self) -> str:
        """Generate a state token for OAuth CSRF protection."""
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate a token. Returns payload or None if invalid."""
        pass
