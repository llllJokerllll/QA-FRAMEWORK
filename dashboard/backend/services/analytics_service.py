"""
Analytics Service

Provides business analytics and metrics tracking:
- User analytics (signups, active users, churn)
- Test analytics (executions, success rates, trends)
- Revenue analytics (MRR, LTV, CAC)
- Feature usage analytics
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

from models import User, TestExecution, Project, Subscription, UsageRecord
from core.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    """Service for business analytics and metrics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get user analytics for a time period
        
        Returns:
            - total_users: Total number of users
            - new_signups: New signups in period
            - active_users: Users with activity in period
            - churned_users: Users who cancelled subscriptions
            - signup_trend: Daily signup counts
            - active_trend: Daily active user counts
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Total users
        total_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_result.scalar() or 0
        
        # New signups in period
        new_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            )
        )
        new_signups = new_result.scalar() or 0
        
        # Active users (users with executions in period)
        active_result = await self.db.execute(
            select(func.count(func.distinct(TestExecution.user_id))).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date
                )
            )
        )
        active_users = active_result.scalar() or 0
        
        # Churned users (cancelled subscriptions in period)
        churned_result = await self.db.execute(
            select(func.count(func.distinct(Subscription.user_id))).where(
                and_(
                    Subscription.status == 'cancelled',
                    Subscription.updated_at >= start_date,
                    Subscription.updated_at <= end_date
                )
            )
        )
        churned_users = churned_result.scalar() or 0
        
        # Daily signup trend
        signup_trend_result = await self.db.execute(
            select(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).where(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            ).group_by(func.date(User.created_at)).order_by(func.date(User.created_at))
        )
        signup_trend = [
            {"date": str(row.date), "count": row.count}
            for row in signup_trend_result
        ]
        
        # Daily active users trend
        active_trend_result = await self.db.execute(
            select(
                func.date(TestExecution.created_at).label('date'),
                func.count(func.distinct(TestExecution.user_id)).label('count')
            ).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date
                )
            ).group_by(func.date(TestExecution.created_at)).order_by(func.date(TestExecution.created_at))
        )
        active_trend = [
            {"date": str(row.date), "count": row.count}
            for row in active_trend_result
        ]
        
        return {
            "total_users": total_users,
            "new_signups": new_signups,
            "active_users": active_users,
            "churned_users": churned_users,
            "churn_rate": round((churned_users / total_users * 100) if total_users > 0 else 0, 2),
            "signup_trend": signup_trend,
            "active_trend": active_trend,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_test_analytics(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get test execution analytics
        
        Returns:
            - total_executions: Total test executions
            - passed: Number of passed tests
            - failed: Number of failed tests
            - success_rate: Overall success rate
            - avg_duration: Average execution duration
            - executions_trend: Daily execution counts
            - top_projects: Most active projects
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Build base query with filters
        base_query = select(TestExecution).where(
            and_(
                TestExecution.created_at >= start_date,
                TestExecution.created_at <= end_date
            )
        )
        
        if user_id:
            base_query = base_query.where(TestExecution.user_id == user_id)
        
        # Total executions
        total_result = await self.db.execute(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            )
        )
        total_executions = total_result.scalar() or 0
        
        # Passed tests
        passed_result = await self.db.execute(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    TestExecution.status == 'passed',
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            )
        )
        passed = passed_result.scalar() or 0
        
        # Failed tests
        failed_result = await self.db.execute(
            select(func.count(TestExecution.id)).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    TestExecution.status == 'failed',
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            )
        )
        failed = failed_result.scalar() or 0
        
        # Success rate
        success_rate = round((passed / total_executions * 100) if total_executions > 0 else 0, 2)
        
        # Average duration
        avg_result = await self.db.execute(
            select(func.avg(TestExecution.duration)).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    TestExecution.duration.isnot(None),
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            )
        )
        avg_duration = avg_result.scalar() or 0.0
        
        # Daily executions trend
        trend_result = await self.db.execute(
            select(
                func.date(TestExecution.created_at).label('date'),
                func.count(TestExecution.id).label('total'),
                func.sum(
                    func.case((TestExecution.status == 'passed', 1), else_=0)
                ).label('passed'),
                func.sum(
                    func.case((TestExecution.status == 'failed', 1), else_=0)
                ).label('failed')
            ).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            ).group_by(func.date(TestExecution.created_at)).order_by(func.date(TestExecution.created_at))
        )
        
        executions_trend = [
            {
                "date": str(row.date),
                "total": row.total,
                "passed": row.passed or 0,
                "failed": row.failed or 0,
                "success_rate": round((row.passed / row.total * 100) if row.total > 0 else 0, 2)
            }
            for row in trend_result
        ]
        
        # Top projects
        top_projects_result = await self.db.execute(
            select(
                Project.name,
                func.count(TestExecution.id).label('execution_count')
            ).join(TestExecution).where(
                and_(
                    TestExecution.created_at >= start_date,
                    TestExecution.created_at <= end_date,
                    *([TestExecution.user_id == user_id] if user_id else [])
                )
            ).group_by(Project.id).order_by(func.count(TestExecution.id).desc()).limit(5)
        )
        
        top_projects = [
            {"name": row.name, "executions": row.execution_count}
            for row in top_projects_result
        ]
        
        return {
            "total_executions": total_executions,
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "avg_duration_seconds": round(avg_duration, 2),
            "executions_trend": executions_trend,
            "top_projects": top_projects,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_revenue_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get revenue and subscription analytics
        
        Returns:
            - mrr: Monthly recurring revenue
            - arr: Annual recurring revenue
            - total_subscribers: Total paying subscribers
            - subscribers_by_plan: Subscribers breakdown by plan
            - revenue_trend: Monthly revenue trend
            - ltv_estimate: Customer lifetime value estimate
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=365)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Plan prices (from Stripe)
        PLAN_PRICES = {
            'free': 0,
            'pro': 99,
            'enterprise': 499
        }
        
        # Active subscribers by plan
        subscribers_result = await self.db.execute(
            select(
                Subscription.plan_type,
                func.count(Subscription.id).label('count')
            ).where(
                Subscription.status == 'active'
            ).group_by(Subscription.plan_type)
        )
        
        subscribers_by_plan = {}
        mrr = 0
        
        for row in subscribers_result:
            plan = row.plan_type or 'free'
            count = row.count
            subscribers_by_plan[plan] = count
            mrr += count * PLAN_PRICES.get(plan, 0)
        
        # Total subscribers
        total_subscribers = sum(subscribers_by_plan.values())
        
        # ARR (Annual Recurring Revenue)
        arr = mrr * 12
        
        # Revenue trend (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        revenue_trend_result = await self.db.execute(
            select(
                func.strftime('%Y-%m', Subscription.created_at).label('month'),
                func.count(Subscription.id).label('new_subscribers')
            ).where(
                and_(
                    Subscription.created_at >= six_months_ago,
                    Subscription.status == 'active'
                )
            ).group_by(func.strftime('%Y-%m', Subscription.created_at)).order_by('month')
        )
        
        revenue_trend = []
        for row in revenue_trend_result:
            # Estimate MRR for each month based on new subscribers
            # (simplified - real implementation would use actual payment data)
            avg_plan_price = 150  # Average of pro and enterprise
            estimated_mrr = row.new_subscribers * avg_plan_price
            revenue_trend.append({
                "month": row.month,
                "new_subscribers": row.new_subscribers,
                "estimated_mrr": estimated_mrr
            })
        
        # LTV Estimate (simplified)
        # LTV = ARPU * Average Customer Lifespan
        # Assumptions: avg_lifespan = 24 months, ARPU = MRR / total_subscribers
        avg_lifespan_months = 24
        arpu = (mrr / total_subscribers) if total_subscribers > 0 else 0
        ltv_estimate = arpu * avg_lifespan_months
        
        return {
            "mrr": mrr,
            "arr": arr,
            "total_subscribers": total_subscribers,
            "subscribers_by_plan": subscribers_by_plan,
            "revenue_trend": revenue_trend,
            "arpu": round(arpu, 2),
            "ltv_estimate": round(ltv_estimate, 2),
            "currency": "USD",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_feature_usage_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get feature usage analytics
        
        Returns:
            - ai_test_generation: Usage stats for AI test generation
            - self_healing: Usage stats for self-healing tests
            - flaky_detection: Usage stats for flaky test detection
            - ci_integrations: CI/CD integration stats
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Feature usage from usage_records
        usage_result = await self.db.execute(
            select(
                UsageRecord.feature_name,
                func.count(UsageRecord.id).label('usage_count'),
                func.count(func.distinct(UsageRecord.user_id)).label('unique_users')
            ).where(
                and_(
                    UsageRecord.created_at >= start_date,
                    UsageRecord.created_at <= end_date
                )
            ).group_by(UsageRecord.feature_name)
        )
        
        feature_usage = {}
        for row in usage_result:
            feature_usage[row.feature_name] = {
                "usage_count": row.usage_count,
                "unique_users": row.unique_users
            }
        
        # Default values for known features
        known_features = [
            'ai_test_generation',
            'self_healing',
            'flaky_detection',
            'parallel_execution',
            'ci_integration',
            'api_usage'
        ]
        
        for feature in known_features:
            if feature not in feature_usage:
                feature_usage[feature] = {
                    "usage_count": 0,
                    "unique_users": 0
                }
        
        # Calculate adoption rates
        total_users_result = await self.db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 1
        
        adoption_rates = {
            feature: round((data['unique_users'] / total_users * 100), 2)
            for feature, data in feature_usage.items()
        }
        
        return {
            "feature_usage": feature_usage,
            "adoption_rates": adoption_rates,
            "total_users": total_users,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard summary
        
        Combines all analytics into a single dashboard view
        """
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Get all analytics
        user_analytics = await self.get_user_analytics(last_30_days, now)
        test_analytics = await self.get_test_analytics(None, last_30_days, now)
        revenue_analytics = await self.get_revenue_analytics(last_30_days, now)
        feature_analytics = await self.get_feature_usage_analytics(last_7_days, now)
        
        # Calculate growth metrics
        previous_month_start = last_30_days - timedelta(days=30)
        previous_month_end = last_30_days
        
        previous_user_analytics = await self.get_user_analytics(previous_month_start, previous_month_end)
        
        user_growth = 0
        if previous_user_analytics['new_signups'] > 0:
            user_growth = round(
                ((user_analytics['new_signups'] - previous_user_analytics['new_signups']) /
                 previous_user_analytics['new_signups'] * 100),
                2
            )
        
        return {
            "summary": {
                "total_users": user_analytics['total_users'],
                "active_users": user_analytics['active_users'],
                "total_executions": test_analytics['total_executions'],
                "success_rate": test_analytics['success_rate'],
                "mrr": revenue_analytics['mrr'],
                "total_subscribers": revenue_analytics['total_subscribers']
            },
            "trends": {
                "user_growth_percent": user_growth,
                "signup_trend": user_analytics['signup_trend'][:7],  # Last 7 days
                "execution_trend": test_analytics['executions_trend'][:7],
                "revenue_trend": revenue_analytics['revenue_trend'][:6]  # Last 6 months
            },
            "features": feature_analytics['feature_usage'],
            "top_projects": test_analytics['top_projects'],
            "period": {
                "current": {
                    "start": last_30_days.isoformat(),
                    "end": now.isoformat()
                },
                "previous": {
                    "start": previous_month_start.isoformat(),
                    "end": previous_month_end.isoformat()
                }
            },
            "generated_at": now.isoformat()
        }


# Factory function
def get_analytics_service(db: AsyncSession) -> AnalyticsService:
    """Get analytics service instance"""
    return AnalyticsService(db)


# Export convenience functions
async def get_user_analytics(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get user analytics"""
    service = AnalyticsService(db)
    return await service.get_user_analytics(start_date, end_date)


async def get_test_analytics(db: AsyncSession, user_id: Optional[int] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get test analytics"""
    service = AnalyticsService(db)
    return await service.get_test_analytics(user_id, start_date, end_date)


async def get_revenue_analytics(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get revenue analytics"""
    service = AnalyticsService(db)
    return await service.get_revenue_analytics(start_date, end_date)


async def get_feature_usage_analytics(db: AsyncSession, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Get feature usage analytics"""
    service = AnalyticsService(db)
    return await service.get_feature_usage_analytics(start_date, end_date)


async def get_dashboard_summary(db: AsyncSession) -> Dict[str, Any]:
    """Get dashboard summary"""
    service = AnalyticsService(db)
    return await service.get_dashboard_summary()
