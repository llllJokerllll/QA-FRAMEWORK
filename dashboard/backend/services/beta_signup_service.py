"""
Beta Signup Service

Business logic for beta tester signup and management.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from models import BetaSignup
from schemas import (
    BetaSignupCreate,
    BetaSignupUpdate,
    BetaSignupResponse,
    BetaSignupStatus,
    TeamSize,
)


async def create_beta_signup(
    db: AsyncSession,
    signup_data: BetaSignupCreate,
) -> BetaSignup:
    """Create a new beta signup."""
    signup = BetaSignup(
        email=signup_data.email,
        company=signup_data.company,
        use_case=signup_data.use_case,
        team_size=signup_data.team_size.value if isinstance(signup_data.team_size, TeamSize) else signup_data.team_size,
        source=signup_data.source,
        utm_campaign=signup_data.utm_campaign,
        utm_source=signup_data.utm_source,
        status=BetaSignupStatus.pending.value,
    )
    db.add(signup)
    await db.commit()
    await db.refresh(signup)
    return signup


async def get_beta_signup_by_id(db: AsyncSession, signup_id: int) -> Optional[BetaSignup]:
    """Get beta signup by ID."""
    result = await db.execute(
        select(BetaSignup).where(BetaSignup.id == signup_id)
    )
    return result.scalar_one_or_none()


async def get_beta_signup_by_email(db: AsyncSession, email: str) -> Optional[BetaSignup]:
    """Get beta signup by email."""
    result = await db.execute(
        select(BetaSignup).where(BetaSignup.email == email)
    )
    return result.scalar_one_or_none()


async def list_beta_signups(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status: Optional[BetaSignupStatus] = None,
    source: Optional[str] = None,
) -> tuple[List[BetaSignup], int]:
    """List beta signups with filters."""
    query = select(BetaSignup)
    
    # Apply filters
    filters = []
    if status:
        filters.append(BetaSignup.status == status.value)
    if source:
        filters.append(BetaSignup.source == source)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_query = select(func.count()).select_from(BetaSignup)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.order_by(BetaSignup.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    signups = result.scalars().all()
    
    return list(signups), total


async def update_beta_signup(
    db: AsyncSession,
    signup_id: int,
    signup_data: BetaSignupUpdate,
) -> Optional[BetaSignup]:
    """Update beta signup."""
    signup = await get_beta_signup_by_id(db, signup_id)
    if not signup:
        return None
    
    update_data = signup_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(signup, field):
            setattr(signup, field, value)
    
    # Auto-set timestamps based on status
    new_status = update_data.get("status")
    if new_status == BetaSignupStatus.approved and not signup.invite_sent_at:
        signup.invite_sent_at = datetime.utcnow()
    elif new_status == BetaSignupStatus.onboarded and not signup.onboarded_at:
        signup.onboarded_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(signup)
    return signup


async def approve_beta_signup(db: AsyncSession, signup_id: int) -> Optional[BetaSignup]:
    """Approve a beta signup."""
    return await update_beta_signup(
        db,
        signup_id,
        BetaSignupUpdate(status=BetaSignupStatus.approved),
    )


async def reject_beta_signup(db: AsyncSession, signup_id: int) -> Optional[BetaSignup]:
    """Reject a beta signup."""
    return await update_beta_signup(
        db,
        signup_id,
        BetaSignupUpdate(status=BetaSignupStatus.rejected),
    )


async def get_beta_signup_stats(db: AsyncSession) -> dict:
    """Get beta signup statistics."""
    # Total count
    total_result = await db.execute(select(func.count()).select_from(BetaSignup))
    total = total_result.scalar()
    
    # By status
    status_query = (
        select(BetaSignup.status, func.count().label("count"))
        .group_by(BetaSignup.status)
    )
    status_result = await db.execute(status_query)
    by_status = {row.status: row.count for row in status_result}
    
    # By source
    source_query = (
        select(BetaSignup.source, func.count().label("count"))
        .where(BetaSignup.source.isnot(None))
        .group_by(BetaSignup.source)
    )
    source_result = await db.execute(source_query)
    by_source = {row.source: row.count for row in source_result}
    
    # By team size
    team_query = (
        select(BetaSignup.team_size, func.count().label("count"))
        .where(BetaSignup.team_size.isnot(None))
        .group_by(BetaSignup.team_size)
    )
    team_result = await db.execute(team_query)
    by_team_size = {row.team_size: row.count for row in team_result}
    
    # Average NPS score
    nps_query = select(func.avg(BetaSignup.feedback_score)).where(
        BetaSignup.feedback_score.isnot(None)
    )
    nps_result = await db.execute(nps_query)
    avg_nps = nps_result.scalar()
    
    # Conversion rate (onboarded / total)
    onboarded = by_status.get(BetaSignupStatus.onboarded.value, 0)
    conversion_rate = (onboarded / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "by_status": by_status,
        "by_source": by_source,
        "by_team_size": by_team_size,
        "average_nps": round(avg_nps, 2) if avg_nps else None,
        "conversion_rate": round(conversion_rate, 2),
    }
