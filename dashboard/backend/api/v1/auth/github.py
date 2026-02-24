"""GitHub OAuth endpoints."""

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional

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
    username: Optional[str] = None
    provider: str = "github"


# Store state tokens temporarily (use Redis in production)
_state_store: dict[str, dict] = {}


@router.get("")
async def github_auth(
    request: Request,
    redirect_uri: str = Query(..., description="URI to redirect after auth"),
    state: Optional[str] = Query(None, description="Optional state parameter"),
    scope: Optional[str] = Query(None, description="Optional scopes"),
):
    """
    Initiate GitHub OAuth flow.
    
    Redirects user to GitHub's authorization page.
    """
    from src.infrastructure.oauth import GitHubOAuthProvider
    
    # Create provider
    provider = GitHubOAuthProvider.from_env()
    
    # Generate state token for CSRF protection
    state_token = state or provider.generate_state()
    
    # Store state with redirect URI
    _state_store[state_token] = {
        "redirect_uri": redirect_uri,
        "provider": "github",
    }
    
    # Build authorization URL
    auth_url = await provider.get_authorization_url(
        state=state_token,
        redirect_uri=redirect_uri,
        scope=scope,
    )
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State token for CSRF protection"),
    error: Optional[str] = Query(None, description="Error if auth failed"),
    error_description: Optional[str] = Query(None, description="Error description"),
):
    """
    Handle GitHub OAuth callback.
    
    Exchanges authorization code for access token.
    """
    from src.infrastructure.oauth import GitHubOAuthProvider
    
    # Check for errors
    if error:
        detail = error_description or error
        raise HTTPException(
            status_code=400,
            detail=f"GitHub OAuth error: {detail}"
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
        provider = GitHubOAuthProvider.from_env()
        
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
            detail=f"Failed to exchange GitHub token: {str(e)}"
        )
    finally:
        await provider.close()


@router.get("/user")
async def get_github_user(
    access_token: str = Query(..., description="GitHub access token"),
):
    """
    Get user info from GitHub.
    
    Fetches user profile using the access token.
    """
    from src.infrastructure.oauth import GitHubOAuthProvider
    from src.domain.auth import Token
    
    try:
        provider = GitHubOAuthProvider.from_env()
        
        # Create minimal token for user info request
        token = Token(access_token=access_token)
        
        user = await provider.get_user_info(token)
        
        return UserInfoResponse(
            id=user.provider_id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            username=user.raw_data.get("login"),
            provider="github",
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user info: {str(e)}"
        )
    finally:
        await provider.close()


@router.post("/validate")
async def validate_github_token(
    access_token: str = Query(..., description="GitHub access token"),
):
    """
    Validate a GitHub access token.
    
    Checks if the token is still valid.
    """
    from src.infrastructure.oauth import GitHubOAuthProvider
    
    try:
        provider = GitHubOAuthProvider.from_env()
        
        is_valid = await provider.check_token_validity(access_token)
        
        return {
            "valid": is_valid,
            "provider": "github",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate token: {str(e)}"
        )
    finally:
        await provider.close()
