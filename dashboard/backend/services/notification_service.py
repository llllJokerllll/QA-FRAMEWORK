"""
Notification Service

Handles notifications for:
- Test completion
- Flaky test detection
- Subscription expiring
- Weekly digest
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from models import User, TestExecution, TestSuite
from services.email_service import send_email

logger = structlog.get_logger()


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_test_completion_notification(
        self,
        execution: TestExecution,
        suite: TestSuite,
        user: User
    ):
        """Send notification when test execution completes"""
        
        status_emoji = "✅" if execution.status == "passed" else "❌"
        subject = f"{status_emoji} Test Suite Completed: {suite.name}"
        
        body = f"""
Your test suite "{suite.name}" has completed.

Status: {execution.status.upper()}
Total Tests: {execution.total_tests}
Passed: {execution.passed_tests}
Failed: {execution.failed_tests}
Duration: {execution.duration}s

View results: https://qa-framework.io/executions/{execution.id}
        """
        
        await send_email(
            to=user.email,
            subject=subject,
            body=body
        )
        
        logger.info(
            "Test completion notification sent",
            user_id=user.id,
            execution_id=execution.id,
            status=execution.status
        )
    
    async def send_flaky_test_notification(
        self,
        test_name: str,
        suite_name: str,
        user: User
    ):
        """Send notification when flaky test is detected"""
        
        subject = f"⚠️ Flaky Test Detected: {test_name}"
        
        body = f"""
A flaky test has been detected in your suite "{suite_name}".

Test: {test_name}
Detection Time: {datetime.utcnow().isoformat()}

Flaky tests have inconsistent results and should be investigated.

View details: https://qa-framework.io/tests/flaky
        """
        
        await send_email(
            to=user.email,
            subject=subject,
            body=body
        )
        
        logger.info(
            "Flaky test notification sent",
            user_id=user.id,
            test_name=test_name
        )
    
    async def send_subscription_expiring_notification(
        self,
        user: User,
        days_remaining: int
    ):
        """Send notification before subscription expires"""
        
        subject = f"⏰ Subscription Expiring in {days_remaining} Days"
        
        body = f"""
Your QA-FRAMEWORK subscription will expire in {days_remaining} days.

Current Plan: {user.subscription_plan.upper()}
Expiry Date: {user.subscription_current_period_end}

To avoid interruption, please renew your subscription:
https://qa-framework.io/billing

Thank you for using QA-FRAMEWORK!
        """
        
        await send_email(
            to=user.email,
            subject=subject,
            body=body
        )
        
        logger.info(
            "Subscription expiring notification sent",
            user_id=user.id,
            days_remaining=days_remaining
        )
    
    async def send_weekly_digest(
        self,
        user: User
    ):
        """Send weekly summary of activity"""
        
        # Get last 7 days stats
        start_date = datetime.utcnow() - timedelta(days=7)
        
        result = await self.db.execute(
            select(
                func.count(TestExecution.id).label('total'),
                func.sum(
                    func.case((TestExecution.status == 'passed', 1), else_=0)
                ).label('passed')
            )
            .join(TestSuite)
            .where(and_(
                TestSuite.created_by == user.id,
                TestExecution.started_at >= start_date
            ))
        )
        
        stats = result.first()
        
        total_executions = stats.total or 0
        passed_executions = stats.passed or 0
        success_rate = (passed_executions / total_executions * 100) if total_executions > 0 else 0
        
        subject = "📊 Your Weekly QA-FRAMEWORK Summary"
        
        body = f"""
Here's your weekly summary for QA-FRAMEWORK:

Total Test Executions: {total_executions}
Success Rate: {success_rate:.1f}%
Tests Passed: {passed_executions}
Tests Failed: {total_executions - passed_executions}

Time Saved: ~{(total_executions * 5) // 60} hours

Keep up the great testing! 🚀

View full report: https://qa-framework.io/analytics
        """
        
        await send_email(
            to=user.email,
            subject=subject,
            body=body
        )
        
        logger.info(
            "Weekly digest sent",
            user_id=user.id,
            total_executions=total_executions
        )
    
    async def get_notification_preferences(
        self,
        user_id: int
    ) -> Dict[str, bool]:
        """Get user notification preferences"""
        # Placeholder - would be stored in database
        return {
            "test_completion": True,
            "flaky_test_detected": True,
            "subscription_expiring": True,
            "weekly_digest": False
        }
    
    async def update_notification_preferences(
        self,
        user_id: int,
        preferences: Dict[str, bool]
    ):
        """Update user notification preferences"""
        # Placeholder - would update database
        logger.info(
            "Notification preferences updated",
            user_id=user_id,
            preferences=preferences
        )
        return preferences
