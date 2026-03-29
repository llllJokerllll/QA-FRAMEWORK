"""Onboarding service - handles user onboarding state management."""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any

from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

# Default onboarding steps
DEFAULT_STEPS = {
    "welcome": False,
    "connect_repo": False,
    "create_suite": False,
    "run_test": False,
    "setup_notifications": False,
}


def get_default_onboarding_state() -> Dict[str, Any]:
    """Return the default onboarding state for new users."""
    return {
        "current_step": 0,
        "steps": dict(DEFAULT_STEPS),
    }


async def get_onboarding_state(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Get the onboarding state for a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    state = user.onboarding_state or get_default_onboarding_state()
    
    return {
        "completed": user.onboarding_completed or False,
        "current_step": state.get("current_step", 0),
        "steps": state.get("steps", dict(DEFAULT_STEPS)),
        "completed_at": user.onboarding_completed_at,
    }


async def update_onboarding_step(
    db: AsyncSession,
    user_id: int,
    step_name: str,
    completed: bool = True,
) -> Dict[str, Any]:
    """Mark a specific onboarding step as completed/incomplete."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    state = user.onboarding_state or get_default_onboarding_state()
    steps = state.get("steps", dict(DEFAULT_STEPS))
    
    if step_name not in steps:
        raise ValueError(f"Invalid step name: {step_name}. Valid steps: {list(steps.keys())}")
    
    steps[step_name] = completed
    state["steps"] = steps
    
    # Auto-advance current_step to the next incomplete step
    step_names = list(DEFAULT_STEPS.keys())
    current = 0
    for i, name in enumerate(step_names):
        if not steps.get(name, False):
            current = i
            break
    else:
        # All steps completed
        current = len(step_names)
    
    state["current_step"] = current
    
    user.onboarding_state = state
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User {user_id} onboarding step '{step_name}' marked as {completed}")
    
    return {
        "completed": user.onboarding_completed or False,
        "current_step": state["current_step"],
        "steps": steps,
        "completed_at": user.onboarding_completed_at,
    }


async def complete_onboarding(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Mark the entire onboarding as completed."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    state = user.onboarding_state or get_default_onboarding_state()
    steps = state.get("steps", dict(DEFAULT_STEPS))
    
    # Mark all steps as completed
    for key in steps:
        steps[key] = True
    
    state["steps"] = steps
    state["current_step"] = len(steps)
    
    user.onboarding_state = state
    user.onboarding_completed = True
    user.onboarding_completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User {user_id} completed onboarding")
    
    return {
        "completed": True,
        "current_step": state["current_step"],
        "steps": steps,
        "completed_at": user.onboarding_completed_at,
    }


async def skip_onboarding(db: AsyncSession, user_id: int) -> Dict[str, Any]:
    """Skip the onboarding flow entirely."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    user.onboarding_completed = True
    user.onboarding_completed_at = datetime.utcnow()
    
    # Keep current state as-is (don't mark steps as completed)
    if not user.onboarding_state:
        user.onboarding_state = get_default_onboarding_state()
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User {user_id} skipped onboarding")
    
    return {
        "completed": True,
        "current_step": user.onboarding_state.get("current_step", 0),
        "steps": user.onboarding_state.get("steps", dict(DEFAULT_STEPS)),
        "completed_at": user.onboarding_completed_at,
    }
