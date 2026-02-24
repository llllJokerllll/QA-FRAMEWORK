"""OAuth provider factory for creating provider instances."""

from typing import Optional
import os

from src.domain.auth.value_objects import AuthProvider
from src.domain.auth.interfaces import OAuthProvider as OAuthProviderInterface
from .google_oauth import GoogleOAuthProvider
from .github_oauth import GitHubOAuthProvider


class OAuthProviderFactory:
    """Factory for creating OAuth provider instances."""
    
    _providers: dict[AuthProvider, type] = {
        AuthProvider.GOOGLE: GoogleOAuthProvider,
        AuthProvider.GITHUB: GitHubOAuthProvider,
    }
    
    @classmethod
    def create(cls, provider: AuthProvider) -> OAuthProviderInterface:
        """
        Create an OAuth provider instance from environment variables.
        
        Args:
            provider: The provider type to create
            
        Returns:
            Configured OAuth provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider not in cls._providers:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
        
        provider_class = cls._providers[provider]
        return provider_class.from_env()
    
    @classmethod
    def create_google(
        cls,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> GoogleOAuthProvider:
        """
        Create a Google OAuth provider.
        
        Args:
            client_id: Google client ID (defaults to env var)
            client_secret: Google client secret (defaults to env var)
            
        Returns:
            Configured GoogleOAuthProvider instance
        """
        from .base_oauth import OAuthConfig
        
        config = OAuthConfig(
            client_id=client_id or os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=client_secret or os.getenv("GOOGLE_CLIENT_SECRET", ""),
            authorization_url=GoogleOAuthProvider.GOOGLE_AUTH_URL,
            token_url=GoogleOAuthProvider.GOOGLE_TOKEN_URL,
            user_info_url=GoogleOAuthProvider.GOOGLE_USER_INFO_URL,
            scopes=GoogleOAuthProvider.DEFAULT_SCOPES,
            additional_params={
                "access_type": "offline",
                "prompt": "consent",
            },
        )
        
        return GoogleOAuthProvider(config)
    
    @classmethod
    def create_github(
        cls,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> GitHubOAuthProvider:
        """
        Create a GitHub OAuth provider.
        
        Args:
            client_id: GitHub client ID (defaults to env var)
            client_secret: GitHub client secret (defaults to env var)
            
        Returns:
            Configured GitHubOAuthProvider instance
        """
        from .base_oauth import OAuthConfig
        
        config = OAuthConfig(
            client_id=client_id or os.getenv("GITHUB_CLIENT_ID", ""),
            client_secret=client_secret or os.getenv("GITHUB_CLIENT_SECRET", ""),
            authorization_url=GitHubOAuthProvider.GITHUB_AUTH_URL,
            token_url=GitHubOAuthProvider.GITHUB_TOKEN_URL,
            user_info_url=GitHubOAuthProvider.GITHUB_USER_INFO_URL,
            scopes=GitHubOAuthProvider.DEFAULT_SCOPES,
        )
        
        return GitHubOAuthProvider(config)
    
    @classmethod
    def get_supported_providers(cls) -> list[AuthProvider]:
        """Get list of supported OAuth providers."""
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_supported(cls, provider: AuthProvider) -> bool:
        """Check if a provider is supported."""
        return provider in cls._providers
    
    @classmethod
    def register_provider(
        cls,
        provider: AuthProvider,
        provider_class: type,
    ) -> None:
        """
        Register a custom OAuth provider.
        
        Args:
            provider: Provider enum value
            provider_class: Provider class (must implement OAuthProvider interface)
        """
        cls._providers[provider] = provider_class
