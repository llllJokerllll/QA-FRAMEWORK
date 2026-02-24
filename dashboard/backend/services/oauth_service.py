"""
OAuth Service - Google & GitHub OAuth Integration
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import os
import secrets

from models import User
from schemas import TokenResponse, OAuthLoginRequest
from services.auth_service import create_access_token, hash_password
from core.logging_config import get_logger

logger = get_logger(__name__)

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/github/callback")


class OAuthService:
    @staticmethod
    def get_google_auth_url(state: str) -> str:
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"

    @staticmethod
    def get_github_auth_url(state: str) -> str:
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": GITHUB_REDIRECT_URI,
            "scope": "user:email",
            "state": state
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://github.com/login/oauth/authorize?{query}"

    @staticmethod
    async def exchange_google_code(code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code"
                },
                headers={"Accept": "application/json"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Google OAuth failed")
            return response.json()

    @staticmethod
    async def exchange_github_code(code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "code": code,
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "redirect_uri": GITHUB_REDIRECT_URI
                },
                headers={"Accept": "application/json"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="GitHub OAuth failed")
            return response.json()

    @staticmethod
    async def get_google_user_info(access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get Google user info")
            return response.json()

    @staticmethod
    async def get_github_user_info(access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get GitHub user info")
            
            user_data = response.json()
            
            # Get email
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {access_token}"}
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                primary = next((e for e in emails if e.get("primary")), None)
                if primary:
                    user_data["email"] = primary["email"]
            
            return user_data

    @staticmethod
    async def oauth_login(
        db: AsyncSession,
        oauth_request: OAuthLoginRequest,
        tenant_id: Optional[str] = None
    ) -> TokenResponse:
        logger.info("OAuth login", provider=oauth_request.provider)
        
        # Exchange code
        if oauth_request.provider == "google":
            tokens = await OAuthService.exchange_google_code(oauth_request.code)
            user_info = await OAuthService.get_google_user_info(tokens["access_token"])
            email = user_info.get("email")
            username = email.split("@")[0]
            name = user_info.get("name", username)
            provider_id = user_info.get("id")
        elif oauth_request.provider == "github":
            tokens = await OAuthService.exchange_github_code(oauth_request.code)
            user_info = await OAuthService.get_github_user_info(tokens["access_token"])
            email = user_info.get("email")
            username = user_info.get("login")
            name = user_info.get("name", username)
            provider_id = str(user_info.get("id"))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {oauth_request.provider}")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided")
        
        # Find or create user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email=email,
                username=username,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                full_name=name,
                tenant_id=tenant_id,
                oauth_provider=oauth_request.provider,
                oauth_provider_id=provider_id
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        # Generate token
        access_token = create_access_token(data={
            "sub": user.username,
            "user_id": user.id,
            "tenant_id": tenant_id
        })
        
        return TokenResponse(access_token=access_token, token_type="bearer")


oauth_service = OAuthService()
