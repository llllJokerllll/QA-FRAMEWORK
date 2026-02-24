"""Auth Router - Combines all OAuth endpoints."""
from fastapi import APIRouter

from . import google, github

# Create main auth router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Include Google OAuth routes
router.include_router(google.router)

# Include GitHub OAuth routes
router.include_router(github.router)


@router.get("/providers")
async def get_oauth_providers():
    """Get list of available OAuth providers.
    
    Returns:
        List of OAuth providers with their configuration status
    """
    from infrastructure.oauth import OAuthProviderFactory
    
    providers = OAuthProviderFactory.get_available_providers()
    return {
        "providers": [
            {
                "name": provider.value,
                "configured": configured,
                "display_name": provider.display_name,
            }
            for provider, configured in providers.items()
        ]
    }
