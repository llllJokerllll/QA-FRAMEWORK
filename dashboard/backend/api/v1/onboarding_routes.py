"""Onboarding API routes - manages user onboarding state and progress."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from database import get_db_session as get_db
from services.auth_service import get_current_user
from services.onboarding_service import (
    get_onboarding_state,
    update_onboarding_step,
    complete_onboarding,
    skip_onboarding,
)
from schemas import OnboardingStateResponse
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


class StepUpdateRequest(BaseModel):
    """Request body for updating a single onboarding step."""
    step_name: str
    completed: bool = True


class StepUpdateResponse(OnboardingStateResponse):
    """Response after updating a step."""
    message: str = "Step updated"


@router.get("", response_model=OnboardingStateResponse)
async def get_user_onboarding(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's onboarding state."""
    try:
        state = await get_onboarding_state(db, current_user.id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/step", response_model=StepUpdateResponse)
async def mark_step_completed(
    request: StepUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark an onboarding step as completed or incomplete."""
    try:
        state = await update_onboarding_step(
            db, current_user.id, request.step_name, request.completed
        )
        return {**state, "message": f"Step '{request.step_name}' updated"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/complete", response_model=OnboardingStateResponse)
async def complete_user_onboarding(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark the entire onboarding as completed."""
    try:
        state = await complete_onboarding(db, current_user.id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/skip", response_model=OnboardingStateResponse)
async def skip_user_onboarding(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Skip the onboarding flow entirely."""
    try:
        state = await skip_onboarding(db, current_user.id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
