"""
API Key Service - API Key Authentication for Integrations
"""

from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import secrets
import hashlib

from models import User, ApiKey
from schemas import ApiKeyCreate, ApiKeyResponse
from database import get_db_session
from core.logging_config import get_logger

logger = get_logger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class ApiKeyService:
    @staticmethod
    def generate_api_key() -> str:
        return f"qaf_live_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    async def create_api_key(db: AsyncSession, user_id: str, key_request: ApiKeyCreate) -> ApiKeyResponse:
        raw_key = ApiKeyService.generate_api_key()
        hashed_key = ApiKeyService.hash_api_key(raw_key)
        
        api_key = ApiKey(
            user_id=user_id,
            name=key_request.name,
            hashed_key=hashed_key,
            scopes=key_request.scopes or [],
            expires_at=key_request.expires_at
        )
        
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        
        return ApiKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key=raw_key,
            scopes=api_key.scopes,
            created_at=api_key.created_at,
            expires_at=api_key.expires_at
        )
    
    @staticmethod
    async def validate_api_key(db: AsyncSession, api_key: str) -> Optional[User]:
        if not api_key or not api_key.startswith("qaf_live_"):
            return None
        
        hashed_key = ApiKeyService.hash_api_key(api_key)
        
        result = await db.execute(
            select(ApiKey).where(and_(ApiKey.hashed_key == hashed_key, ApiKey.is_active == True))
        )
        key_record = result.scalar_one_or_none()
        
        if not key_record:
            return None
        
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            return None
        
        key_record.last_used_at = datetime.utcnow()
        await db.commit()
        
        result = await db.execute(select(User).where(User.id == key_record.user_id))
        return result.scalar_one_or_none()


async def get_user_from_api_key(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    if not api_key:
        return None
    return await ApiKeyService.validate_api_key(db, api_key)


api_key_service = ApiKeyService()
