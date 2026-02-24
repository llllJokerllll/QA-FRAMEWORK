"""
Authentication Routes - OAuth, API Keys, Login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db_session
from services.oauth_service import oauth_service, OAuthService
from services.api_key_service import api_key_service, get_user_from_api_key
from services.auth_service import login_for_access_token
from schemas import (
    LoginRequest, TokenResponse, OAuthLoginRequest, OAuthUrlResponse,
    ApiKeyCreate, ApiKeyResponse
)
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Email/Password
@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    return await login_for_access_token(login_request, db)


# OAuth
@router.get("/oauth/{provider}/url", response_model=OAuthUrlResponse)
async def get_oauth_url(provider: str):
    import secrets
    state = secrets.token_urlsafe(16)
    
    if provider == "google":
        url = OAuthService.get_google_auth_url(state)
    elif provider == "github":
        url = OAuthService.get_github_auth_url(state)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    return OAuthUrlResponse(provider=provider, authorization_url=url, state=state)


@router.post("/oauth/callback", response_model=TokenResponse)
async def oauth_callback(oauth_request: OAuthLoginRequest, db: AsyncSession = Depends(get_db_session)):
    return await oauth_service.oauth_login(db, oauth_request)


# API Keys
@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_request: ApiKeyCreate,
    current_user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await api_key_service.create_api_key(db, current_user.id, key_request)


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return await api_key_service.list_api_keys(db, current_user.id)


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    success = await api_key_service.revoke_api_key(db, current_user.id, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key revoked successfully"}
