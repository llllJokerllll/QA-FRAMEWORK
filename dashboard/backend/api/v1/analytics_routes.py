"""
Analytics Routes

API endpoints for business analytics and metrics
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from services.auth_service import get_current_user
from services.analytics_service import (
    get_analytics_service,
    get_user_analytics,
    get_test_analytics,
    get_revenue_analytics,
    get_feature_usage_analytics,
    get_dashboard_summary
)
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get comprehensive dashboard analytics
    
    Returns:
        - summary: Key metrics (users, executions, MRR, subscribers)
        - trends: Growth trends (signups, executions, revenue)
        - features: Feature usage stats
        - top_projects: Most active projects
    """
    try:
        logger.info(f"Dashboard analytics requested by user {current_user.id}")
        
        analytics = await get_dashboard_summary(db)
        
        return {
            "success": True,
            "data": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get user analytics
    
    Query params:
        - start_date: Start date for analytics period (optional)
        - end_date: End date for analytics period (optional)
    
    Returns:
        - total_users: Total number of users
        - new_signups: New signups in period
        - active_users: Users with activity in period
        - churned_users: Users who cancelled subscriptions
        - signup_trend: Daily signup counts
        - active_trend: Daily active user counts
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        logger.info(f"User analytics requested by user {current_user.id}")
        
        analytics = await get_user_analytics(db, start, end)
        
        return {
            "success": True,
            "data": analytics
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tests")
async def get_tests_analytics(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get test execution analytics
    
    Query params:
        - user_id: Filter by specific user (optional)
        - start_date: Start date for analytics period (optional)
        - end_date: End date for analytics period (optional)
    
    Returns:
        - total_executions: Total test executions
        - passed: Number of passed tests
        - failed: Number of failed tests
        - success_rate: Overall success rate
        - avg_duration: Average execution duration
        - executions_trend: Daily execution counts
        - top_projects: Most active projects
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Non-admin users can only see their own analytics
        filter_user_id = user_id
        if current_user.role != 'admin':
            filter_user_id = current_user.id
        
        logger.info(f"Test analytics requested by user {current_user.id}")
        
        analytics = await get_test_analytics(db, filter_user_id, start, end)
        
        return {
            "success": True,
            "data": analytics
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting test analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
async def get_revenue_analytics_endpoint(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get revenue and subscription analytics
    
    Query params:
        - start_date: Start date for analytics period (optional)
        - end_date: End date for analytics period (optional)
    
    Returns:
        - mrr: Monthly recurring revenue
        - arr: Annual recurring revenue
        - total_subscribers: Total paying subscribers
        - subscribers_by_plan: Subscribers breakdown by plan
        - revenue_trend: Monthly revenue trend
        - ltv_estimate: Customer lifetime value estimate
    
    Note: Admin only endpoint
    """
    try:
        # Only admins can view revenue analytics
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        logger.info(f"Revenue analytics requested by admin {current_user.id}")
        
        analytics = await get_revenue_analytics(db, start, end)
        
        return {
            "success": True,
            "data": analytics
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features")
async def get_features_analytics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get feature usage analytics
    
    Query params:
        - start_date: Start date for analytics period (optional)
        - end_date: End date for analytics period (optional)
    
    Returns:
        - feature_usage: Usage stats per feature
        - adoption_rates: Feature adoption rates
        - total_users: Total users for adoption calculation
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        logger.info(f"Feature analytics requested by user {current_user.id}")
        
        analytics = await get_feature_usage_analytics(db, start, end)
        
        return {
            "success": True,
            "data": analytics
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        logger.error(f"Error getting feature analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_analytics(
    report_type: str = Query(..., description="Report type: dashboard, users, tests, revenue, features"),
    format: str = Query("json", description="Export format: json, csv"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Export analytics report
    
    Query params:
        - report_type: Type of report to export
        - format: Export format (json or csv)
        - start_date: Start date for report period (optional)
        - end_date: End date for report period (optional)
    
    Returns:
        - Exported data in requested format
    """
    try:
        # Parse dates
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        # Get data based on report type
        if report_type == "dashboard":
            data = await get_dashboard_summary(db)
        elif report_type == "users":
            data = await get_user_analytics(db, start, end)
        elif report_type == "tests":
            data = await get_test_analytics(db, None, start, end)
        elif report_type == "revenue":
            if current_user.role != 'admin':
                raise HTTPException(status_code=403, detail="Admin access required")
            data = await get_revenue_analytics(db, start, end)
        elif report_type == "features":
            data = await get_feature_usage_analytics(db, start, end)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid report type: {report_type}")
        
        logger.info(f"Analytics export requested by user {current_user.id}: {report_type}")
        
        # Format output
        if format == "csv":
            # Convert to CSV (simplified - real implementation would use pandas or csv module)
            import io
            import csv
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Flatten nested dict for CSV
            def flatten_dict(d, parent_key='', sep='_'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            
            flat_data = flatten_dict(data)
            
            # Write CSV
            writer.writerow(flat_data.keys())
            writer.writerow(flat_data.values())
            
            return {
                "success": True,
                "format": "csv",
                "data": output.getvalue()
            }
        else:
            return {
                "success": True,
                "format": "json",
                "data": data
            }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
