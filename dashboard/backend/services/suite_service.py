"""
Test Suite Service

Provides test suite management functionality with Redis caching.
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import TestSuite, TestCase
from schemas import TestSuiteCreate, TestSuiteUpdate
from core.logging_config import get_logger
from core.cache import cache_manager, CacheManager

# Initialize logger
logger = get_logger(__name__)


async def create_suite_service(
    suite_data: TestSuiteCreate, user_id: int, db: AsyncSession
) -> TestSuite:
    """Create a new test suite"""
    logger.info(
        "Creating new test suite",
        name=suite_data.name,
        framework_type=suite_data.framework_type,
        user_id=user_id,
    )

    db_suite = TestSuite(
        name=suite_data.name,
        description=suite_data.description,
        framework_type=suite_data.framework_type,
        config=suite_data.config,
        created_by=user_id,
    )

    db.add(db_suite)
    await db.commit()
    await db.refresh(db_suite)

    # Invalidate suite list cache
    await cache_manager.invalidate_suite_cache()

    logger.info(
        "Test suite created successfully",
        suite_id=db_suite.id,
        name=db_suite.name,
        user_id=user_id,
    )

    return db_suite


async def list_suites_service(
    skip: int = 0, limit: int = 100, db: AsyncSession = None
) -> List[TestSuite]:
    """List all test suites with pagination (cached)"""
    logger.debug("Listing test suites", skip=skip, limit=limit)

    # Generate cache key
    cache_key = cache_manager.get_suite_list_key(skip, limit)

    # Try to get from cache
    cached_suites = await cache_manager.async_get(cache_key)
    if cached_suites is not None:
        logger.info("Test suites retrieved from cache", count=len(cached_suites))
        return cached_suites

    # Fetch from database
    result = await db.execute(
        select(TestSuite)
        .where(TestSuite.is_active == True)
        .options(selectinload(TestSuite.tests))
        .offset(skip)
        .limit(limit)
        .order_by(TestSuite.created_at.desc())
    )
    suites = result.scalars().all()

    # Cache the results
    await cache_manager.async_set(cache_key, suites, ttl=CacheManager.MEDIUM_TTL)

    logger.info(
        "Test suites listed successfully", count=len(suites), skip=skip, limit=limit
    )

    return suites


async def get_suite_by_id(suite_id: int, db: AsyncSession) -> TestSuite:
    """Get a test suite by ID (cached)"""
    logger.debug("Getting test suite by ID", suite_id=suite_id)

    # Generate cache key
    cache_key = cache_manager.get_suite_key(suite_id)

    # Try to get from cache
    cached_suite = await cache_manager.async_get(cache_key)
    if cached_suite is not None:
        logger.debug("Test suite retrieved from cache", suite_id=suite_id)
        return cached_suite

    # Fetch from database
    result = await db.execute(
        select(TestSuite)
        .where(TestSuite.id == suite_id)
        .options(selectinload(TestSuite.tests))
    )
    suite = result.scalar_one_or_none()

    if not suite:
        logger.error("Test suite not found", suite_id=suite_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Test suite not found"
        )

    # Cache the result
    await cache_manager.async_set(cache_key, suite, ttl=CacheManager.MEDIUM_TTL)

    logger.debug(
        "Test suite retrieved successfully", suite_id=suite_id, name=suite.name
    )

    return suite


async def update_suite_service(
    suite_id: int, suite_update: TestSuiteUpdate, db: AsyncSession
) -> TestSuite:
    """Update a test suite"""
    logger.info("Updating test suite", suite_id=suite_id)

    suite = await get_suite_by_id(suite_id, db)

    # Update fields
    updated_fields = []
    if suite_update.name is not None:
        logger.info(
            "Updating suite name",
            suite_id=suite_id,
            old_name=suite.name,
            new_name=suite_update.name,
        )
        suite.name = suite_update.name
        updated_fields.append("name")
    if suite_update.description is not None:
        logger.info("Updating suite description", suite_id=suite_id)
        suite.description = suite_update.description
        updated_fields.append("description")
    if suite_update.framework_type is not None:
        logger.info(
            "Updating suite framework type",
            suite_id=suite_id,
            old_type=suite.framework_type,
            new_type=suite_update.framework_type,
        )
        suite.framework_type = suite_update.framework_type
        updated_fields.append("framework_type")
    if suite_update.config is not None:
        logger.info("Updating suite config", suite_id=suite_id)
        suite.config = suite_update.config
        updated_fields.append("config")
    if suite_update.is_active is not None:
        logger.info(
            "Updating suite active status",
            suite_id=suite_id,
            old_status=suite.is_active,
            new_status=suite_update.is_active,
        )
        suite.is_active = suite_update.is_active
        updated_fields.append("is_active")

    await db.commit()
    await db.refresh(suite)

    # Invalidate suite cache
    await cache_manager.invalidate_suite_cache(suite_id)

    logger.info(
        "Test suite updated successfully",
        suite_id=suite_id,
        updated_fields=updated_fields,
    )

    return suite


async def delete_suite_service(suite_id: int, db: AsyncSession) -> None:
    """Delete a test suite (soft delete)"""
    logger.info("Soft deleting test suite", suite_id=suite_id)

    suite = await get_suite_by_id(suite_id, db)

    logger.info(
        "Marking suite as inactive",
        suite_id=suite_id,
        current_name=suite.name,
        current_status=suite.is_active,
    )

    suite.is_active = False
    await db.commit()

    # Invalidate suite cache
    await cache_manager.invalidate_suite_cache(suite_id)

    logger.info(
        "Test suite soft deleted successfully", suite_id=suite_id, name=suite.name
    )
