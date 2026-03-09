"""
Audit Logging Service

Logs critical actions for security and compliance:
- Login/logout events
- Subscription changes
- API key creation/deletion
- User permission changes
- Data exports
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import structlog

logger = structlog.get_logger()

Base = declarative_base()


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="success")  # success, failure
    error_message = Column(Text, nullable=True)


class AuditService:
    """Service for logging audit events"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_event(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit event
        
        Args:
            action: Action performed (e.g., "user.login", "subscription.create")
            resource_type: Type of resource (e.g., "user", "subscription", "api_key")
            user_id: ID of user performing action
            resource_id: ID of affected resource
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional event details
            status: Event status (success, failure)
            error_message: Error message if failed
        
        Returns:
            Created audit log entry
        """
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            status=status,
            error_message=error_message
        )
        
        self.db.add(log_entry)
        await self.db.commit()
        await self.db.refresh(log_entry)
        
        logger.info(
            "Audit event logged",
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            status=status
        )
        
        return log_entry
    
    async def log_login(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str,
        success: bool = True
    ):
        """Log user login event"""
        await self.log_event(
            action="user.login",
            resource_type="user",
            user_id=user_id,
            resource_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure"
        )
    
    async def log_logout(
        self,
        user_id: int,
        ip_address: str
    ):
        """Log user logout event"""
        await self.log_event(
            action="user.logout",
            resource_type="user",
            user_id=user_id,
            resource_id=user_id,
            ip_address=ip_address
        )
    
    async def log_subscription_change(
        self,
        user_id: int,
        old_plan: str,
        new_plan: str,
        ip_address: str
    ):
        """Log subscription change"""
        await self.log_event(
            action="subscription.change",
            resource_type="subscription",
            user_id=user_id,
            ip_address=ip_address,
            details={
                "old_plan": old_plan,
                "new_plan": new_plan
            }
        )
    
    async def log_api_key_create(
        self,
        user_id: int,
        key_name: str,
        ip_address: str
    ):
        """Log API key creation"""
        await self.log_event(
            action="api_key.create",
            resource_type="api_key",
            user_id=user_id,
            ip_address=ip_address,
            details={"key_name": key_name}
        )
    
    async def log_api_key_delete(
        self,
        user_id: int,
        key_id: int,
        ip_address: str
    ):
        """Log API key deletion"""
        await self.log_event(
            action="api_key.delete",
            resource_type="api_key",
            user_id=user_id,
            resource_id=key_id,
            ip_address=ip_address
        )
    
    async def log_data_export(
        self,
        user_id: int,
        export_type: str,
        ip_address: str
    ):
        """Log data export"""
        await self.log_event(
            action="data.export",
            resource_type="export",
            user_id=user_id,
            ip_address=ip_address,
            details={"export_type": export_type}
        )
    
    async def get_user_audit_logs(
        self,
        user_id: int,
        limit: int = 100
    ) -> list[AuditLog]:
        """Get audit logs for a user"""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    async def get_recent_failed_logins(
        self,
        ip_address: str,
        hours: int = 24
    ) -> int:
        """Get count of recent failed login attempts from IP"""
        from sqlalchemy import select, func
        from datetime import timedelta
        
        threshold = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(func.count(AuditLog.id))
            .where(AuditLog.action == "user.login")
            .where(AuditLog.ip_address == ip_address)
            .where(AuditLog.status == "failure")
            .where(AuditLog.timestamp >= threshold)
        )
        
        return result.scalar() or 0
