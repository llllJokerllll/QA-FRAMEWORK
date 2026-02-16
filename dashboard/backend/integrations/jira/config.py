"""
Jira Configuration Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class JiraConfig(BaseModel):
    """Configuration for Jira integration"""
    
    base_url: str = Field(
        ...,
        description="Jira instance URL",
        examples=["https://yourcompany.atlassian.net"]
    )
    email: str = Field(
        ...,
        description="Jira account email"
    )
    api_token: str = Field(
        ...,
        description="Jira API token (generate at Atlassian Account Settings)"
    )
    default_project: Optional[str] = Field(
        None,
        description="Default project key for new issues"
    )
    default_issue_type: str = Field(
        "Bug",
        description="Default issue type for bugs"
    )
    default_test_issue_type: str = Field(
        "Task",
        description="Default issue type for test cases"
    )
    auto_create_bugs: bool = Field(
        True,
        description="Automatically create bugs for failed tests"
    )
    label_prefix: str = Field(
        "qa-framework",
        description="Prefix for labels added to issues"
    )
    
    @field_validator('base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is valid and uses HTTPS"""
        if not v.startswith('https://'):
            raise ValueError('base_url must use HTTPS')
        return v.rstrip('/')
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation"""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "base_url": "https://yourcompany.atlassian.net",
                "email": "qa@yourcompany.com",
                "api_token": "ATATT3xFfGF0T3...",
                "default_project": "QA",
                "default_issue_type": "Bug",
                "auto_create_bugs": True
            }
        }
