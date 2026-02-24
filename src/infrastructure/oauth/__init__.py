"""Infrastructure layer for OAuth providers."""
from .base_oauth import BaseOAuthProvider, OAuthConfigurationError, OAuthExchangeError, OAuthUserInfoError, OAuthRefreshError
from .google_oauth import GoogleOAuthProvider
from .github_oauth import GitHubOAuthProvider
from .oauth_factory import OAuthProviderFactory

__all__ = [
    "BaseOAuthProvider",
    "GoogleOAuthProvider",
    "GitHubOAuthProvider",
    "OAuthProviderFactory",
    "OAuthConfigurationError",
    "OAuthExchangeError",
    "OAuthUserInfoError",
    "OAuthRefreshError",
]