"""GitHub OAuth provider implementation."""

from datetime import datetime
from typing import Optional
import os

from .base_oauth import BaseOAuthProvider, OAuthConfig
from src.domain.auth import Token, OAuthUser
from src.domain.auth.value_objects import AuthProvider


class GitHubOAuthProvider(BaseOAuthProvider):
    """GitHub OAuth 2.0 provider implementation."""
    
    # GitHub OAuth endpoints
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_INFO_URL = "https://api.github.com/user"
    GITHUB_USER_EMAIL_URL = "https://api.github.com/user/emails"
    
    # Default scopes for GitHub OAuth
    DEFAULT_SCOPES = [
        "read:user",
        "user:email",
    ]
    
    @property
    def provider_name(self) -> AuthProvider:
        """Get the provider name."""
        return AuthProvider.GITHUB
    
    @classmethod
    def from_env(cls) -> "GitHubOAuthProvider":
        """Create provider from environment variables."""
        config = OAuthConfig(
            client_id=os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET", ""),
            authorization_url=cls.GITHUB_AUTH_URL,
            token_url=cls.GITHUB_TOKEN_URL,
            user_info_url=cls.GITHUB_USER_INFO_URL,
            scopes=cls.DEFAULT_SCOPES,
        )
        return cls(config)
    
    async def exchange_code(
        self,
        code: str,
        redirect_uri: str,
    ) -> Token:
        """
        Exchange authorization code for access token.
        
        Overrides base to handle GitHub's specific response format.
        """
        client = self._get_http_client()
        
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
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
        
        # GitHub doesn't provide refresh tokens
        return self._parse_token_response(token_data)
    
    async def get_user_info(self, token: Token) -> OAuthUser:
        """
        Get user information from GitHub.
        
        Args:
            token: Valid access token
            
        Returns:
            OAuthUser entity with user information
        """
        client = self._get_http_client()
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "QA-FRAMEWORK/1.0",
        }
        
        # Get basic user info
        response = await client.get(
            self.config.user_info_url,
            headers=headers,
        )
        
        response.raise_for_status()
        user_data = response.json()
        
        # Get primary email if not public
        email = user_data.get("email")
        if not email:
            email = await self._get_primary_email(client, headers)
        
        return self._parse_user_info({**user_data, "email": email})
    
    async def _get_primary_email(self, client, headers: dict) -> Optional[str]:
        """Get user's primary email from GitHub."""
        try:
            response = await client.get(
                self.GITHUB_USER_EMAIL_URL,
                headers=headers,
            )
            
            if response.status_code == 200:
                emails = response.json()
                for email_info in emails:
                    if email_info.get("primary") and email_info.get("verified"):
                        return email_info.get("email")
        except Exception:
            pass
        
        return None
    
    def _parse_user_info(self, data: dict) -> OAuthUser:
        """Parse user info from GitHub API response."""
        # GitHub uses 'login' as the username
        name = data.get("name") or data.get("login")
        
        # GitHub avatar URL
        avatar_url = data.get("avatar_url")
        
        return OAuthUser(
            provider=AuthProvider.GITHUB,
            provider_id=str(data.get("id", "")),
            email=data.get("email", ""),
            name=name,
            avatar_url=avatar_url,
            raw_data=data,
        )
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a GitHub access token.
        
        GitHub doesn't have a standard revocation endpoint.
        Tokens can be revoked by deleting the OAuth app authorization
        in GitHub settings.
        
        Args:
            token: Token to revoke
            
        Returns:
            True (always - GitHub handles this differently)
        """
        # GitHub tokens are managed through the GitHub UI or API
        # There's no direct revocation endpoint for OAuth tokens
        return True
    
    async def check_token_validity(self, token: str) -> bool:
        """
        Check if a GitHub token is still valid.
        
        Args:
            token: Token to check
            
        Returns:
            True if token is valid
        """
        client = self._get_http_client()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "QA-FRAMEWORK/1.0",
        }
        
        try:
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
            )
            return response.status_code == 200
        except Exception:
            return False
