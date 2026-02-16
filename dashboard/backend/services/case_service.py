"""
Test Case Service

Provides test case management functionality with Redis caching.
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import TestCase, TestSuite
from schemas import TestCaseCreate, TestCaseUpdate
from core.logging_config import get_logger
from core.cache import cache_manager, CacheManager

# Initialize logger
logger = get_logger(__name__)


async def create_case_service(case_data: TestCaseCreate, db: AsyncSession) -> TestCase:
    """Create a new test case"""
    logger.info(
        "Creating new test case",
        suite_id=case_data.suite_id,
        name=case_data.name,
        test_type=case_data.test_type,
        priority=case_data.priority,
    )

    # Verify suite exists
    result = await db.execute(
        select(TestSuite).where(TestSuite.id == case_data.suite_id)
    )
    suite = result.scalar_one_or_none()

    if not suite:
        logger.error("Test suite not found", suite_id=case_data.suite_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test suite not found"
        )

    db_case = TestCase(
        suite_id=case_data.suite_id,
        name=case_data.name,
        description=case_data.description,
        test_code=case_data.test_code,
        test_type=case_data.test_type,
        priority=case_data.priority,
        tags=case_data.tags,
    )

    db.add(db_case)
    await db.commit()
    await db.refresh(db_case)

    # Invalidate case cache for the suite
    await cache_manager.invalidate_case_cache(suite_id=case_data.suite_id)

    logger.info(
        "Test case created successfully",
        case_id=db_case.id,
        suite_id=db_case.suite_id,
        name=db_case.name,
    )

    return db_case


async def list_cases_service(
    suite_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = None,
) -> List[TestCase]:
    """List test cases with optional suite filter (cached)"""
    logger.info("Listing test cases", suite_id=suite_id, skip=skip, limit=limit)

    # Generate cache key
    cache_key = cache_manager.get_case_list_key(suite_id, skip, limit)

    # Try to get from cache
    cached_cases = await cache_manager.async_get(cache_key)
    if cached_cases is not None:
        logger.info("Test cases retrieved from cache", count=len(cached_cases))
        return cached_cases

    # Fetch from database
    query = select(TestCase).where(TestCase.is_active == True)

    if suite_id:
        query = query.where(TestCase.suite_id == suite_id)

    result = await db.execute(
        query.options(selectinload(TestCase.suite))
        .offset(skip)
        .limit(limit)
        .order_by(TestCase.created_at.desc())
    )
    cases = result.scalars().all()

    # Cache the results
    await cache_manager.async_set(cache_key, cases, ttl=CacheManager.MEDIUM_TTL)

    logger.info("Test cases listed successfully", count=len(cases), suite_id=suite_id)

    return cases


async def get_case_by_id(case_id: int, db: AsyncSession) -> TestCase:
    """Get a test case by ID (cached)"""
    logger.info("Getting test case by ID", case_id=case_id)

    # Generate cache key
    cache_key = cache_manager.get_case_key(case_id)

    # Try to get from cache
    cached_case = await cache_manager.async_get(cache_key)
    if cached_case is not None:
        logger.debug("Test case retrieved from cache", case_id=case_id)
        return cached_case

    # Fetch from database
    result = await db.execute(
        select(TestCase)
        .where(TestCase.id == case_id)
        .options(selectinload(TestCase.suite))
    )
    case = result.scalar_one_or_none()

    if not case:
        logger.error("Test case not found", case_id=case_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test case not found"
        )

    # Cache the result
    await cache_manager.async_set(cache_key, case, ttl=CacheManager.MEDIUM_TTL)

    logger.info("Test case retrieved successfully", case_id=case_id, name=case.name)

    return case


async def update_case_service(
    case_id: int, case_update: TestCaseUpdate, db: AsyncSession
) -> TestCase:
    """Update a test case"""
    logger.info("Updating test case", case_id=case_id)

    case = await get_case_by_id(case_id, db)

    # Update fields
    if case_update.name is not None:
        logger.info(
            "Updating case name",
            case_id=case_id,
            old_name=case.name,
            new_name=case_update.name,
        )
        case.name = case_update.name
    if case_update.description is not None:
        logger.info("Updating case description", case_id=case_id)
        case.description = case_update.description
    if case_update.test_code is not None:
        logger.info("Updating case test code", case_id=case_id)
        case.test_code = case_update.test_code
    if case_update.test_type is not None:
        logger.info(
            "Updating case test type",
            case_id=case_id,
            old_type=case.test_type,
            new_type=case_update.test_type,
        )
        case.test_type = case_update.test_type
    if case_update.priority is not None:
        logger.info(
            "Updating case priority",
            case_id=case_id,
            old_priority=case.priority,
            new_priority=case_update.priority,
        )
        case.priority = case_update.priority
    if case_update.tags is not None:
        logger.info(
            "Updating case tags",
            case_id=case_id,
            old_tags=case.tags,
            new_tags=case_update.tags,
        )
        case.tags = case_update.tags
    if case_update.is_active is not None:
        logger.info(
            "Updating case active status",
            case_id=case_id,
            old_status=case.is_active,
            new_status=case_update.is_active,
        )
        case.is_active = case_update.is_active

    await db.commit()
    await db.refresh(case)

    # Invalidate case cache
    await cache_manager.invalidate_case_cache(case_id, case.suite_id)

    logger.info(
        "Test case updated successfully",
        case_id=case_id,
        updated_fields=case_update.model_dump(exclude_unset=True),
    )

    return case


async def delete_case_service(case_id: int, db: AsyncSession) -> None:
    """Delete a test case (soft delete)"""
    logger.info("Soft deleting test case", case_id=case_id)

    case = await get_case_by_id(case_id, db)

    logger.info(
        "Marking case as inactive",
        case_id=case_id,
        current_name=case.name,
        current_status=case.is_active,
    )

    case.is_active = False
    await db.commit()

    # Invalidate case cache
    await cache_manager.invalidate_case_cache(case_id, case.suite_id)

    logger.info("Test case soft deleted successfully", case_id=case_id)
