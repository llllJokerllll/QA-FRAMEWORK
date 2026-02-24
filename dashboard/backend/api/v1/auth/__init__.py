"""Auth API router module."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from .google import router as google_router
from .github import router as github_router
from .email import router as email_router
from .api_keys import router as api_keys_router
from .sessions import router as sessions_router

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Include all auth sub-routers
router.include_router(google_router, prefix="/google", tags=["Google OAuth"])
router.include_router(github_router, prefix="/github", tags=["GitHub OAuth"])
router.include_router(email_router, tags=["Email Auth"])
router.include_router(api_keys_router, prefix="/api-keys", tags=["API Keys"])
router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])


@router.get("/providers")
async def list_auth_providers():
    """List available authentication providers."""
    from src.infrastructure.oauth import OAuthProviderFactory
    from src.domain.auth.value_objects import AuthProvider
    
    supported = OAuthProviderFactory.get_supported_providers()
    
    return {
        "providers": [
            {
                "name": provider.value,
                "type": "oauth" if provider in [AuthProvider.GOOGLE, AuthProvider.GITHUB] else "credentials",
                "available": _check_provider_availability(provider),
            }
            for provider in supported + [AuthProvider.EMAIL, AuthProvider.API_KEY]
        ]
    }


def _check_provider_availability(provider: AuthProvider) -> bool:
    """Check if provider credentials are configured."""
    import os
    
    if provider == AuthProvider.GOOGLE:
        return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
    elif provider == AuthProvider.GITHUB:
        return bool(os.getenv("GITHUB_CLIENT_ID") and os.getenv("GITHUB_CLIENT_SECRET"))
    elif provider == AuthProvider.EMAIL:
        return True  # Always available
    elif provider == AuthProvider.API_KEY:
        return True  # Always available
    
    return False
