"""OAuth infrastructure module for QA-FRAMEWORK SaaS."""

from .base_oauth import BaseOAuthProvider
from .google_oauth import GoogleOAuthProvider
from .github_oauth import GitHubOAuthProvider
from .oauth_factory import OAuthProviderFactory

__all__ = [
    "BaseOAuthProvider",
    "GoogleOAuthProvider",
    "GitHubOAuthProvider",
    "OAuthProviderFactory",
]
