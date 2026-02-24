"""Google OAuth provider implementation."""

from datetime import datetime
from typing import Optional
import os

from .base_oauth import BaseOAuthProvider, OAuthConfig
from src.domain.auth import Token, OAuthUser
from src.domain.auth.value_objects import AuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    """Google OAuth 2.0 provider implementation."""
    
    # Google OAuth endpoints
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    # Default scopes for Google OAuth
    DEFAULT_SCOPES = [
        "openid",
        "email",
        "profile",
    ]
    
    @property
    def provider_name(self) -> AuthProvider:
        """Get the provider name."""
        return AuthProvider.GOOGLE
    
    @classmethod
    def from_env(cls) -> "GoogleOAuthProvider":
        """Create provider from environment variables."""
        config = OAuthConfig(
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            authorization_url=cls.GOOGLE_AUTH_URL,
            token_url=cls.GOOGLE_TOKEN_URL,
            user_info_url=cls.GOOGLE_USER_INFO_URL,
            scopes=cls.DEFAULT_SCOPES,
            additional_params={
                "access_type": "offline",  # Get refresh token
                "prompt": "consent",  # Force consent screen
            },
        )
        return cls(config)
    
    async def get_user_info(self, token: Token) -> OAuthUser:
        """
        Get user information from Google.
        
        Args:
            token: Valid access token
            
        Returns:
            OAuthUser entity with user information
        """
        client = self._get_http_client()
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Accept": "application/json",
        }
        
        response = await client.get(
            self.config.user_info_url,
            headers=headers,
        )
        
        response.raise_for_status()
        user_data = response.json()
        
        return self._parse_user_info(user_data)
    
    def _parse_user_info(self, data: dict) -> OAuthUser:
        """Parse user info from Google API response."""
        return OAuthUser(
            provider=AuthProvider.GOOGLE,
            provider_id=data.get("id", ""),
            email=data.get("email", ""),
            name=data.get("name"),
            avatar_url=data.get("picture"),
            raw_data=data,
        )
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a Google access token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        client = self._get_http_client()
        
        revoke_url = f"https://oauth2.googleapis.com/revoke?token={token}"
        
        try:
            response = await client.post(revoke_url)
            return response.status_code == 200
        except Exception:
            return False
    
    async def get_authorization_url(
        self,
        state: str,
        redirect_uri: str,
        scope: Optional[str] = None,
    ) -> str:
        """
        Generate Google authorization URL.
        
        Overrides base to add Google-specific parameters.
        """
        # Include offline access for refresh token
        if scope is None:
            scope = " ".join(self.DEFAULT_SCOPES)
        
        return await super().get_authorization_url(state, redirect_uri, scope)
