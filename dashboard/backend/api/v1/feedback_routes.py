"""
Feedback Routes

API endpoints for feedback collection and management.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from schemas import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    FeedbackListResponse,
    FeedbackStatus,
    FeedbackType,
    Priority,
    ApiResponse,
)
from services.feedback_service import (
    create_feedback,
    get_feedback_by_id,
    list_feedback,
    update_feedback,
    delete_feedback,
    get_feedback_stats,
)
from services.auth_service import get_current_user_optional, get_current_user
from models import User

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback",
    description="Submit new feedback. Can be anonymous or authenticated.",
)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Submit new feedback (anonymous or authenticated)."""
    user_agent = request.headers.get("user-agent")
    tenant_id = current_user.tenant_id if current_user else None
    
    feedback = await create_feedback(
        db=db,
        feedback_data=feedback_data,
        user_id=current_user.id if current_user else None,
        tenant_id=tenant_id,
        user_agent=user_agent,
    )
    return feedback


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="List feedback",
    description="List all feedback with optional filters. Requires authentication.",
)
async def get_feedback_list(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[FeedbackStatus] = None,
    feedback_type: Optional[FeedbackType] = None,
    priority: Optional[Priority] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List feedback with pagination and filters."""
    skip = (page - 1) * page_size
    feedbacks, total = await list_feedback(
        db=db,
        skip=skip,
        limit=page_size,
        status=status_filter,
        feedback_type=feedback_type,
        priority=priority,
    )
    return FeedbackListResponse(
        items=[FeedbackResponse.model_validate(f) for f in feedbacks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/stats",
    summary="Get feedback statistics",
    description="Get aggregated feedback statistics.",
)
async def get_feedback_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback statistics."""
    tenant_id = current_user.tenant_id if not current_user.is_superuser else None
    stats = await get_feedback_stats(db, tenant_id=tenant_id)
    return stats


@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Get feedback by ID",
    description="Get a specific feedback entry by ID.",
)
async def get_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get feedback by ID."""
    feedback = await get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    return feedback


@router.patch(
    "/{feedback_id}",
    response_model=FeedbackResponse,
    summary="Update feedback",
    description="Update feedback status, assignment, or other fields.",
)
async def update_feedback_endpoint(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update feedback."""
    feedback = await update_feedback(db, feedback_id, feedback_data)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    return feedback


@router.delete(
    "/{feedback_id}",
    response_model=ApiResponse,
    summary="Delete feedback",
    description="Delete feedback. Admin only.",
)
async def delete_feedback_endpoint(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete feedback (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete feedback",
        )
    
    success = await delete_feedback(db, feedback_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    return ApiResponse(success=True, message="Feedback deleted successfully")
