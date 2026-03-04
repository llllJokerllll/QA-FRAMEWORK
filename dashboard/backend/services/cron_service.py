"""
Cron Job Service

Business logic for managing scheduled background jobs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from models.cron import CronJob, CronExecution
from schemas.cron import CronJobResponse, CronExecutionResponse, CronStats, CronJobCreate
from datetime import datetime, timedelta
from typing import List, Optional


class CronService:
    """Service for cron job operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_jobs(self) -> List[CronJobResponse]:
        """Get all active cron jobs with statistics"""
        result = await self.db.execute(
            select(CronJob).where(CronJob.is_active == True)
        )
        jobs = result.scalars().all()

        # Calculate success_rate for each job
        response = []
        for job in jobs:
            success_rate = 0.0
            if job.success_count + job.error_count > 0:
                success_rate = job.success_count / (job.success_count + job.error_count)

            response.append(CronJobResponse(
                **job.__dict__,
                success_rate=success_rate
            ))

        return response

    async def get_job(self, job_id: int) -> Optional[CronJobResponse]:
        """Get a specific cron job by ID"""
        result = await self.db.execute(
            select(CronJob).where(CronJob.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            return None

        success_rate = 0.0
        if job.success_count + job.error_count > 0:
            success_rate = job.success_count / (job.success_count + job.error_count)

        return CronJobResponse(**job.__dict__, success_rate=success_rate)

    async def get_executions(self, job_id: int, limit: int = 50) -> List[CronExecutionResponse]:
        """Get execution history for a specific job"""
        result = await self.db.execute(
            select(CronExecution)
            .where(CronExecution.job_id == job_id)
            .order_by(CronExecution.started_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_stats(self) -> CronStats:
        """Get statistics about cron jobs"""
        # Total jobs
        total_result = await self.db.execute(
            select(func.count(CronJob.id)).where(CronJob.is_active == True)
        )
        total_jobs = total_result.scalar()

        # By status
        active_result = await self.db.execute(
            select(func.count(CronJob.id)).where(
                and_(CronJob.is_active == True, CronJob.status == "active")
            )
        )
        active_jobs = active_result.scalar()

        paused_result = await self.db.execute(
            select(func.count(CronJob.id)).where(
                and_(CronJob.is_active == True, CronJob.status == "paused")
            )
        )
        paused_jobs = paused_result.scalar()

        error_result = await self.db.execute(
            select(func.count(CronJob.id)).where(
                and_(CronJob.is_active == True, CronJob.status == "error")
            )
        )
        error_jobs = error_result.scalar()

        # Today's executions
        today = datetime.now().date()
        today_result = await self.db.execute(
            select(func.count(CronExecution.id)).where(
                func.date(CronExecution.started_at) == today
            )
        )
        total_executions_today = today_result.scalar()

        # Today's success rate
        success_result = await self.db.execute(
            select(func.count(CronExecution.id)).where(
                and_(
                    func.date(CronExecution.started_at) == today,
                    CronExecution.status == "success"
                )
            )
        )
        success_count = success_result.scalar()

        success_rate_today = 0.0
        if total_executions_today > 0:
            success_rate_today = success_count / total_executions_today

        return CronStats(
            total_jobs=total_jobs,
            active_jobs=active_jobs,
            paused_jobs=paused_jobs,
            error_jobs=error_jobs,
            total_executions_today=total_executions_today,
            success_rate_today=success_rate_today
        )

    async def run_job(self, job_id: int) -> dict:
        """Trigger manual execution of a cron job"""
        # Get job
        job = await self.get_job(job_id)
        if not job:
            raise ValueError("Job not found")

        # Create execution record
        execution = CronExecution(
            job_id=job_id,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        await self.db.commit()

        # TODO: Actually run the script using subprocess
        # For now, just return success after a short delay
        import asyncio
        await asyncio.sleep(1)  # Simulate execution time

        execution.status = "success"
        execution.finished_at = datetime.utcnow()
        execution.duration = 1.0
        await self.db.commit()

        return {"status": "started", "execution_id": execution.id}
