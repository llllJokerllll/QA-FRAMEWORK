"""
Beta Signup Routes

API endpoints for beta tester signup and management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import (
    BetaSignupCreate,
    BetaSignupUpdate,
    BetaSignupResponse,
    BetaSignupListResponse,
    BetaSignupStatus,
    ApiResponse,
)
from services.beta_signup_service import (
    create_beta_signup,
    get_beta_signup_by_id,
    get_beta_signup_by_email,
    list_beta_signups,
    update_beta_signup,
    approve_beta_signup,
    reject_beta_signup,
    get_beta_signup_stats,
)
from services.auth_service import get_current_user
from models import User

router = APIRouter(prefix="/beta", tags=["Beta Signup"])


@router.post(
    "/signup",
    response_model=BetaSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up for beta",
    description="Sign up for the beta program. Public endpoint.",
)
async def signup_for_beta(
    signup_data: BetaSignupCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Sign up for beta program (public endpoint)."""
    # Check if email already exists
    existing = await get_beta_signup_by_email(db, signup_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered for beta",
        )
    
    # Extract UTM parameters from request if not provided
    query_params = dict(request.query_params)
    if not signup_data.utm_campaign and "utm_campaign" in query_params:
        signup_data.utm_campaign = query_params["utm_campaign"]
    if not signup_data.utm_source and "utm_source" in query_params:
        signup_data.utm_source = query_params["utm_source"]
    
    signup = await create_beta_signup(db, signup_data)
    return signup


@router.get(
    "",
    response_model=BetaSignupListResponse,
    summary="List beta signups",
    description="List all beta signups with optional filters. Admin only.",
)
async def get_beta_signup_list(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[BetaSignupStatus] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List beta signups (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view beta signups",
        )
    
    skip = (page - 1) * page_size
    signups, total = await list_beta_signups(
        db=db,
        skip=skip,
        limit=page_size,
        status=status_filter,
        source=source,
    )
    return BetaSignupListResponse(
        items=[BetaSignupResponse.model_validate(s) for s in signups],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/stats",
    summary="Get beta signup statistics",
    description="Get aggregated beta signup statistics. Admin only.",
)
async def get_beta_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get beta signup statistics."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view beta statistics",
        )
    stats = await get_beta_signup_stats(db)
    return stats


@router.get(
    "/check/{email}",
    summary="Check if email is registered",
    description="Check if an email is already registered for beta.",
)
async def check_beta_email(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Check if email is already registered."""
    existing = await get_beta_signup_by_email(db, email)
    return {"registered": existing is not None}


@router.get(
    "/{signup_id}",
    response_model=BetaSignupResponse,
    summary="Get beta signup by ID",
    description="Get a specific beta signup by ID. Admin only.",
)
async def get_beta_signup(
    signup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get beta signup by ID."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view beta signups",
        )
    
    signup = await get_beta_signup_by_id(db, signup_id)
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beta signup not found",
        )
    return signup


@router.patch(
    "/{signup_id}",
    response_model=BetaSignupResponse,
    summary="Update beta signup",
    description="Update beta signup status or notes. Admin only.",
)
async def update_beta_signup_endpoint(
    signup_id: int,
    signup_data: BetaSignupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update beta signup."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update beta signups",
        )
    
    signup = await update_beta_signup(db, signup_id, signup_data)
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beta signup not found",
        )
    return signup


@router.post(
    "/{signup_id}/approve",
    response_model=BetaSignupResponse,
    summary="Approve beta signup",
    description="Approve a beta signup and send invite. Admin only.",
)
async def approve_beta_signup_endpoint(
    signup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve beta signup."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve beta signups",
        )
    
    signup = await approve_beta_signup(db, signup_id)
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beta signup not found",
        )
    
    # TODO: Send welcome email with invite link
    # This would integrate with the email service
    
    return signup


@router.post(
    "/{signup_id}/reject",
    response_model=BetaSignupResponse,
    summary="Reject beta signup",
    description="Reject a beta signup. Admin only.",
)
async def reject_beta_signup_endpoint(
    signup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject beta signup."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reject beta signups",
        )
    
    signup = await reject_beta_signup(db, signup_id)
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beta signup not found",
        )
    return signup


@router.delete(
    "/{signup_id}",
    response_model=ApiResponse,
    summary="Delete beta signup",
    description="Delete beta signup. Admin only.",
)
async def delete_beta_signup_endpoint(
    signup_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete beta signup (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete beta signups",
        )
    
    signup = await get_beta_signup_by_id(db, signup_id)
    if not signup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beta signup not found",
        )
    
    await db.delete(signup)
    await db.commit()
    return ApiResponse(success=True, message="Beta signup deleted successfully")
