"""Base OAuth provider implementation."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional
import secrets

from src.domain.auth import OAuthProvider as OAuthProviderInterface
from src.domain.auth import Token, OAuthUser
from src.domain.auth.value_objects import AuthProvider


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    user_info_url: str
    scopes: list[str]
    
    # Optional settings
    redirect_uri: Optional[str] = None
    additional_params: dict = None
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


class BaseOAuthProvider(OAuthProviderInterface):
    """Base implementation for OAuth providers."""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self._http_client = None
    
    @property
    @abstractmethod
    def provider_name(self) -> AuthProvider:
        """Get the provider name."""
        pass
    
    def _get_http_client(self):
        """Get or create HTTP client."""
        if self._http_client is None:
            import httpx
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    def generate_state(self) -> str:
        """Generate a secure state parameter for CSRF protection."""
        return secrets.token_urlsafe(32)
    
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
        from urllib.parse import urlencode, urlparse, urlunparse
        
        # Use provided scope or default from config
        scope_str = scope or " ".join(self.config.scopes)
        
        # Build query parameters
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope_str,
            "state": state,
        }
        
        # Add any additional parameters
        params.update(self.config.additional_params)
        
        # Build full URL
        parsed = urlparse(self.config.authorization_url)
        query = urlencode(params)
        
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query,
            parsed.fragment,
        ))
    
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
        client = self._get_http_client()
        
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        
        headers = {
            "Accept": "application/json",
        }
        
        response = await client.post(
            self.config.token_url,
            data=data,
            headers=headers,
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return self._parse_token_response(token_data)
    
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
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New Token entity
        """
        client = self._get_http_client()
        
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        response = await client.post(
            self.config.token_url,
            data=data,
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        return self._parse_token_response(token_data, refresh_token)
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        # Default implementation - providers may override
        # Most providers have a revocation endpoint
        return True
    
    def _parse_token_response(
        self,
        data: dict,
        refresh_token: Optional[str] = None,
    ) -> Token:
        """Parse token response from provider."""
        from datetime import datetime, timedelta
        
        # Calculate expiration time
        expires_in = data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return Token(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", refresh_token),
            token_type=data.get("token_type", "Bearer"),
            expires_at=expires_at,
            scope=data.get("scope", ""),
        )
