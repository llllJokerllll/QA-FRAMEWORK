"""Browser-Use API Routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from services.auth_service import get_current_user
from services.ai.browser_use_service import BrowserUseService
from schemas.browser_use import (
    BrowserUseExecuteRequest,
    BrowserUseExecuteResponse,
    BrowserUseStatusResponse,
    BrowserUseResultsResponse,
)
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/browser-use", tags=["browser-use"])

# Service singleton
_browser_use_service = None


def get_browser_use_service() -> BrowserUseService:
    """Get BrowserUseService singleton."""
    global _browser_use_service
    if _browser_use_service is None:
        _browser_use_service = BrowserUseService()
    return _browser_use_service


@router.post("/execute", response_model=BrowserUseExecuteResponse)
async def execute_browser_task(
    request: BrowserUseExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    """
    Execute a browser-use task.
    
    The task runs asynchronously. Use the returned task_id to check status.
    """
    logger.info(
        "Browser-use execute request",
        user_id=current_user.id,
        prompt=request.prompt,
        url=request.url
    )
    
    try:
        task_id = await service.execute_task(
            prompt=request.prompt,
            url=request.url,
            user_id=current_user.id,
            db=db,
            options=request.options.model_dump() if request.options else None
        )
        
        return BrowserUseExecuteResponse(
            task_id=task_id,
            status="pending",
            message="Task created successfully"
        )
    except Exception as e:
        logger.error("Failed to create browser-use task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=BrowserUseStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    """Get browser-use task status."""
    result = await service.get_status(task_id, db)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return BrowserUseStatusResponse(**result)


@router.get("/results/{task_id}", response_model=BrowserUseResultsResponse)
async def get_task_results(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    service: BrowserUseService = Depends(get_browser_use_service)
):
    """Get browser-use task results."""
    result = await service.get_results(task_id, db)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return BrowserUseResultsResponse(**result)
