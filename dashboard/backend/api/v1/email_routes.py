"""
Email Routes

API endpoints for email management
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from services.auth_service import get_current_user
from services.email_service import (
    send_beta_invitation,
    send_welcome_email,
    send_test_report,
    send_password_reset
)
from models import User
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/email", tags=["Email"])


# Request/Response Models
class BetaInvitationRequest(BaseModel):
    email: EmailStr
    name: str
    referral_code: str
    accept_url: Optional[str] = None


class WelcomeEmailRequest(BaseModel):
    email: EmailStr
    name: str


class TestReportRequest(BaseModel):
    email: EmailStr
    project_name: str
    execution_date: str
    total_tests: int
    passed: int
    failed: int
    duration: str
    report_url: str
    failed_tests: Optional[List[Dict[str, Any]]] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr
    name: str
    reset_token: str
    expires_in: Optional[int] = 24


class BulkEmailRequest(BaseModel):
    emails: List[EmailStr]
    subject: str
    template: str
    template_data: Dict[str, Any]


# Endpoints
@router.post("/beta-invitation")
async def send_beta_invitation_endpoint(
    request: BetaInvitationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Send beta tester invitation email
    
    Request body:
        - email: Recipient email
        - name: Recipient name
        - referral_code: Unique referral code
        - accept_url: Optional custom acceptance URL
    
    Returns:
        - success: True if email sent
        - message: Status message
    """
    try:
        logger.info(f"Beta invitation email requested by user {current_user.id} to {request.email}")
        
        # Send email in background
        background_tasks.add_task(
            send_beta_invitation,
            request.email,
            request.name,
            request.referral_code,
            request.accept_url
        )
        
        return {
            "success": True,
            "message": f"Beta invitation email queued for {request.email}"
        }
        
    except Exception as e:
        logger.error(f"Error sending beta invitation email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome")
async def send_welcome_email_endpoint(
    request: WelcomeEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Send welcome email to new user
    
    Request body:
        - email: Recipient email
        - name: Recipient name
    
    Returns:
        - success: True if email sent
        - message: Status message
    """
    try:
        logger.info(f"Welcome email requested by user {current_user.id} to {request.email}")
        
        # Send email in background
        background_tasks.add_task(
            send_welcome_email,
            request.email,
            request.name
        )
        
        return {
            "success": True,
            "message": f"Welcome email queued for {request.email}"
        }
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-report")
async def send_test_report_endpoint(
    request: TestReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Send test execution report email
    
    Request body:
        - email: Recipient email
        - project_name: Project name
        - execution_date: Execution date (ISO format)
        - total_tests: Total number of tests
        - passed: Number of passed tests
        - failed: Number of failed tests
        - duration: Execution duration (e.g., "2m 30s")
        - report_url: URL to full report
        - failed_tests: Optional list of failed test details
    
    Returns:
        - success: True if email sent
        - message: Status message
    """
    try:
        logger.info(f"Test report email requested by user {current_user.id} to {request.email}")
        
        # Send email in background
        background_tasks.add_task(
            send_test_report,
            request.email,
            request.project_name,
            request.execution_date,
            request.total_tests,
            request.passed,
            request.failed,
            request.duration,
            request.report_url,
            request.failed_tests
        )
        
        return {
            "success": True,
            "message": f"Test report email queued for {request.email}"
        }
        
    except Exception as e:
        logger.error(f"Error sending test report email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/password-reset")
async def send_password_reset_endpoint(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Send password reset email (public endpoint)
    
    Request body:
        - email: Recipient email
        - name: Recipient name
        - reset_token: Password reset token
        - expires_in: Token expiration in hours (default: 24)
    
    Returns:
        - success: True if email sent
        - message: Status message
    """
    try:
        logger.info(f"Password reset email requested for {request.email}")
        
        # Send email in background
        background_tasks.add_task(
            send_password_reset,
            request.email,
            request.name,
            request.reset_token,
            request.expires_in
        )
        
        return {
            "success": True,
            "message": f"Password reset email queued for {request.email}"
        }
        
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk")
async def send_bulk_emails_endpoint(
    request: BulkEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Send bulk emails (admin only)
    
    Request body:
        - emails: List of recipient emails
        - subject: Email subject
        - template: Template name (beta_invitation, welcome, test_report)
        - template_data: Data to fill in template
    
    Returns:
        - success: True if emails queued
        - queued_count: Number of emails queued
        - message: Status message
    """
    try:
        # Only admins can send bulk emails
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        logger.info(f"Bulk email requested by admin {current_user.id} to {len(request.emails)} recipients")
        
        # Validate template
        valid_templates = ['beta_invitation', 'welcome', 'test_report']
        if request.template not in valid_templates:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid template. Must be one of: {valid_templates}"
            )
        
        # Queue emails in background
        queued_count = 0
        
        for email in request.emails:
            try:
                if request.template == 'beta_invitation':
                    background_tasks.add_task(
                        send_beta_invitation,
                        email,
                        request.template_data.get('name', 'User'),
                        request.template_data.get('referral_code', ''),
                        request.template_data.get('accept_url')
                    )
                elif request.template == 'welcome':
                    background_tasks.add_task(
                        send_welcome_email,
                        email,
                        request.template_data.get('name', 'User')
                    )
                elif request.template == 'test_report':
                    background_tasks.add_task(
                        send_test_report,
                        email,
                        request.template_data.get('project_name', 'Project'),
                        request.template_data.get('execution_date', datetime.utcnow().isoformat()),
                        request.template_data.get('total_tests', 0),
                        request.template_data.get('passed', 0),
                        request.template_data.get('failed', 0),
                        request.template_data.get('duration', '0s'),
                        request.template_data.get('report_url', ''),
                        request.template_data.get('failed_tests')
                    )
                
                queued_count += 1
                
            except Exception as e:
                logger.error(f"Error queuing email for {email}: {e}")
        
        return {
            "success": True,
            "queued_count": queued_count,
            "total_recipients": len(request.emails),
            "message": f"Bulk emails queued: {queued_count}/{len(request.emails)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending bulk emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_email_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List available email templates
    
    Returns:
        - templates: List of available template names and descriptions
    """
    templates = [
        {
            "name": "beta_invitation",
            "description": "Beta tester invitation email",
            "required_fields": ["name", "referral_code"],
            "optional_fields": ["accept_url"]
        },
        {
            "name": "welcome",
            "description": "Welcome email for new users",
            "required_fields": ["name"],
            "optional_fields": []
        },
        {
            "name": "test_report",
            "description": "Test execution report",
            "required_fields": ["project_name", "execution_date", "total_tests", "passed", "failed", "duration", "report_url"],
            "optional_fields": ["failed_tests"]
        },
        {
            "name": "password_reset",
            "description": "Password reset email",
            "required_fields": ["name", "reset_token"],
            "optional_fields": ["expires_in"]
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    }


@router.post("/preview/{template_name}")
async def preview_email_template(
    template_name: str,
    template_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Preview email template with sample data
    
    Path params:
        - template_name: Name of template to preview
    
    Request body:
        - Template data to fill in
    
    Returns:
        - html: Rendered HTML preview
    """
    try:
        from services.email_service import EmailTemplate
        
        if template_name == 'beta_invitation':
            html = EmailTemplate.BETA_INVITATION.format(
                name=template_data.get('name', 'John Doe'),
                email=template_data.get('email', 'john@example.com'),
                accept_url=template_data.get('accept_url', 'https://example.com/accept'),
                referral_code=template_data.get('referral_code', 'BETA123'),
                discord_url='https://discord.gg/example',
                unsubscribe_url='https://example.com/unsubscribe',
                privacy_url='https://example.com/privacy',
                year=datetime.now().year
            )
        elif template_name == 'welcome':
            html = EmailTemplate.WELCOME.format(
                name=template_data.get('name', 'John Doe'),
                dashboard_url='https://dashboard.example.com',
                docs_url='https://docs.example.com',
                discord_url='https://discord.gg/example',
                year=datetime.now().year
            )
        elif template_name == 'password_reset':
            html = EmailTemplate.PASSWORD_RESET.format(
                name=template_data.get('name', 'John Doe'),
                reset_url='https://example.com/reset?token=xxx',
                expires_in=template_data.get('expires_in', 24),
                year=datetime.now().year
            )
        else:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")
        
        return {
            "success": True,
            "template_name": template_name,
            "html": html
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing email template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
