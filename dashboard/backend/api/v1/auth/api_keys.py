"""API Key management endpoints."""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

router = APIRouter()


class APIKeyCreate(BaseModel):
    """API key creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    scopes: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    """API key response with plaintext key (shown once)."""
    id: UUID
    name: str
    key: str  # Plaintext key - only shown once!
    scopes: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None


class APIKeyInfo(BaseModel):
    """API key info without sensitive data."""
    id: UUID
    name: str
    scopes: List[str]
    last_used_at: Optional[datetime] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool


# Available scopes for API keys
AVAILABLE_SCOPES = {
    "read:tests": "Read test results",
    "write:tests": "Create and update tests",
    "delete:tests": "Delete tests",
    "read:reports": "Read reports",
    "write:reports": "Generate reports",
    "admin": "Full administrative access",
    "*": "All scopes (use with caution)",
}


@router.post("", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyCreate):
    """
    Create a new API key.
    
    Returns the plaintext key - this is the only time it will be shown!
    """
    from src.domain.auth import APIKey
    from uuid import uuid4
    from datetime import timedelta
    
    # Validate scopes
    for scope in request.scopes:
        if scope not in AVAILABLE_SCOPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scope: {scope}. Available scopes: {list(AVAILABLE_SCOPES.keys())}"
            )
    
    # Calculate expiration
    expires_at = None
    if request.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
    
    # TODO: Get user_id from authentication
    user_id = uuid4()  # Placeholder
    
    # Create API key
    api_key, plaintext_key = APIKey.create(
        name=request.name,
        user_id=user_id,
        scopes=request.scopes,
        expires_at=expires_at,
    )
    
    # TODO: Store in database
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=plaintext_key,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
    )


@router.get("", response_model=List[APIKeyInfo])
async def list_api_keys():
    """
    List all API keys for the authenticated user.
    
    Does not return the actual key values.
    """
    # TODO: Get user_id from authentication
    # TODO: Query database for user's API keys
    
    # Placeholder
    return []


@router.get("/scopes")
async def list_available_scopes():
    """List all available scopes for API keys."""
    return {
        "scopes": [
            {"name": name, "description": desc}
            for name, desc in AVAILABLE_SCOPES.items()
        ]
    }


@router.get("/{key_id}", response_model=APIKeyInfo)
async def get_api_key(key_id: UUID):
    """
    Get API key information.
    
    Does not return the actual key value.
    """
    # TODO: Get user_id from authentication
    # TODO: Query database
    
    raise HTTPException(
        status_code=404,
        detail="API key not found"
    )


@router.delete("/{key_id}")
async def revoke_api_key(key_id: UUID):
    """
    Revoke an API key.
    
    The key will immediately become invalid.
    """
    # TODO: Get user_id from authentication
    # TODO: Verify ownership
    # TODO: Delete or deactivate in database
    
    return {
        "success": True,
        "message": "API key revoked",
    }


@router.post("/{key_id}/regenerate", response_model=APIKeyResponse)
async def regenerate_api_key(key_id: UUID):
    """
    Regenerate an API key.
    
    Creates a new key with the same scopes and invalidates the old one.
    """
    # TODO: Get user_id from authentication
    # TODO: Verify ownership
    # TODO: Create new key
    # TODO: Delete old key
    
    raise HTTPException(
        status_code=404,
        detail="API key not found"
    )


@router.get("/{key_id}/usage")
async def get_api_key_usage(
    key_id: UUID,
    days: int = Query(7, ge=1, le=90, description="Number of days to show"),
):
    """
    Get usage statistics for an API key.
    
    Returns request counts and patterns.
    """
    # TODO: Query usage logs
    
    return {
        "key_id": key_id,
        "period_days": days,
        "total_requests": 0,
        "requests_by_day": [],
        "requests_by_endpoint": [],
        "last_used": None,
    }
