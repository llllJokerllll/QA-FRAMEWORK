"""
Cron Jobs Models

Models for managing scheduled background jobs with execution tracking.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CronJob(Base):
    """Cron job model for scheduling and tracking automated tasks"""
    __tablename__ = "cron_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    schedule = Column(String, nullable=False)  # Cron expression
    status = Column(String, default="active")  # active, paused, error
    description = Column(Text)

    # Script path
    script_path = Column(String, nullable=False)

    # Stats
    last_run = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    avg_duration = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    executions = relationship("CronExecution", backref="job", cascade="all, delete-orphan")


class CronExecution(Base):
    """Execution log for cron jobs"""
    __tablename__ = "cron_executions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("cron_jobs.id"), nullable=False)

    # Execution status
    status = Column(String, nullable=False)  # running, success, error, skipped

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True))

    # Performance
    duration = Column(Float)  # Duration in seconds

    # Output
    output = Column(Text)
    error_message = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
