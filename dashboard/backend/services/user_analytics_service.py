"""
User Analytics Service

Provides user-specific analytics:
- Tests executed (7/30 days)
- Success rate
- Time saved
- Flaky tests detected
- Self-healing success rate
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from models import User, TestExecution, TestSuite

logger = structlog.get_logger()


class UserAnalyticsService:
    """Service for user-specific analytics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_stats(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user statistics for the last N days
        
        Args:
            user_id: User ID
            days: Number of days to include
        
        Returns:
            Dict with user statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total executions
        result = await self.db.execute(
            select(func.count(TestExecution.id))
            .join(TestSuite)
            .where(and_(
                TestSuite.created_by == user_id,
                TestExecution.started_at >= start_date
            ))
        )
        total_executions = result.scalar() or 0
        
        # Get successful executions
        result = await self.db.execute(
            select(func.count(TestExecution.id))
            .join(TestSuite)
            .where(and_(
                TestSuite.created_by == user_id,
                TestExecution.started_at >= start_date,
                TestExecution.status == 'passed'
            ))
        )
        successful_executions = result.scalar() or 0
        
        # Calculate success rate
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Calculate time saved (estimate: 5 min per test execution)
        time_saved_hours = (total_executions * 5) / 60
        
        # Get flaky tests detected (placeholder)
        flaky_tests = 0
        
        # Get self-healing success rate (placeholder)
        self_healing_rate = 0.0
        
        return {
            "period_days": days,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate, 1),
            "time_saved_hours": round(time_saved_hours, 1),
            "flaky_tests_detected": flaky_tests,
            "self_healing_success_rate": self_healing_rate
        }
    
    async def get_execution_trends(
        self,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get execution trends over time
        
        Args:
            user_id: User ID
            days: Number of days to include
        
        Returns:
            List of daily execution data
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily executions
        result = await self.db.execute(
            select(
                func.date(TestExecution.started_at).label('date'),
                func.count(TestExecution.id).label('total'),
                func.sum(
                    func.case((TestExecution.status == 'passed', 1), else_=0)
                ).label('passed'),
                func.sum(
                    func.case((TestExecution.status == 'failed', 1), else_=0)
                ).label('failed')
            )
            .join(TestSuite)
            .where(and_(
                TestSuite.created_by == user_id,
                TestExecution.started_at >= start_date
            ))
            .group_by(func.date(TestExecution.started_at))
            .order_by(func.date(TestExecution.started_at))
        )
        
        trends = []
        for row in result:
            trends.append({
                "date": str(row.date),
                "total": row.total,
                "passed": row.passed or 0,
                "failed": row.failed or 0,
                "success_rate": round((row.passed / row.total * 100) if row.total > 0 else 0, 1)
            })
        
        return trends
    
    async def get_suite_breakdown(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get breakdown by test suite
        
        Args:
            user_id: User ID
        
        Returns:
            List of suite statistics
        """
        result = await self.db.execute(
            select(
                TestSuite.id,
                TestSuite.name,
                func.count(TestExecution.id).label('total_executions'),
                func.avg(TestExecution.duration).label('avg_duration'),
                func.sum(
                    func.case((TestExecution.status == 'passed', 1), else_=0)
                ).label('passed'),
                func.sum(
                    func.case((TestExecution.status == 'failed', 1), else_=0)
                ).label('failed')
            )
            .join(TestExecution)
            .where(TestSuite.created_by == user_id)
            .group_by(TestSuite.id, TestSuite.name)
            .order_by(func.count(TestExecution.id).desc())
        )
        
        breakdown = []
        for row in result:
            total = row.total_executions or 0
            passed = row.passed or 0
            
            breakdown.append({
                "suite_id": row.id,
                "suite_name": row.name,
                "total_executions": total,
                "avg_duration": round(row.avg_duration or 0, 1),
                "success_rate": round((passed / total * 100) if total > 0 else 0, 1)
            })
        
        return breakdown
    
    async def get_dashboard_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard summary
        
        Args:
            user_id: User ID
        
        Returns:
            Dict with all analytics data
        """
        stats_7d = await self.get_user_stats(user_id, days=7)
        stats_30d = await self.get_user_stats(user_id, days=30)
        trends = await self.get_execution_trends(user_id, days=30)
        breakdown = await self.get_suite_breakdown(user_id)
        
        return {
            "last_7_days": stats_7d,
            "last_30_days": stats_30d,
            "trends": trends,
            "suite_breakdown": breakdown
        }
