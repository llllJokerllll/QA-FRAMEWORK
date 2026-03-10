"""
Bulk Operations API Routes

Provides endpoints for bulk operations on test suites.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session as get_db
from schemas import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    BulkExecuteRequest,
    BulkExecuteResponse,
    BulkArchiveRequest,
    BulkArchiveResponse,
)
from services.auth_service import get_current_user
from services.bulk_service import (
    bulk_delete_suites,
    bulk_execute_suites,
    bulk_archive_suites,
)
from core.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/suites", tags=["bulk-operations"])


@router.post(
    "/bulk-delete",
    response_model=BulkDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk delete test suites",
    description="Soft delete multiple test suites at once. Maximum 100 suites per request."
)
async def bulk_delete(
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Bulk delete multiple test suites.

    Soft deletes multiple test suites by setting is_active to false.
    The suites and their cases are retained in the database but marked as inactive.

    Args:
        request: BulkDeleteRequest containing list of suite_ids
        db: Database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        BulkDeleteResponse with operation results

    Raises:
        HTTPException 401: Authentication required
        HTTPException 400: Invalid request (empty list, duplicates, or exceeds limit)
        HTTPException 500: Database operation failed

    Example:
        POST /api/v1/suites/bulk-delete
        Authorization: Bearer <token>
        {
            "suite_ids": [1, 2, 3, 4, 5]
        }

        Response (200 OK):
        {
            "total_requested": 5,
            "successful": [
                {"suite_id": 1, "name": "API Tests"},
                {"suite_id": 2, "name": "UI Tests"},
                {"suite_id": 3, "name": "Integration Tests"}
            ],
            "failed": [
                {"suite_id": 4, "reason": "Suite already deleted"}
            ],
            "not_found": [
                {"suite_id": 5, "reason": "Suite not found"}
            ]
        }
    """
    logger.info(
        "Bulk delete endpoint called",
        suite_count=len(request.suite_ids),
        user_id=current_user.id
    )

    try:
        result = await bulk_delete_suites(
            suite_ids=request.suite_ids,
            db=db,
            user_id=current_user.id
        )

        logger.info(
            "Bulk delete operation completed",
            total_requested=result["total_requested"],
            successful=len(result["successful"]),
            failed=len(result["failed"]),
            not_found=len(result["not_found"])
        )

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in bulk delete endpoint",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during bulk delete: {str(e)}"
        )


@router.post(
    "/bulk-execute",
    response_model=BulkExecuteResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk execute test suites",
    description="Execute multiple test suites at once. Maximum 50 suites per request."
)
async def bulk_execute(
    request: BulkExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Bulk execute multiple test suites.

    Creates test executions for multiple suites simultaneously.
    Each suite gets its own execution record.

    Args:
        request: BulkExecuteRequest containing:
            - suite_ids: List of suite IDs to execute (max 50)
            - execution_type: Type of execution (manual, scheduled, ci)
            - environment: Execution environment (dev, staging, production)
        db: Database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        BulkExecuteResponse with operation results

    Raises:
        HTTPException 401: Authentication required
        HTTPException 400: Invalid request (empty list, duplicates, exceeds limit, invalid params)
        HTTPException 500: Database operation failed

    Example:
        POST /api/v1/suites/bulk-execute
        Authorization: Bearer <token>
        {
            "suite_ids": [1, 2, 3],
            "execution_type": "manual",
            "environment": "staging"
        }

        Response (200 OK):
        {
            "total_requested": 3,
            "successful": [
                {
                    "suite_id": 1,
                    "suite_name": "API Tests",
                    "execution_id": 101,
                    "status": "pending"
                },
                {
                    "suite_id": 2,
                    "suite_name": "UI Tests",
                    "execution_id": 102,
                    "status": "pending"
                }
            ],
            "failed": [
                {"suite_id": 3, "reason": "Suite not found or inactive"}
            ],
            "not_found": []
        }
    """
    logger.info(
        "Bulk execute endpoint called",
        suite_count=len(request.suite_ids),
        execution_type=request.execution_type,
        environment=request.environment,
        user_id=current_user.id
    )

    try:
        result = await bulk_execute_suites(
            suite_ids=request.suite_ids,
            db=db,
            user_id=current_user.id,
            execution_type=request.execution_type,
            environment=request.environment
        )

        logger.info(
            "Bulk execute operation completed",
            total_requested=result["total_requested"],
            successful=len(result["successful"]),
            failed=len(result["failed"]),
            not_found=len(result["not_found"])
        )

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in bulk execute endpoint",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during bulk execute: {str(e)}"
        )


@router.post(
    "/bulk-archive",
    response_model=BulkArchiveResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk archive test suites",
    description="Archive multiple test suites at once. Maximum 100 suites per request."
)
async def bulk_archive(
    request: BulkArchiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Bulk archive multiple test suites.

    Archives multiple test suites by marking them as inactive and adding
    archive metadata. Preserves execution history. Cannot archive suites
    with active executions.

    Args:
        request: BulkArchiveRequest containing list of suite_ids
        db: Database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        BulkArchiveResponse with operation results

    Raises:
        HTTPException 401: Authentication required
        HTTPException 400: Invalid request (empty list, duplicates, or exceeds limit)
        HTTPException 500: Database operation failed

    Example:
        POST /api/v1/suites/bulk-archive
        Authorization: Bearer <token>
        {
            "suite_ids": [1, 2, 3, 4]
        }

        Response (200 OK):
        {
            "total_requested": 4,
            "successful": [
                {"suite_id": 1, "name": "Legacy API Tests"},
                {"suite_id": 2, "name": "Deprecated UI Tests"}
            ],
            "failed": [
                {
                    "suite_id": 3,
                    "name": "Active Tests",
                    "reason": "Suite has 2 active execution(s). Stop them before archiving."
                }
            ],
            "not_found": [],
            "already_archived": [
                {"suite_id": 4, "name": "Old Tests"}
            ]
        }
    """
    logger.info(
        "Bulk archive endpoint called",
        suite_count=len(request.suite_ids),
        user_id=current_user.id
    )

    try:
        result = await bulk_archive_suites(
            suite_ids=request.suite_ids,
            db=db,
            user_id=current_user.id
        )

        logger.info(
            "Bulk archive operation completed",
            total_requested=result["total_requested"],
            successful=len(result["successful"]),
            failed=len(result["failed"]),
            not_found=len(result["not_found"]),
            already_archived=len(result["already_archived"])
        )

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in bulk archive endpoint",
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during bulk archive: {str(e)}"
        )
