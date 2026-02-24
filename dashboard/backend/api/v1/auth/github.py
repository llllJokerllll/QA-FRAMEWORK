"""GitHub OAuth Endpoints."""
import secrets
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from infrastructure.oauth import GitHubOAuthProvider, OAuthConfigurationError, OAuthExchangeError, OAuthUserInfoError
from domain.auth.entities import Token

router = APIRouter()


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"


@router.get(
    "/auth/github",
    response_class=RedirectResponse,
    responses={
        307: {"description": "Redirect to GitHub OAuth"},
        503: {"description": "OAuth provider not configured"},
    },
)
async def github_auth() -> RedirectResponse:
    """Initiate GitHub OAuth flow.
    
    Redirects user to GitHub OAuth authorization page.
    """
    try:
        provider = GitHubOAuthProvider()
        
        if not provider.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub OAuth is not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.",
            )
        
        state = secrets.token_urlsafe(16)
        auth_url = await provider.get_authorization_url(state=state)
        
        return RedirectResponse(url=auth_url, status_code=307)
        
    except OAuthConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get(
    "/auth/github/callback",
    response_model=TokenResponse,
    responses={
        200: {"description": "OAuth successful, token returned"},
        400: {"description": "Invalid code or state"},
        503: {"description": "OAuth provider not configured"},
    },
)
async def github_callback(
    code: str,
    state: str,
) -> TokenResponse:
    """Handle GitHub OAuth callback.
    
    Exchanges the authorization code for an access token and retrieves user information.
    
    Args:
        code: Authorization code from GitHub
        state: CSRF protection state parameter
        
    Returns:
        Token response with access token
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required",
        )
    
    provider = GitHubOAuthProvider()
    
    if not provider.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured",
        )
    
    try:
        # Exchange code for token
        token: Token = await provider.exchange_code(code=code)
        
        # Get user info
        user = await provider.get_user_info(token)
        
        # In production, create/update user in database and generate JWT here
        # For now, return the OAuth token
        
        return TokenResponse(
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            expires_in=token.expires_in,
            token_type=token.token_type,
        )
        
    except OAuthExchangeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token exchange failed: {e}",
        )
    except OAuthUserInfoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user info: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {e}",
        )
    finally:
        await provider.close()
