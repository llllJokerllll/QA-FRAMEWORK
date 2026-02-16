"""
Zephyr Configuration Schema
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ZephyrConfig(BaseModel):
    """Configuration for Zephyr Squad integration"""
    
    # Inherit Jira connection settings (Zephyr runs inside Jira)
    jira_base_url: str = Field(
        ...,
        description="Jira instance URL (Zephyr uses same auth)"
    )
    jira_email: str = Field(
        ...,
        description="Jira account email"
    )
    jira_api_token: str = Field(
        ...,
        description="Jira API token"
    )
    default_project: Optional[str] = Field(
        None,
        description="Default project key"
    )
    auto_create_cycles: bool = Field(
        True,
        description="Automatically create test cycles for runs"
    )
    cycle_naming: str = Field(
        "CI Run {date}",
        description="Template for cycle names. Variables: {date}, {branch}, {commit}"
    )
    
    @field_validator('jira_base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith('https://'):
            raise ValueError('jira_base_url must use HTTPS')
        return v.rstrip('/')
    
    class Config:
        json_schema_extra = {
            "example": {
                "jira_base_url": "https://yourcompany.atlassian.net",
                "jira_email": "qa@yourcompany.com",
                "jira_api_token": "ATATT3xFfGF0T3...",
                "default_project": "QA",
                "auto_create_cycles": True,
                "cycle_naming": "CI Run {date}"
            }
        }
