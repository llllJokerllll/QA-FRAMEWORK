"""
Bulk Operations Service

Provides bulk operations for test suites including delete, execute, and archive.

Usage:
    from services.bulk_service import BulkService

    bulk_service = BulkService()
    result = await bulk_service.bulk_delete_suites(suite_ids, db)
"""

from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from models import TestSuite, TestExecution
from core.logging_config import get_logger
from core.cache import cache_manager
from services.suite_service import get_suite_by_id
from services.execution_service import create_execution_service
from schemas import TestExecutionCreate

# Initialize logger
logger = get_logger(__name__)


class BulkService:
    """Service for bulk operations on test suites."""

    @staticmethod
    async def bulk_delete_suites(
        suite_ids: List[int],
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Bulk soft delete multiple test suites.

        Args:
            suite_ids: List of suite IDs to delete
            db: Database session
            user_id: ID of user performing the operation

        Returns:
            Dictionary with operation results

        Raises:
            HTTPException: If validation fails or no suites found
        """
        logger.info(
            "Starting bulk delete operation",
            suite_ids=suite_ids,
            user_id=user_id,
            count=len(suite_ids)
        )

        # Validate input
        if not suite_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No suite IDs provided"
            )

        if len(suite_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete more than 100 suites at once"
            )

        # Validate all suite IDs are unique
        if len(set(suite_ids)) != len(suite_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate suite IDs detected"
            )

        results = {
            "total_requested": len(suite_ids),
            "successful": [],
            "failed": [],
            "not_found": []
        }

        # Process each suite
        for suite_id in suite_ids:
            try:
                # Get suite
                result = await db.execute(
                    select(TestSuite).where(TestSuite.id == suite_id)
                )
                suite = result.scalar_one_or_none()

                if not suite:
                    results["not_found"].append({
                        "suite_id": suite_id,
                        "reason": "Suite not found"
                    })
                    logger.warning(
                        "Suite not found during bulk delete",
                        suite_id=suite_id
                    )
                    continue

                # Check if already deleted
                if not suite.is_active:
                    results["failed"].append({
                        "suite_id": suite_id,
                        "reason": "Suite already deleted"
                    })
                    logger.warning(
                        "Suite already deleted",
                        suite_id=suite_id,
                        name=suite.name
                    )
                    continue

                # Soft delete
                suite.is_active = False
                suite.updated_at = datetime.utcnow()

                results["successful"].append({
                    "suite_id": suite_id,
                    "name": suite.name
                })

                logger.info(
                    "Suite soft deleted in bulk operation",
                    suite_id=suite_id,
                    name=suite.name
                )

            except Exception as e:
                results["failed"].append({
                    "suite_id": suite_id,
                    "reason": str(e)
                })
                logger.error(
                    "Failed to delete suite in bulk operation",
                    suite_id=suite_id,
                    error=str(e),
                    exc_info=True
                )

        # Commit changes
        try:
            await db.commit()
            logger.info(
                "Bulk delete committed",
                successful_count=len(results["successful"])
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to commit bulk delete",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to commit bulk delete: {str(e)}"
            )

        # Invalidate cache for all deleted suites
        for suite_id in suite_ids:
            await cache_manager.invalidate_suite_cache(suite_id)

        logger.info(
            "Bulk delete operation completed",
            total=results["total_requested"],
            successful=len(results["successful"]),
            failed=len(results["failed"]),
            not_found=len(results["not_found"])
        )

        return results

    @staticmethod
    async def bulk_execute_suites(
        suite_ids: List[int],
        db: AsyncSession,
        user_id: int,
        execution_type: str = "manual",
        environment: str = "production"
    ) -> Dict[str, Any]:
        """
        Bulk execute multiple test suites.

        Args:
            suite_ids: List of suite IDs to execute
            db: Database session
            user_id: ID of user performing the operation
            execution_type: Type of execution (manual, scheduled, ci)
            environment: Execution environment (dev, staging, production)

        Returns:
            Dictionary with operation results

        Raises:
            HTTPException: If validation fails or no suites found
        """
        logger.info(
            "Starting bulk execute operation",
            suite_ids=suite_ids,
            user_id=user_id,
            execution_type=execution_type,
            environment=environment,
            count=len(suite_ids)
        )

        # Validate input
        if not suite_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No suite IDs provided"
            )

        if len(suite_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot execute more than 50 suites at once"
            )

        # Validate all suite IDs are unique
        if len(set(suite_ids)) != len(suite_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate suite IDs detected"
            )

        # Validate execution_type
        valid_execution_types = ["manual", "scheduled", "ci"]
        if execution_type not in valid_execution_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid execution_type. Must be one of: {', '.join(valid_execution_types)}"
            )

        # Validate environment
        valid_environments = ["dev", "staging", "production"]
        if environment not in valid_environments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid environment. Must be one of: {', '.join(valid_environments)}"
            )

        results = {
            "total_requested": len(suite_ids),
            "successful": [],
            "failed": [],
            "not_found": []
        }

        # Process each suite
        for suite_id in suite_ids:
            try:
                # Get suite
                result = await db.execute(
                    select(TestSuite).where(
                        and_(
                            TestSuite.id == suite_id,
                            TestSuite.is_active == True
                        )
                    )
                )
                suite = result.scalar_one_or_none()

                if not suite:
                    results["not_found"].append({
                        "suite_id": suite_id,
                        "reason": "Suite not found or inactive"
                    })
                    logger.warning(
                        "Suite not found or inactive during bulk execute",
                        suite_id=suite_id
                    )
                    continue

                # Create execution
                execution_data = TestExecutionCreate(
                    suite_id=suite_id,
                    execution_type=execution_type,
                    environment=environment
                )

                execution = await create_execution_service(
                    execution_data,
                    user_id,
                    db
                )

                results["successful"].append({
                    "suite_id": suite_id,
                    "suite_name": suite.name,
                    "execution_id": execution.id,
                    "status": execution.status
                })

                logger.info(
                    "Execution created in bulk operation",
                    suite_id=suite_id,
                    suite_name=suite.name,
                    execution_id=execution.id
                )

            except HTTPException as e:
                results["failed"].append({
                    "suite_id": suite_id,
                    "reason": e.detail
                })
                logger.error(
                    "Failed to execute suite in bulk operation",
                    suite_id=suite_id,
                    error=e.detail
                )
            except Exception as e:
                results["failed"].append({
                    "suite_id": suite_id,
                    "reason": str(e)
                })
                logger.error(
                    "Failed to execute suite in bulk operation",
                    suite_id=suite_id,
                    error=str(e),
                    exc_info=True
                )

        logger.info(
            "Bulk execute operation completed",
            total=results["total_requested"],
            successful=len(results["successful"]),
            failed=len(results["failed"]),
            not_found=len(results["not_found"])
        )

        return results

    @staticmethod
    async def bulk_archive_suites(
        suite_ids: List[int],
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Bulk archive multiple test suites.

        Archiving marks suites as inactive and moves them to archive storage.
        This is different from delete as it preserves execution history.

        Args:
            suite_ids: List of suite IDs to archive
            db: Database session
            user_id: ID of user performing the operation

        Returns:
            Dictionary with operation results

        Raises:
            HTTPException: If validation fails or no suites found
        """
        logger.info(
            "Starting bulk archive operation",
            suite_ids=suite_ids,
            user_id=user_id,
            count=len(suite_ids)
        )

        # Validate input
        if not suite_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No suite IDs provided"
            )

        if len(suite_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot archive more than 100 suites at once"
            )

        # Validate all suite IDs are unique
        if len(set(suite_ids)) != len(suite_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate suite IDs detected"
            )

        results = {
            "total_requested": len(suite_ids),
            "successful": [],
            "failed": [],
            "not_found": [],
            "already_archived": []
        }

        # Process each suite
        for suite_id in suite_ids:
            try:
                # Get suite
                result = await db.execute(
                    select(TestSuite).where(TestSuite.id == suite_id)
                )
                suite = result.scalar_one_or_none()

                if not suite:
                    results["not_found"].append({
                        "suite_id": suite_id,
                        "reason": "Suite not found"
                    })
                    logger.warning(
                        "Suite not found during bulk archive",
                        suite_id=suite_id
                    )
                    continue

                # Check if already archived
                if not suite.is_active:
                    results["already_archived"].append({
                        "suite_id": suite_id,
                        "name": suite.name
                    })
                    logger.info(
                        "Suite already archived",
                        suite_id=suite_id,
                        name=suite.name
                    )
                    continue

                # Check for active executions
                active_executions_result = await db.execute(
                    select(TestExecution).where(
                        and_(
                            TestExecution.suite_id == suite_id,
                            TestExecution.status == "running"
                        )
                    )
                )
                active_executions = active_executions_result.scalars().all()

                if active_executions:
                    results["failed"].append({
                        "suite_id": suite_id,
                        "name": suite.name,
                        "reason": f"Suite has {len(active_executions)} active execution(s). Stop them before archiving."
                    })
                    logger.warning(
                        "Cannot archive suite with active executions",
                        suite_id=suite_id,
                        name=suite.name,
                        active_executions=len(active_executions)
                    )
                    continue

                # Archive suite (mark as inactive)
                suite.is_active = False
                suite.updated_at = datetime.utcnow()

                # Add archive metadata to config
                if not suite.config:
                    suite.config = {}
                suite.config["archived"] = True
                suite.config["archived_at"] = datetime.utcnow().isoformat()
                suite.config["archived_by"] = user_id

                results["successful"].append({
                    "suite_id": suite_id,
                    "name": suite.name
                })

                logger.info(
                    "Suite archived in bulk operation",
                    suite_id=suite_id,
                    name=suite.name
                )

            except Exception as e:
                results["failed"].append({
                    "suite_id": suite_id,
                    "reason": str(e)
                })
                logger.error(
                    "Failed to archive suite in bulk operation",
                    suite_id=suite_id,
                    error=str(e),
                    exc_info=True
                )

        # Commit changes
        try:
            await db.commit()
            logger.info(
                "Bulk archive committed",
                successful_count=len(results["successful"])
            )
        except Exception as e:
            await db.rollback()
            logger.error(
                "Failed to commit bulk archive",
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to commit bulk archive: {str(e)}"
            )

        # Invalidate cache for all archived suites
        for suite_id in suite_ids:
            await cache_manager.invalidate_suite_cache(suite_id)

        logger.info(
            "Bulk archive operation completed",
            total=results["total_requested"],
            successful=len(results["successful"]),
            failed=len(results["failed"]),
            not_found=len(results["not_found"]),
            already_archived=len(results["already_archived"])
        )

        return results


# Convenience functions for direct import
async def bulk_delete_suites(
    suite_ids: List[int],
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    """Convenience function for bulk delete."""
    return await BulkService.bulk_delete_suites(suite_ids, db, user_id)


async def bulk_execute_suites(
    suite_ids: List[int],
    db: AsyncSession,
    user_id: int,
    execution_type: str = "manual",
    environment: str = "production"
) -> Dict[str, Any]:
    """Convenience function for bulk execute."""
    return await BulkService.bulk_execute_suites(
        suite_ids, db, user_id, execution_type, environment
    )


async def bulk_archive_suites(
    suite_ids: List[int],
    db: AsyncSession,
    user_id: int
) -> Dict[str, Any]:
    """Convenience function for bulk archive."""
    return await BulkService.bulk_archive_suites(suite_ids, db, user_id)
