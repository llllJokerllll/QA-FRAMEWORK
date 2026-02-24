"""Google OAuth endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfoResponse(BaseModel):
    """User information response."""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "google"


# Store state tokens temporarily (use Redis in production)
_state_store: dict[str, dict] = {}


@router.get("")
async def google_auth(
    request: Request,
    redirect_uri: str = Query(..., description="URI to redirect after auth"),
    state: Optional[str] = Query(None, description="Optional state parameter"),
):
    """
    Initiate Google OAuth flow.
    
    Redirects user to Google's consent screen.
    """
    from src.infrastructure.oauth import GoogleOAuthProvider
    
    # Create provider
    provider = GoogleOAuthProvider.from_env()
    
    # Generate state token for CSRF protection
    state_token = state or provider.generate_state()
    
    # Store state with redirect URI
    _state_store[state_token] = {
        "redirect_uri": redirect_uri,
        "provider": "google",
    }
    
    # Build authorization URL
    auth_url = await provider.get_authorization_url(
        state=state_token,
        redirect_uri=redirect_uri,
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State token for CSRF protection"),
    error: Optional[str] = Query(None, description="Error if auth failed"),
):
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for access token.
    """
    from src.infrastructure.oauth import GoogleOAuthProvider
    
    # Check for errors
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth error: {error}"
        )
    
    # Verify state token
    state_data = _state_store.pop(state, None)
    if not state_data:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired state token"
        )
    
    redirect_uri = state_data["redirect_uri"]
    
    try:
        # Create provider
        provider = GoogleOAuthProvider.from_env()
        
        # Exchange code for token
        token = await provider.exchange_code(code, redirect_uri)
        
        # Get user info
        oauth_user = await provider.get_user_info(token)
        
        # TODO: Link or create user in database
        # TODO: Generate JWT token for our system
        
        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            expires_in=token.expires_in_seconds,
            refresh_token=token.refresh_token,
            scope=token.scope,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to exchange Google token: {str(e)}"
        )
    finally:
        await provider.close()


@router.post("/refresh")
async def google_refresh(
    refresh_token: str = Query(..., description="Refresh token"),
):
    """
    Refresh Google access token.
    
    Use a refresh token to get a new access token.
    """
    from src.infrastructure.oauth import GoogleOAuthProvider
    
    try:
        provider = GoogleOAuthProvider.from_env()
        
        new_token = await provider.refresh_token(refresh_token)
        
        return TokenResponse(
            access_token=new_token.access_token,
            token_type=new_token.token_type,
            expires_in=new_token.expires_in_seconds,
            refresh_token=new_token.refresh_token,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh token: {str(e)}"
        )
    finally:
        await provider.close()


@router.get("/user")
async def get_google_user(
    access_token: str = Query(..., description="Google access token"),
):
    """
    Get user info from Google.
    
    Fetches user profile using the access token.
    """
    from src.infrastructure.oauth import GoogleOAuthProvider
    from src.domain.auth import Token
    
    try:
        provider = GoogleOAuthProvider.from_env()
        
        # Create minimal token for user info request
        token = Token(access_token=access_token)
        
        user = await provider.get_user_info(token)
        
        return UserInfoResponse(
            id=user.provider_id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            provider="google",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user info: {str(e)}"
        )
    finally:
        await provider.close()
