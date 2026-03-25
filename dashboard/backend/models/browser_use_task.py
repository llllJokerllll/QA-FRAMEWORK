"""Browser-Use Task Model."""
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, JSON
from sqlalchemy.sql import func
from models import Base
import enum


class TaskStatus(str, enum.Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BrowserUseTask(Base):
    """Browser-Use task execution record."""
    __tablename__ = "browser_use_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    url = Column(String(500), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    options = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    screenshots = Column(JSON, nullable=True)
    video_path = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
