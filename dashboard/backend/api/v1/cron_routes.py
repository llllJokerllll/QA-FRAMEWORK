"""
Cron Job Routes

API endpoints for managing scheduled background jobs.
SECURITY FIX: Added authentication - BETA LAUNCH PREP 2026-03-27
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db_session
from services.cron_service import CronService
from schemas.cron import CronJobResponse, CronExecutionResponse, CronStats
from services.auth_service import get_current_user
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/cron", tags=["Cron Jobs"])


@router.get("/jobs", response_model=List[CronJobResponse])
async def get_cron_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get all active cron jobs (AUTH REQUIRED).

    Returns a list of all active cron jobs with their statistics.
    """
    service = CronService(db)
    return await service.get_jobs()


@router.get("/jobs/{job_id}", response_model=CronJobResponse)
async def get_cron_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific cron job by ID (AUTH REQUIRED).

    Args:
        job_id: The ID of cron job

    Returns:
        CronJobResponse with job details and statistics

    Raises:
        HTTPException: 404 if job not found
    """
    service = CronService(db)
    job = await service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/executions", response_model=List[CronExecutionResponse])
async def get_job_executions(
    job_id: int,
    limit: int = Query(50, ge=1, le=500, description="Maximum number of executions to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get execution history for a specific job (AUTH REQUIRED).

    Args:
        job_id: The ID of cron job
        limit: Maximum number of executions to return (default: 50, max: 500)

    Returns:
        List of CronExecutionResponse with execution history
    """
    service = CronService(db)
    return await service.get_executions(job_id, limit)


@router.post("/jobs/{job_id}/run")
async def run_cron_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Trigger manual execution of a cron job (AUTH REQUIRED).

    This will immediately execute script associated with job.

    Args:
        job_id: The ID of cron job

    Returns:
        Dict with execution status

    Raises:
        HTTPException: 404 if job not found
        HTTPException: 403 if user is not superuser
    """
    # SECURITY: Only admins can trigger cron jobs manually
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can trigger cron jobs manually"
        )

    service = CronService(db)
    try:
        result = await service.run_job(job_id)
        logger.info(f"Cron job triggered manually by admin", job_id=job_id, user_id=current_user.id, execution_id=result.get("execution_id"))
        return result
    except ValueError as e:
        logger.error(f"Failed to run cron job", job_id=job_id, error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats", response_model=CronStats)
async def get_cron_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get overall cron job statistics (AUTH REQUIRED).

    Returns aggregated statistics about all active cron jobs.
    """
    service = CronService(db)
    stats = await service.get_stats()
    logger.info("Cron stats retrieved", total_jobs=stats.total_jobs, executions_today=stats.total_executions_today)
    return stats
