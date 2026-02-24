"""Base OAuth Provider Implementation."""
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import httpx

from domain.auth.interfaces import OAuthProvider
from domain.auth.entities import OAuthUser, Token


class OAuthError(Exception):
    """Base exception for OAuth errors."""
    pass


class OAuthConfigurationError(OAuthError):
    """Raised when OAuth provider is not properly configured."""
    pass


class OAuthExchangeError(OAuthError):
    """Raised when code exchange fails."""
    pass


class OAuthUserInfoError(OAuthError):
    """Raised when fetching user info fails."""
    pass


class OAuthRefreshError(OAuthError):
    """Raised when token refresh fails."""
    pass


class BaseOAuthProvider(OAuthProvider):
    """Base implementation for OAuth 2.0 providers.
    
    Provides common functionality for OAuth 2.0 authorization code flow.
    Subclasses must implement provider-specific methods.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        """Initialize OAuth provider.
        
        Args:
            client_id: OAuth client ID (falls back to env var)
            client_secret: OAuth client secret (falls back to env var)
            redirect_uri: OAuth redirect URI (falls back to env var)
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._http_client: Optional[httpx.AsyncClient] = None
    
    @property
    def client_id(self) -> str:
        """Get client ID from config or environment."""
        return self._client_id or os.getenv(f"{self.name.upper()}_CLIENT_ID", "")
    
    @property
    def client_secret(self) -> str:
        """Get client secret from config or environment."""
        return self._client_secret or os.getenv(f"{self.name.upper()}_CLIENT_SECRET", "")
    
    @property
    def redirect_uri(self) -> str:
        """Get redirect URI from config or environment."""
        default = f"http://localhost:3000/auth/{self.name}/callback"
        return self._redirect_uri or os.getenv(f"{self.name.upper()}_REDIRECT_URI", default)
    
    def is_configured(self) -> bool:
        """Check if provider has valid credentials."""
        return bool(self.client_id and self.client_secret)
    
    def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True
            )
        return self._http_client
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Optional request headers
            data: Optional form data
            json_data: Optional JSON data
            
        Returns:
            HTTP response
        """
        client = self._get_http_client()
        
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                if json_data:
                    response = await client.post(url, headers=headers, json=json_data)
                else:
                    response = await client.post(url, headers=headers, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except httpx.RequestError as e:
            raise OAuthError(f"HTTP request failed: {e}") from e
    
    def _build_url(self, base_url: str, params: Dict[str, str]) -> str:
        """Build URL with query parameters.
        
        Args:
            base_url: Base URL
            params: Query parameters
            
        Returns:
            Complete URL with query string
        """
        from urllib.parse import urlencode
        query = urlencode(params)
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}{query}
    
    def _parse_token_response(self, data: Dict[str, Any]) -> Token:
        """Parse OAuth token response.
        
        Args:
            data: Token response data
            
        Returns:
            Token entity
        """
        expires_in = data.get("expires_in")
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return Token(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer").title(),
        )
    
    async def get_authorization_url(
        self,
        state: str,
        redirect_uri: Optional[str] = None,
    ) -> str:
        """Get OAuth authorization URL.
        
        Args:
            state: CSRF protection state
            redirect_uri: Optional redirect URI override
            
        Returns:
            Authorization URL
        """
        if not self.is_configured():
            raise OAuthConfigurationError(f"{self.name} OAuth provider not configured")
        
        uri = redirect_uri or self.redirect_uri
        params = self._get_authorization_params(state, uri)
        return self._build_url(self._authorization_url, params)
    
    async def exchange_code(
        self,
        code: str,
        redirect_uri: Optional[str] = None,
    ) -> Token:
        """Exchange authorization code for token.
        
        Args:
            code: Authorization code
            redirect_uri: Optional redirect URI override
            
        Returns:
            Token entity
        """
        if not self.is_configured():
            raise OAuthConfigurationError(f"{self.name} OAuth provider not configured")
        
        uri = redirect_uri or self.redirect_uri
        
        try:
            response = await self._exchange_code_impl(code, uri)
            data = response.json()
            
            if response.status_code != 200:
                error = data.get("error", "unknown_error")
                error_desc = data.get("error_description", "No description")
                raise OAuthExchangeError(f"Token exchange failed: {error} - {error_desc}")
            
            return self._parse_token_response(data)
            
        except httpx.RequestError as e:
            raise OAuthExchangeError(f"Token exchange request failed: {e}") from e
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token
        """
        if not self.is_configured():
            raise OAuthConfigurationError(f"{self.name} OAuth provider not configured")
        
        try:
            response = await self._refresh_token_impl(refresh_token)
            data = response.json()
            
            if response.status_code != 200:
                error = data.get("error", "unknown_error")
                raise OAuthRefreshError(f