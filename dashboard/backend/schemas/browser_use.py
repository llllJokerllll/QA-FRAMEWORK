"""Browser-Use API Schemas."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class BrowserUseOptions(BaseModel):
    """Options for browser-use execution."""
    record_video: bool = False
    take_screenshots: bool = True
    max_steps: int = 50
    headless: bool = True


class BrowserUseExecuteRequest(BaseModel):
    """Request to execute a browser-use task."""
    prompt: str
    url: str
    options: Optional[BrowserUseOptions] = None


class BrowserUseExecuteResponse(BaseModel):
    """Response after creating a browser-use task."""
    task_id: str
    status: str
    message: str = "Task created successfully"
    created_at: Optional[datetime] = None


class BrowserUseStep(BaseModel):
    """Single step in browser-use execution."""
    action: str
    target: str
    success: bool
    timestamp: Optional[datetime] = None


class BrowserUseStatusResponse(BaseModel):
    """Response for task status."""
    task_id: str
    status: str
    progress: int = 0
    current_step: Optional[str] = None
    error: Optional[str] = None


class BrowserUseResultsResponse(BaseModel):
    """Response with full task results."""
    task_id: str
    status: str
    success: Optional[bool] = None
    steps: List[BrowserUseStep] = []
    screenshots: List[str] = []
    video: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None
