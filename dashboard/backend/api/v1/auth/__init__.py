"""Auth API v1 module."""
from .router import router
from .dependencies import get_oauth_provider, require_oauth_config

__all__ = ["router", "get_oauth_provider", "require_oauth_config"]