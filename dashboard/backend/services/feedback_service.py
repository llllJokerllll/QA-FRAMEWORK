"""
Feedback Service

Business logic for feedback collection and management.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models import Feedback, User
from schemas import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    FeedbackStatus,
    FeedbackType,
    Priority,
)


async def create_feedback(
    db: AsyncSession,
    feedback_data: FeedbackCreate,
    user_id: Optional[int] = None,
    tenant_id: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Feedback:
    """Create a new feedback entry."""
    feedback = Feedback(
        user_id=user_id,
        tenant_id=tenant_id,
        feedback_type=feedback_data.feedback_type.value,
        category=feedback_data.category,
        title=feedback_data.title,
        description=feedback_data.description,
        priority=feedback_data.priority.value if isinstance(feedback_data.priority, Priority) else feedback_data.priority,
        page_url=feedback_data.page_url,
        user_agent=user_agent,
        browser_info=feedback_data.browser_info,
        rating=feedback_data.rating,
        tags=feedback_data.tags or [],
        attachments=feedback_data.attachments or [],
        status=FeedbackStatus.new.value,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


async def get_feedback_by_id(db: AsyncSession, feedback_id: int) -> Optional[Feedback]:
    """Get feedback by ID."""
    result = await db.execute(
        select(Feedback)
        .options(selectinload(Feedback.user), selectinload(Feedback.assignee))
        .where(Feedback.id == feedback_id)
    )
    return result.scalar_one_or_none()


async def list_feedback(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[FeedbackStatus] = None,
    feedback_type: Optional[FeedbackType] = None,
    priority: Optional[Priority] = None,
    user_id: Optional[int] = None,
) -> tuple[List[Feedback], int]:
    """List feedback with filters."""
    query = select(Feedback).options(
        selectinload(Feedback.user), selectinload(Feedback.assignee)
    )
    
    # Apply filters
    filters = []
    if status:
        filters.append(Feedback.status == status.value)
    if feedback_type:
        filters.append(Feedback.feedback_type == feedback_type.value)
    if priority:
        filters.append(Feedback.priority == priority.value)
    if user_id:
        filters.append(Feedback.user_id == user_id)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(func.count()).select_from(Feedback)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    feedbacks = result.scalars().all()
    
    return list(feedbacks), total


async def update_feedback(
    db: AsyncSession,
    feedback_id: int,
    feedback_data: FeedbackUpdate,
) -> Optional[Feedback]:
    """Update feedback."""
    feedback = await get_feedback_by_id(db, feedback_id)
    if not feedback:
        return None
    
    update_data = feedback_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(feedback, field):
            if field in ["feedback_type", "priority", "status"]:
                # Convert enum to value
                setattr(feedback, field, value.value if hasattr(value, "value") else value)
            else:
                setattr(feedback, field, value)
    
    # Auto-set resolved_at when status changes to resolved
    if update_data.get("status") == FeedbackStatus.resolved and not feedback.resolved_at:
        feedback.resolved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(feedback)
    return feedback


async def delete_feedback(db: AsyncSession, feedback_id: int) -> bool:
    """Delete feedback."""
    feedback = await get_feedback_by_id(db, feedback_id)
    if not feedback:
        return False
    
    await db.delete(feedback)
    await db.commit()
    return True


async def get_feedback_stats(db: AsyncSession, tenant_id: Optional[str] = None) -> dict:
    """Get feedback statistics."""
    base_query = select(Feedback)
    if tenant_id:
        base_query = base_query.where(Feedback.tenant_id == tenant_id)
    
    # Total count
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = total_result.scalar()
    
    # By status
    status_query = (
        select(Feedback.status, func.count().label("count"))
        .group_by(Feedback.status)
    )
    if tenant_id:
        status_query = status_query.where(Feedback.tenant_id == tenant_id)
    status_result = await db.execute(status_query)
    by_status = {row.status: row.count for row in status_result}
    
    # By type
    type_query = (
        select(Feedback.feedback_type, func.count().label("count"))
        .group_by(Feedback.feedback_type)
    )
    if tenant_id:
        type_query = type_query.where(Feedback.tenant_id == tenant_id)
    type_result = await db.execute(type_query)
    by_type = {row.feedback_type: row.count for row in type_result}
    
    # Average rating
    rating_query = select(func.avg(Feedback.rating)).where(Feedback.rating.isnot(None))
    if tenant_id:
        rating_query = rating_query.where(Feedback.tenant_id == tenant_id)
    rating_result = await db.execute(rating_query)
    avg_rating = rating_result.scalar()
    
    return {
        "total": total,
        "by_status": by_status,
        "by_type": by_type,
        "average_rating": round(avg_rating, 2) if avg_rating else None,
    }
