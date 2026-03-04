"""
Cron Job Schemas

Pydantic schemas for cron job validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CronJobStatus(str, Enum):
    active = "active"
    paused = "paused"
    error = "error"


class CronJobBase(BaseModel):
    """Base schema for cron job"""
    name: str = Field(..., min_length=1, max_length=100, description="Job name")
    schedule: str = Field(..., description="Cron expression (e.g., '0 13 * * *')")
    description: Optional[str] = Field(None, description="Job description")
    script_path: str = Field(..., description="Path to script to execute")


class CronJobCreate(CronJobBase):
    """Schema for creating a cron job"""
    pass


class CronJobResponse(CronJobBase):
    """Schema for cron job response"""
    id: int
    status: CronJobStatus
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    success_rate: float
    avg_duration: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CronExecutionStatus(str, Enum):
    running = "running"
    success = "success"
    error = "error"
    skipped = "skipped"


class CronExecutionBase(BaseModel):
    """Base schema for cron execution"""
    job_id: int
    status: CronExecutionStatus
    started_at: datetime
    duration: Optional[float] = None
    output: Optional[str] = None


class CronExecutionResponse(CronExecutionBase):
    """Schema for cron execution response"""
    id: int
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CronStats(BaseModel):
    """Schema for cron job statistics"""
    total_jobs: int
    active_jobs: int
    paused_jobs: int
    error_jobs: int
    total_executions_today: int
    success_rate_today: float
