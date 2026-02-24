"""OAuth Dependencies."""
from typing import Optional
from fastapi import HTTPException, status, Depends

from domain.auth.interfaces import OAuthProvider
from domain.auth.value_objects import AuthProvider
from infrastructure.oauth import OAuthProviderFactory


def get_oauth_provider(provider_name: str) -> OAuthProvider:
    """Dependency to get an OAuth provider instance.
    
    Args:
        provider_name: Name of the OAuth provider
        
    Returns:
        OAuthProvider instance
        
    Raises:
        HTTPException: If provider is not supported
    """
    try:
        return OAuthProviderFactory.create_from_string(provider_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


def require_oauth_config(provider: OAuthProvider) -> OAuthProvider:
    """Dependency to require OAuth provider configuration.
    
    Args:
        provider: OAuth provider instance
        
    Returns:
        OAuth provider instance
        
    Raises:
        HTTPException: If provider is not configured
    """
    if not provider.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider.display_name} OAuth is not configured",
        )
    return provider


class OAuthProviderChecker:
    """Helper class to check OAuth provider availability."""
    
    @staticmethod
    def get_available_providers() -> dict:
        """Get available OAuth providers."""
        return OAuthProviderFactory.get_available_providers()
    
    @staticmethod
    def is_provider_configured(provider_name: str) -> bool:
        """Check if a specific provider is configured."""
        try:
            provider = OAuthProviderFactory.create_from_string(provider_name)
            return provider.is_configured()
        except ValueError:
            return False


def get_oauth_status() -> dict:
    """Get status of all OAuth providers."""
    checker = OAuthProviderChecker()
    return {
        "providers": [
            {
                "name": provider.value,
                "configured": configured,
            }
            for provider, configured in checker.get_available_providers().items()
        ]
    }
