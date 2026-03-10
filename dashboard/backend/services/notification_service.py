"""Notification service for QA-FRAMEWORK Dashboard."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from models.notification import Notification
from models.user import User


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data or {}
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Notification], int, int]:
        """Get notifications for a user."""
        # Base query
        query = select(Notification).where(Notification.user_id == user_id)

        # Filter unread only
        if unread_only:
            query = query.where(Notification.read == False)

        # Order by created_at desc
        query = query.order_by(desc(Notification.created_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get unread count
        unread_query = select(func.count()).where(
            and_(Notification.user_id == user_id, Notification.read == False)
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar()

        # Apply pagination
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await db.execute(query)
        notifications = result.scalars().all()

        return notifications, total, unread_count

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: str,
        user_id: int
    ) -> bool:
        """Mark a notification as read."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()

        if notification:
            notification.read = True
            await db.commit()
            return True
        return False

    @staticmethod
    async def mark_all_as_read(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Mark all notifications as read for a user."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read == False
                )
            )
        )
        notifications = result.scalars().all()

        count = 0
        for notification in notifications:
            notification.read = True
            count += 1

        await db.commit()
        return count

    @staticmethod
    async def delete_notification(
        db: AsyncSession,
        notification_id: str,
        user_id: int
    ) -> bool:
        """Delete a notification."""
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
        )
        notification = result.scalar_one_or_none()

        if notification:
            await db.delete(notification)
            await db.commit()
            return True
        return False

    @staticmethod
    async def create_test_completed_notification(
        db: AsyncSession,
        user_id: int,
        suite_name: str,
        suite_id: int,
        execution_id: int,
        pass_rate: float
    ) -> Notification:
        """Create notification for completed test."""
        status = "passed" if pass_rate == 100 else "completed"
        return await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type="test_completed",
            title=f"Test Suite {status.title()}",
            message=f"{suite_name} completed with {pass_rate:.1f}% pass rate",
            data={
                "suite_id": suite_id,
                "execution_id": execution_id,
                "pass_rate": pass_rate
            }
        )

    @staticmethod
    async def create_test_failed_notification(
        db: AsyncSession,
        user_id: int,
        suite_name: str,
        suite_id: int,
        execution_id: int,
        failed_tests: int
    ) -> Notification:
        """Create notification for failed test."""
        return await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type="test_failed",
            title="Test Suite Failed",
            message=f"{suite_name} failed with {failed_tests} test(s) failing",
            data={
                "suite_id": suite_id,
                "execution_id": execution_id,
                "failed_tests": failed_tests
            }
        )

    @staticmethod
    async def create_suite_created_notification(
        db: AsyncSession,
        user_id: int,
        suite_name: str,
        suite_id: int
    ) -> Notification:
        """Create notification for new test suite."""
        return await NotificationService.create_notification(
            db=db,
            user_id=user_id,
            type="suite_created",
            title="Test Suite Created",
            message=f"New test suite '{suite_name}' has been created",
            data={
                "suite_id": suite_id
            }
        )
